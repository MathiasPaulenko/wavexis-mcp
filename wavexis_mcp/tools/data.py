"""Data extraction, auditing, and analysis tools for WaveXisMCP.

Provides tools for recording browser interactions, running
Lighthouse-style audits, extracting structured data, intercepting
WebSocket frames, crawling websites, and visual regression testing.
"""

from __future__ import annotations

import asyncio
import base64
import contextlib
import inspect
import json
import logging
import time
from collections import deque
from typing import Any
from urllib.parse import urlparse

import regex as _regex
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


def _score_ms(value_ms: float, good: float, poor: float) -> int:
    """Map a millisecond metric to a 0-100 score using Lighthouse thresholds."""
    if value_ms <= good:
        return 100
    if value_ms >= poor:
        return 0
    return int(round(100 - (value_ms - good) / (poor - good) * 100))


_PERF_EVAL_JS = """(function(){
var nav = performance.getEntriesByType('navigation')[0] || {};
var paints = performance.getEntriesByType('paint');
var fcp = 0;
for (var i=0;i<paints.length;i++){
  if(paints[i].name==='first-contentful-paint') { fcp=paints[i].startTime; }
}
var lcp = 0;
try {
  var lcpEntries = performance.getEntriesByType('largest-contentful-paint');
  if(lcpEntries.length) lcp = lcpEntries[lcpEntries.length-1].startTime;
} catch(e) {}
var cls = 0;
try {
  var shifts = performance.getEntriesByType('layout-shift');
  for(var i=0;i<shifts.length;i++){ if(!shifts[i].hadRecentInput) cls += shifts[i].value; }
} catch(e) {}
return {
  ttfb: nav.responseStart||0,
  fcp: fcp,
  lcp: lcp,
  cls: cls,
  dom_content_loaded: nav.domContentLoadedEventEnd||0,
  load: nav.loadEventEnd||0,
  dom_nodes: document.getElementsByTagName('*').length
};
})()"""

_A11Y_EVAL_JS = """(function(){
var imgs = document.querySelectorAll('img');
var missingAlt = 0;
for (var i=0;i<imgs.length;i++){ if(!imgs[i].getAttribute('alt')) missingAlt++; }
var controls = document.querySelectorAll('input,select,textarea');
var unlabeled = 0;
for (var i=0;i<controls.length;i++){
  var c = controls[i];
  var hasLabel = c.id && document.querySelector('label[for="'+c.id+'"]')
    || c.getAttribute('aria-label') || c.getAttribute('aria-labelledby')
    || c.getAttribute('title') || (c.closest && c.closest('label'))
    || c.type === 'hidden' || c.type === 'submit' || c.type === 'button';
  if(!hasLabel) unlabeled++;
}
return {
  has_lang: !!document.documentElement.lang,
  total_imgs: imgs.length,
  imgs_missing_alt: missingAlt,
  total_controls: controls.length,
  unlabeled_controls: unlabeled
};
})()"""

_SEO_EVAL_JS = """(function(){
var desc = document.querySelector('meta[name="description"]');
var canonical = document.querySelector('link[rel="canonical"]');
var viewport = document.querySelector('meta[name="viewport"]');
return {
  title_length: (document.title||'').length,
  meta_description_length: desc ? (desc.getAttribute('content')||'').length : 0,
  h1_count: document.querySelectorAll('h1').length,
  has_canonical: !!canonical,
  has_viewport: !!viewport
};
})()"""

_BEST_PRACTICES_EVAL_JS = """(function(){
var mixedContent = 0;
if (location.protocol === 'https:') {
  mixedContent = document.querySelectorAll(
    'img[src^="http:"],script[src^="http:"],link[href^="http:"],iframe[src^="http:"]'
  ).length;
}
return {
  is_https: location.protocol === 'https:',
  has_doctype: !!document.doctype,
  mixed_content_resources: mixedContent,
  has_console_api_errors: false
};
})()"""


def _audit_performance(metrics: dict[str, Any]) -> dict[str, Any]:
    """Compute a performance category from real CDP/raw metrics.

    The returned score interpolates FCP/TTFB/load values against
    Lighthouse thresholds instead of returning a fixed number.
    """
    ttfb = float(metrics.get("TTFB") or metrics.get("ttfb") or 0)
    fcp = float(metrics.get("FCP") or metrics.get("fcp") or 0)
    load = float(metrics.get("loadTime") or metrics.get("load") or 0)
    scores = [
        _score_ms(ttfb, 800, 1800),
        _score_ms(fcp, 1800, 3000) if fcp else None,
        _score_ms(load, 2500, 6000) if load else None,
    ]
    valid = [s for s in scores if s is not None]
    score = int(round(sum(valid) / len(valid))) if valid else 0
    return {
        "score": score,
        "ttfb_ms": ttfb,
        "fcp_ms": fcp,
        "load_ms": load,
        "dom_size": int(metrics.get("dom_nodes") or metrics.get("domNodes") or 0),
        "raw_metrics": metrics,
    }


async def _audit_accessibility(backend: AbstractBackend) -> dict[str, Any]:
    """Run real DOM checks for the accessibility category."""
    result = await backend.eval(_A11Y_EVAL_JS)
    result = result if isinstance(result, dict) else {}

    issues: list[dict[str, Any]] = []
    if not result.get("has_lang"):
        issues.append({"id": "html-has-lang", "impact": "serious"})
    for _ in range(int(result.get("imgs_missing_alt") or 0)):
        issues.append({"id": "image-alt", "impact": "critical"})
    for _ in range(int(result.get("unlabeled_controls") or 0)):
        issues.append({"id": "label", "impact": "critical"})

    penalty = min(100, len(issues) * 15)
    return {
        "score": 100 - penalty,
        "issues": issues,
        "issue_count": len(issues),
        "has_lang": bool(result.get("has_lang")),
        "total_imgs": int(result.get("total_imgs") or 0),
        "imgs_missing_alt": int(result.get("imgs_missing_alt") or 0),
        "unlabeled_controls": int(result.get("unlabeled_controls") or 0),
    }


async def _audit_seo(backend: AbstractBackend, title: str) -> dict[str, Any]:
    """Run real DOM checks for the SEO category."""
    result = await backend.eval(_SEO_EVAL_JS)
    result = result if isinstance(result, dict) else {}

    issues: list[str] = []
    if not title:
        issues.append("missing title")
    elif not (10 <= len(title) <= 60):
        issues.append("title length outside 10-60 chars")
    if not result.get("meta_description_length"):
        issues.append("missing meta description")
    if not result.get("h1_count"):
        issues.append("missing h1")
    if not result.get("has_viewport"):
        issues.append("missing viewport meta")

    score = max(0, 100 - len(issues) * 20)
    return {
        "score": score,
        "title": title,
        "title_length": len(title),
        "h1_count": int(result.get("h1_count") or 0),
        "meta_description_length": int(result.get("meta_description_length") or 0),
        "has_canonical": bool(result.get("has_canonical")),
        "issues": issues,
    }


async def _audit_best_practices(backend: AbstractBackend, url: str) -> dict[str, Any]:
    """Run real checks for the best-practices category."""
    result = await backend.eval(_BEST_PRACTICES_EVAL_JS)
    result = result if isinstance(result, dict) else {}

    console_errors: list[dict[str, Any]] = []
    try:
        console_errors = [
            e for e in (await backend.capture_console(level="error")) if isinstance(e, dict)
        ]
    except Exception:
        console_errors = []

    issues: list[str] = []
    if not result.get("is_https") and url.startswith("http:"):
        issues.append("page not served over HTTPS")
    if not result.get("has_doctype"):
        issues.append("missing doctype")
    if result.get("mixed_content_resources"):
        issues.append(f"{result['mixed_content_resources']} mixed-content resources")
    if console_errors:
        issues.append(f"{len(console_errors)} console errors")

    score = max(0, 100 - len(issues) * 20)
    return {
        "score": score,
        "issues": issues,
        "is_https": bool(result.get("is_https")),
        "mixed_content_resources": int(result.get("mixed_content_resources") or 0),
        "console_errors": console_errors,
    }


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

        Delegates to ``wavexis.actions.record.record_events`` to inject a
        recording script that captures user interactions (clicks, input,
        navigation, scroll, keypress) and then converts the captured events
        to a multi-action YAML workflow using
        ``wavexis.actions.record.events_to_yaml``.

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
                validate_url(input.url)

                # Delegate event capture to wavexis.
                from wavexis.actions.record import events_to_yaml, record_events

                events = await asyncio.wait_for(
                    record_events(backend, input.url, duration=input.duration),
                    timeout=input.duration + 30,
                )

                title = await backend.eval("document.title")
                title = str(title) if title else "recorded"

                # Convert events to YAML using wavexis.
                yaml_text = events_to_yaml(events, input.url)

                # Count actions in the YAML for the response.
                import yaml as _yaml_mod

                parsed = _yaml_mod.safe_load(yaml_text) or {}
                actions = parsed.get("actions", []) if isinstance(parsed, dict) else []

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

                perf = await backend.eval(_PERF_EVAL_JS)
                title = await backend.eval("document.title")
                title = str(title) if title else ""

                cats: dict[str, Any] = {}
                all_cats = not input.categories

                if all_cats or "performance" in input.categories:
                    cats["performance"] = _audit_performance(perf if isinstance(perf, dict) else {})
                if all_cats or "accessibility" in input.categories:
                    cats["accessibility"] = await _audit_accessibility(backend)
                if all_cats or "seo" in input.categories:
                    cats["seo"] = await _audit_seo(backend, title)
                if all_cats or "best-practices" in input.categories:
                    cats["best-practices"] = await _audit_best_practices(backend, input.url)

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
            if input.mock_responses:
                return format_error(
                    "wavexis_websocket_intercept",
                    ValueError(
                        "mock_responses is not supported: WebSocket frames cannot "
                        "be mocked via CDP/BiDi. Capture-only tool."
                    ),
                )
            backend, sid = await session_manager.acquire_backend(
                input.session_id,
                backend=input.backend,
                headless=input.headless,
            )
            try:
                from wavexis.config import WaitStrategy

                real = getattr(backend, "_backend", backend)
                require_session = getattr(real, "_require_session", None)
                if require_session is None:
                    return format_error(
                        "wavexis_websocket_intercept",
                        RuntimeError(
                            "WebSocket frame capture requires a CDP backend (backend='cdp')."
                        ),
                    )
                cdp_session = require_session()
                if inspect.isawaitable(cdp_session):
                    cdp_session = await cdp_session

                ws_urls: dict[str, str] = {}
                sent: list[dict[str, Any]] = []
                received: list[dict[str, Any]] = []
                errors: list[str] = []

                def _matches(url: str) -> bool:
                    return _url_matches(url, input.url_pattern or "")

                def on_created(params: Any) -> None:
                    if isinstance(params, dict):
                        rid = params.get("requestId", "")
                        url = params.get("url", "")
                        if rid:
                            ws_urls[rid] = url

                def on_frame(params: Any, direction: str) -> None:
                    if not isinstance(params, dict):
                        return
                    rid = params.get("requestId", "")
                    url = ws_urls.get(rid, "")
                    if not _matches(url):
                        return
                    response = params.get("response", {})
                    payload = response.get("payloadData", "")
                    entry = {
                        "url": url,
                        "request_id": rid,
                        "payload": payload,
                        "opcode": response.get("opcode"),
                    }
                    if direction == "sent":
                        sent.append(entry)
                    else:
                        received.append(entry)

                on_sent = lambda p: on_frame(p, "sent")  # noqa: E731
                on_received = lambda p: on_frame(p, "received")  # noqa: E731
                on_error = lambda p: (  # noqa: E731
                    errors.append(str(p.get("errorMessage", "frame error")))
                    if isinstance(p, dict)
                    else None
                )

                handlers = [
                    ("Network.webSocketCreated", on_created),
                    ("Network.webSocketFrameSent", on_sent),
                    ("Network.webSocketFrameReceived", on_received),
                    ("Network.webSocketFrameError", on_error),
                ]
                for event, handler in handlers:
                    res = cdp_session.on(event, handler)
                    if inspect.isawaitable(res):
                        await res

                try:
                    # Network.enable + handlers antes de navegar: si no,
                    # webSocketCreated se pierde y los frames quedan sin URL.
                    await backend.raw("Network.enable", {})
                    wait = WaitStrategy(strategy="load", timeout=input.wait_timeout)
                    validate_url(input.url)
                    await backend.navigate(input.url, wait)
                    await asyncio.sleep(input.duration_ms / 1000)
                finally:
                    for event, handler in handlers:
                        with contextlib.suppress(Exception):
                            res = cdp_session.off(event, handler)
                            if inspect.isawaitable(res):
                                await res

                return format_json_response(
                    {
                        "url": input.url,
                        "sent": sent,
                        "received": received,
                        "errors": errors,
                        "frames_sent": len(sent),
                        "frames_received": len(received),
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
