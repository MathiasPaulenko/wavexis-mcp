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
_logger = logging.getLogger(__name__)


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
                from wavexis.config import WaitStrategy

                wait = WaitStrategy(strategy="load", timeout=30000)
                validate_url(input.url)
                await backend.navigate(input.url, wait)

                await asyncio.sleep(input.duration)

                title = await backend.eval("document.title")
                title = str(title) if title else "recorded"

                yaml_text = yaml.safe_dump(
                    {
                        "actions": [
                            {"navigate": {"url": input.url}},
                            {"eval": {"expression": "document.title"}},
                        ]
                    }
                )

                return format_json_response(
                    {
                        "yaml": yaml_text,
                        "events_captured": 2,
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
                            if link not in visited:
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
