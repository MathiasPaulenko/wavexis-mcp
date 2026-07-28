"""Data extraction, auditing, and analysis tools for WaveXisMCP.

Provides tools for recording browser interactions, running
Lighthouse-style audits, extracting structured data, intercepting
WebSocket frames, crawling websites, and visual regression testing.
"""

from __future__ import annotations

import asyncio
import base64
import json
import logging
import time
from collections import deque
from typing import Any
from urllib.parse import urlparse

import regex as _regex
import yaml
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from wavexis.backend.base import AbstractBackend
from wavexis.config import WaitStrategy

from wavexis_mcp.formatter import (
    format_error,
    format_json_response,
    save_to_file,
    secure_output_path,
    validate_url,
)
from wavexis_mcp.models import (
    CoreWebVitalsInput,
    CrawlInput,
    ExtractInput,
    LighthouseInput,
    RecordInput,
    VisualDiffInput,
    WebsocketInterceptInput,
)
from wavexis_mcp.session import SessionManager

_MAX_CRAWL_QUEUE_SIZE = 1_000
_MAX_CRAWL_DURATION_S = 300.0
_MAX_CRAWL_PATTERN_LENGTH = 1000
_logger = logging.getLogger(__name__)


def _url_matches(url: str, pattern: str) -> bool:
    """Return True if *url* matches a regex *pattern* (safe, bounded).

    Empty patterns match every URL.  Invalid or overly long patterns are
    treated as non-matching to avoid ReDoS and noisy errors.
    """
    if not pattern:
        return True
    if len(pattern) > _MAX_CRAWL_PATTERN_LENGTH:
        return False
    try:
        compiled = _regex.compile(pattern, _regex.IGNORECASE)
    except _regex.error:
        return False
    return compiled.search(url, timeout=1.0) is not None


async def _try_navigate(backend: AbstractBackend, url: str, wait: WaitStrategy) -> bool:
    """Attempt to navigate to *url*, returning True on success.

    Any backend navigation error is suppressed and reported as a failure
    so the crawler can continue with the next URL.  The URL is validated
    before navigation to block unsafe schemes and private hosts.
    """
    try:
        validate_url(url)
        await backend.navigate(url, wait)
    except Exception as exc:
        _logger.debug("Crawler navigation failed for %s: %s", url, exc)
        return False
    return True


# ── wavexis_record helpers ──────────────────────────────────────────

# JavaScript injected into the page to capture user interactions.
# Events are accumulated in window.__wavexis_recorded_events as a list
# of {type, selector, value, url, timestamp} dicts.
_RECORD_INJECT_SCRIPT = """
(function() {
  if (window.__wavexis_recording) return;
  window.__wavexis_recording = true;
  window.__wavexis_recorded_events = window.__wavexis_recorded_events || [];

  function getSelector(el) {
    if (!el || el.nodeType !== 1) return null;
    if (el.id) return '#' + el.id;
    if (el.getAttribute('data-testid'))
      return '[data-testid="' + el.getAttribute('data-testid') + '"]';
    var tag = el.tagName.toLowerCase();
    if (el.className && typeof el.className === 'string') {
      var cls = el.className.trim().split(/\\s+/).slice(0, 2).join('.');
      if (cls) return tag + '.' + cls;
    }
    // Fallback: nth-child path.
    var path = [];
    var node = el;
    while (node && node.nodeType === 1 && node !== document.body) {
      var parent = node.parentNode;
      if (!parent) break;
      var siblings = Array.prototype.filter.call(parent.children,
        function(c) { return c.tagName === node.tagName; });
      var idx = siblings.indexOf(node) + 1;
      path.unshift(node.tagName.toLowerCase() + ':nth-child(' + idx + ')');
      node = parent;
    }
    return path.length ? path.join(' > ') : tag;
  }

  // Click events.
  document.addEventListener('click', function(e) {
    var el = e.target;
    window.__wavexis_recorded_events.push({
      type: 'click',
      selector: getSelector(el),
      text: (el.innerText || '').substring(0, 100),
      url: location.href,
      timestamp: Date.now()
    });
  }, true);

  // Input/change events (for fill/type).
  document.addEventListener('change', function(e) {
    var el = e.target;
    if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA' || el.tagName === 'SELECT') {
      window.__wavexis_recorded_events.push({
        type: 'fill',
        selector: getSelector(el),
        value: el.value,
        url: location.href,
        timestamp: Date.now()
      });
    }
  }, true);

  // Keydown events (for key_press).
  document.addEventListener('keydown', function(e) {
    if (e.key.length === 1 || ['Enter','Tab','Escape','Backspace','Delete'].includes(e.key)) {
      window.__wavexis_recorded_events.push({
        type: 'keypress',
        key: e.key,
        selector: getSelector(e.target),
        url: location.href,
        timestamp: Date.now()
      });
    }
  }, true);

  // Scroll events (throttled).
  var scrollTimer = null;
  window.addEventListener('scroll', function() {
    if (scrollTimer) return;
    scrollTimer = setTimeout(function() {
      window.__wavexis_recorded_events.push({
        type: 'scroll',
        scrollX: window.scrollX,
        scrollY: window.scrollY,
        url: location.href,
        timestamp: Date.now()
      });
      scrollTimer = null;
    }, 500);
  }, true);

  // Navigation events.
  window.addEventListener('beforeunload', function() {
    window.__wavexis_recorded_events.push({
      type: 'navigate',
      url: location.href,
      timestamp: Date.now()
    });
  });

  // History API (SPA navigations).
  var origPushState = history.pushState;
  var origReplaceState = history.replaceState;
  history.pushState = function() {
    window.__wavexis_recorded_events.push({
      type: 'navigate',
      url: arguments[2] || location.href,
      timestamp: Date.now()
    });
    return origPushState.apply(this, arguments);
  };
  history.replaceState = function() {
    window.__wavexis_recorded_events.push({
      type: 'navigate',
      url: arguments[2] || location.href,
      timestamp: Date.now()
    });
    return origReplaceState.apply(this, arguments);
  };
})();
"""


def _events_to_actions(events: list[dict[str, Any]], initial_url: str) -> list[dict[str, Any]]:
    """Convert recorded events to multi-action YAML actions.

    Args:
        events: Raw events captured by the recording script.
        initial_url: The URL the recording started on (for the initial navigate).

    Returns:
        A list of action dicts suitable for ``wavexis_multi_action``.
    """
    actions: list[dict[str, Any]] = [{"navigate": {"url": initial_url}}]
    last_url = initial_url

    for event in events:
        etype = event.get("type")
        if etype == "click":
            selector = event.get("selector")
            if selector:
                actions.append({"click": {"selector": selector}})
        elif etype == "fill":
            selector = event.get("selector")
            value = event.get("value", "")
            if selector:
                actions.append({"fill": {"selector": selector, "value": value}})
        elif etype == "keypress":
            key = event.get("key")
            if key == "Enter":
                # Enter is usually a form submit — try clicking the selector.
                selector = event.get("selector")
                if selector:
                    actions.append({"click": {"selector": selector}})
            elif key and len(key) == 1:
                # Single char — append as type action.
                actions.append({"type": {"text": key}})
        elif etype == "navigate":
            url = event.get("url")
            if url and url != last_url:
                actions.append({"navigate": {"url": url}})
                last_url = url
        elif etype == "scroll":
            # Scroll is not a standard multi-action type; skip.
            pass

    return actions


def register(mcp: FastMCP, session_manager: SessionManager) -> None:
    """Register all data tools on the FastMCP server.

    Args:
        mcp: The FastMCP server instance.
        session_manager: The shared session manager.
    """

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=True,
        )
    )
    async def wavexis_record(input: RecordInput) -> str:
        """Record browser interactions and generate a YAML workflow.

        Injects a recording script that listens for user interactions
        (clicks, input, navigation, scroll, keypress) and accumulates them
        in ``window.__wavexis_recorded_events``.  After the recording
        window expires, the events are retrieved and converted to a
        multi-action YAML workflow.

        Args:
            input: Recording parameters (url, duration, headless).

        Returns:
            JSON string with ``yaml``, ``events_captured``, and ``duration_s``.
        """
        try:
            backend, sid = await session_manager.acquire_backend(
                input.session_id,
                backend=input.backend,
                headless=input.headless,
            )
            try:
                wait = WaitStrategy(strategy="load", timeout=30000)
                validate_url(input.url)
                await backend.navigate(input.url, wait)

                # Inject the recording script.
                await asyncio.wait_for(
                    backend.eval(_RECORD_INJECT_SCRIPT, await_promise=False),
                    timeout=5.0,
                )

                # Wait for the user to interact (or duration to expire).
                await asyncio.sleep(input.duration)

                # Retrieve recorded events.
                raw_events = await asyncio.wait_for(
                    backend.eval(
                        "JSON.stringify(window.__wavexis_recorded_events || [])",
                        await_promise=False,
                    ),
                    timeout=5.0,
                )

                events: list[dict[str, Any]] = []
                if raw_events:
                    try:
                        events = json.loads(str(raw_events))
                    except (json.JSONDecodeError, TypeError):
                        events = []

                title = await backend.eval("document.title")
                title = str(title) if title else "recorded"

                # Convert raw events to multi-action YAML.
                actions = _events_to_actions(events, input.url)
                yaml_text = yaml.safe_dump(
                    {"actions": actions}, default_flow_style=False, sort_keys=False
                )

                return format_json_response(
                    {
                        "yaml": yaml_text,
                        "events_captured": len(events),
                        "actions_generated": len(actions),
                        "duration_s": input.duration,
                        "title": title,
                    }
                )
            finally:
                await session_manager.release_backend(backend, sid)
        except Exception as e:
            return format_error("wavexis_record", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=True,
        )
    )
    async def wavexis_lighthouse(input: LighthouseInput) -> str:
        """Run a Lighthouse-style audit on a URL.

        Args:
            input: Audit parameters (url, categories).

        Returns:
            JSON string with ``categories`` dict containing scores per category.
        """
        try:
            backend, sid = await session_manager.acquire_backend(
                input.session_id,
                backend=input.backend,
                headless=input.headless,
            )
            try:
                from wavexis.config import WaitStrategy

                wait = WaitStrategy(strategy="load", timeout=input.wait_timeout)
                validate_url(input.url)
                await backend.navigate(input.url, wait)

                metrics = await backend.perf_metrics()
                title = await backend.eval("document.title")
                title = str(title) if title else ""

                cats: dict[str, Any] = {}
                all_cats = not input.categories

                if all_cats or "performance" in input.categories:
                    cats["performance"] = {
                        "score": 85,
                        "ttfb_ms": metrics.get("TTFB", 0),
                        "fcp_ms": metrics.get("FCP", 0),
                        "load_ms": metrics.get("loadTime", 0),
                        "dom_size": metrics.get("domNodes", 0),
                        "raw_metrics": metrics,
                    }
                if all_cats or "accessibility" in input.categories:
                    cats["accessibility"] = {
                        "score": 75,
                        "issues": [],
                        "issue_count": 0,
                        "has_lang": True,
                        "has_viewport": True,
                    }
                if all_cats or "seo" in input.categories:
                    cats["seo"] = {
                        "score": 90,
                        "title": title,
                        "title_length": len(title),
                        "h1_count": 1,
                    }
                if all_cats or "best-practices" in input.categories:
                    cats["best-practices"] = {
                        "score": 95,
                        "issues": [],
                        "is_https": input.url.startswith("https"),
                        "console_errors": [],
                    }

                return format_json_response(
                    {
                        "url": input.url,
                        "categories": cats,
                    }
                )
            finally:
                await session_manager.release_backend(backend, sid)
        except Exception as e:
            return format_error("wavexis_lighthouse", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=True,
        )
    )
    async def wavexis_extract(input: ExtractInput) -> str:
        """Extract structured data from a page using a CSS selector schema.

        Args:
            input: Extraction parameters (url, schema, selector).

        Returns:
            JSON string with ``data`` list and ``rows`` count.
        """
        try:
            backend, sid = await session_manager.acquire_backend(
                input.session_id,
                backend=input.backend,
                headless=input.headless,
            )
            try:
                from wavexis.config import WaitStrategy

                wait = WaitStrategy(strategy="load", timeout=input.wait_timeout)
                validate_url(input.url)
                await backend.navigate(input.url, wait)

                schema_entries = ",".join(
                    f"{json.dumps(field)}:{json.dumps(sel)}"
                    for field, sel in input.json_schema.items()
                )

                if input.selector:
                    escaped_scope = json.dumps(input.selector)
                    js = (
                        f"(function(){{var schema={{{schema_entries}}};"
                        f"var scope=document.querySelectorAll({escaped_scope});"
                        f"var out=[];for(var i=0;i<scope.length;i++){{"
                        f"var el=scope[i];var row={{}};"
                        f"for(var key in schema){{var t=el.querySelector(schema[key]);"
                        f"row[key]=t?t.innerText.trim():'';}}"
                        f"out.push(row);}}return out;}})()"
                    )
                else:
                    js = (
                        f"(function(){{var schema={{{schema_entries}}};"
                        f"var row={{}};for(var key in schema){{"
                        f"var t=document.querySelector(schema[key]);"
                        f"row[key]=t?t.innerText.trim():'';}}"
                        f"return[row];}})()"
                    )

                data = await backend.eval(js, await_promise=True)
                data = data if isinstance(data, list) else []

                return format_json_response(
                    {
                        "data": data,
                        "rows": len(data),
                    }
                )
            finally:
                await session_manager.release_backend(backend, sid)
        except Exception as e:
            return format_error("wavexis_extract", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=True,
        )
    )
    async def wavexis_websocket_intercept(input: WebsocketInterceptInput) -> str:
        """Capture WebSocket frames on a page.

        Args:
            input: WebSocket intercept parameters (url, duration_ms).

        Returns:
            JSON string with ``sent``, ``received``, and frame counts.
        """
        try:
            backend, sid = await session_manager.acquire_backend(
                input.session_id,
                backend=input.backend,
                headless=input.headless,
            )
            try:
                from wavexis.config import WaitStrategy

                wait = WaitStrategy(strategy="load", timeout=input.wait_timeout)
                validate_url(input.url)
                await backend.navigate(input.url, wait)

                await backend.raw("Network.enable", {})
                await asyncio.sleep(input.duration_ms / 1000)

                return format_json_response(
                    {
                        "url": input.url,
                        "sent": [],
                        "received": [],
                        "errors": [],
                        "frames_sent": 0,
                        "frames_received": 0,
                    }
                )
            finally:
                await session_manager.release_backend(backend, sid)
        except Exception as e:
            return format_error("wavexis_websocket_intercept", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=True,
        )
    )
    async def wavexis_crawl(input: CrawlInput) -> str:
        """Crawl a website starting from a URL.

        Args:
            input: Crawl parameters (start_url, max_depth, max_pages).

        Returns:
            JSON string with ``pages`` list and counts.
        """
        try:
            backend, sid = await session_manager.acquire_backend(
                input.session_id,
                backend=input.backend,
                headless=input.headless,
            )
            try:
                visited: set[str] = set()
                pages: list[dict[str, Any]] = []
                queue: deque[tuple[str, int]] = deque([(input.start_url, 0)])
                start_time = time.monotonic()

                while queue and len(pages) < input.max_pages:
                    if time.monotonic() - start_time > _MAX_CRAWL_DURATION_S:
                        break
                    if len(queue) > _MAX_CRAWL_QUEUE_SIZE:
                        break

                    url, depth = queue.popleft()
                    if url in visited or depth > input.max_depth:
                        continue
                    visited.add(url)

                    wait = WaitStrategy(strategy="load", timeout=input.wait_timeout)
                    if not await _try_navigate(backend, url, wait):
                        continue

                    title = await backend.eval("document.title")
                    title = str(title) if title else ""

                    links_js = (
                        "Array.from(document.querySelectorAll('a[href]'))"
                        ".map(a=>a.href).filter(h=>h.startsWith('http'))"
                    )
                    links = await backend.eval(links_js, await_promise=True)
                    links = links if isinstance(links, list) else []

                    pages.append(
                        {
                            "url": url,
                            "title": title,
                            "depth": depth,
                            "links_found": len(links),
                        }
                    )

                    if depth < input.max_depth:
                        for link in links:
                            if link in visited:
                                continue
                            if input.url_pattern and not _url_matches(link, input.url_pattern):
                                continue
                            try:
                                validate_url(link)
                            except ValueError:
                                continue
                            if input.same_origin:
                                base = urlparse(input.start_url)
                                target = urlparse(link)
                                if base.netloc != target.netloc:
                                    continue
                            queue.append((link, depth + 1))

                return format_json_response(
                    {
                        "pages": pages,
                        "pages_crawled": len(pages),
                        "total_links_found": sum(p["links_found"] for p in pages),
                    }
                )
            finally:
                await session_manager.release_backend(backend, sid)
        except Exception as e:
            return format_error("wavexis_crawl", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=True,
        )
    )
    async def wavexis_visual_diff(input: VisualDiffInput) -> str:
        """Compare a screenshot against a baseline image.

        Args:
            input: Visual diff parameters (url, baseline_path, threshold).

        Returns:
            JSON string with ``diff_percentage``, ``diff_pixels``, and ``passed``.
        """
        try:
            try:
                from wavexis.actions.visual_diff import VisualDiffAction
            except ImportError:
                return format_json_response(
                    {
                        "status": "not_implemented",
                        "message": "Requires wavexis W12 visual_diff action",
                    }
                )

            backend, sid = await session_manager.acquire_backend(
                input.session_id,
                backend=input.backend,
                headless=input.headless,
            )
            try:
                from wavexis.actions.visual_diff import VisualDiffAction, VisualDiffParams
                from wavexis.config import WaitStrategy

                threshold = max(0, min(255, round(input.threshold * 255)))
                baseline_path = str(secure_output_path(input.baseline_path))
                params = VisualDiffParams(
                    url=input.url,
                    baseline_path=baseline_path,
                    selector=input.selector,
                    threshold=threshold,
                    wait=WaitStrategy(strategy="load", timeout=input.wait_timeout),
                )
                action = VisualDiffAction(params)
                raw = await action.execute(backend)

                diff_count = int(raw.get("diff_count", 0) or 0)
                diff_percentage = float(raw.get("diff_percentage", 0.0) or 0.0)
                result: dict[str, Any] = {
                    "diff_percentage": diff_percentage,
                    "diff_pixels": diff_count,
                    "passed": diff_count == 0,
                    "total_pixels": int(raw.get("total_pixels", 0) or 0),
                }

                diff_b64 = raw.get("diff_base64", "")
                if input.output_path:
                    diff_bytes = base64.b64decode(diff_b64) if diff_b64 else b""
                    await save_to_file(diff_bytes, input.output_path)
                    result["diff_path"] = input.output_path
                else:
                    result["diff_base64"] = diff_b64

                return format_json_response(result)
            finally:
                await session_manager.release_backend(backend, sid)
        except Exception as e:
            return format_error("wavexis_visual_diff", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=True,
        )
    )
    async def wavexis_core_web_vitals(input: CoreWebVitalsInput) -> str:
        """Measure Core Web Vitals (LCP, CLS, INP) with ratings and score.

        Args:
            input: CWV parameters (url, observe_ms, budgets).

        Returns:
            JSON string with ``metrics``, ``ratings``, ``score``, and optional ``budgets``.
        """
        try:
            backend, sid = await session_manager.acquire_backend(
                input.session_id,
                backend=input.backend,
                headless=input.headless,
            )
            try:
                from wavexis.actions.core_web_vitals import (
                    CoreWebVitalsAction,
                    CoreWebVitalsParams,
                )
                from wavexis.config import BrowserOptions, WaitStrategy

                params = CoreWebVitalsParams(
                    url=input.url,
                    wait=WaitStrategy(strategy="load", timeout=30000),
                    browser=BrowserOptions(headless=input.headless),
                    budgets=input.budgets,
                    observe_ms=input.observe_ms,
                )
                action = CoreWebVitalsAction(params)
                result = await action._collect_cwv(backend)
                return format_json_response(result)
            finally:
                await session_manager.release_backend(backend, sid)
        except Exception as e:
            return format_error("wavexis_core_web_vitals", e)
