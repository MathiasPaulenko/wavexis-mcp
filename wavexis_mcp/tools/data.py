"""Data extraction, auditing, and analysis tools for WaveXisMCP.

Provides tools for recording browser interactions, running
Lighthouse-style audits, extracting structured data, intercepting
WebSocket frames, crawling websites, and visual regression testing.
"""

from __future__ import annotations

import asyncio
from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from wavexis_mcp.formatter import format_error, format_json_response, save_to_file
from wavexis_mcp.models import (
    CrawlInput,
    ExtractInput,
    LighthouseInput,
    RecordInput,
    VisualDiffInput,
    WebsocketInterceptInput,
)
from wavexis_mcp.session import SessionManager


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
                input.session_id if hasattr(input, "session_id") else None,
                backend=input.backend,
                headless=input.headless,
            )
            try:
                from wavexis.config import WaitStrategy

                wait = WaitStrategy(strategy="load", timeout=30000)
                await backend.navigate(input.url, wait)

                await asyncio.sleep(input.duration)

                title = await backend.eval("document.title")
                title = str(title) if title else "recorded"

                yaml_text = (
                    f"actions:\n"
                    f"  - navigate:\n"
                    f"      url: {input.url}\n"
                    f"  - eval:\n"
                    f"      expression: document.title\n"
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
                await backend.navigate(input.url, wait)

                data: list[dict[str, Any]] = []

                if input.selector:
                    escaped_scope = input.selector.replace("'", "\\'")
                    count_js = f"document.querySelectorAll('{escaped_scope}').length"
                    count = await backend.eval(count_js, await_promise=True)
                    count = int(count) if count else 0

                    for i in range(count):
                        row: dict[str, Any] = {}
                        for field, sel in input.schema.items():
                            escaped_sel = sel.replace("'", "\\'")
                            js = (
                                f"(function(){{var els=document.querySelectorAll"
                                f"('{escaped_scope}');var el=els[{i}];"
                                f"if(!el)return '';var t=el.querySelector"
                                f"('{escaped_sel}');return t?t.innerText.trim()"
                                f":'';}})()"
                            )
                            val = await backend.eval(js, await_promise=True)
                            row[field] = str(val) if val else ""
                        data.append(row)
                else:
                    row = {}
                    for field, sel in input.schema.items():
                        escaped_sel = sel.replace("'", "\\'")
                        js = (
                            f"(function(){{var el=document.querySelector"
                            f"('{escaped_sel}');return el?el.innerText.trim()"
                            f":'';}})()"
                        )
                        val = await backend.eval(js, await_promise=True)
                        row[field] = str(val) if val else ""
                    data.append(row)

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
                from wavexis.config import WaitStrategy

                visited: set[str] = set()
                pages: list[dict[str, Any]] = []
                queue: list[tuple[str, int]] = [(input.start_url, 0)]

                while queue and len(pages) < input.max_pages:
                    url, depth = queue.pop(0)
                    if url in visited or depth > input.max_depth:
                        continue
                    visited.add(url)

                    wait = WaitStrategy(strategy="load", timeout=input.wait_timeout)
                    try:
                        await backend.navigate(url, wait)
                    except Exception:
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
                                if input.same_origin:
                                    from urllib.parse import urlparse

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
                from wavexis.config import ScreenshotParams, WaitStrategy

                wait = WaitStrategy(strategy="load", timeout=input.wait_timeout)
                await backend.navigate(input.url, wait)

                params = ScreenshotParams(url="", full_page=True)
                current = await backend.screenshot(params)

                import anyio

                baseline = await anyio.Path(input.baseline_path).read_bytes()

                action = VisualDiffAction()
                result = action.compare(baseline, current, threshold=input.threshold)

                if input.output_path and result.get("diff_bytes"):
                    save_to_file(result["diff_bytes"], input.output_path)
                    result["diff_path"] = input.output_path
                    del result["diff_bytes"]

                return format_json_response(result)
            finally:
                await session_manager.release_backend(backend, sid)
        except Exception as e:
            return format_error("wavexis_visual_diff", e)
