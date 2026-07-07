"""Capture tools for WaveXisMCP.

Provides screenshot, PDF, scrape, and screencast tools.  Binary
outputs can be returned as base64 or saved to disk via
``output_path`` / ``output_dir``.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from wavexis.config import PDFParams, ScreencastParams, ScreenshotParams

from wavexis_mcp.formatter import (
    encode_base64,
    format_error,
    format_json_response,
    save_to_file,
)
from wavexis_mcp.models import (
    AnnotatedScreenshotInput,
    PDFInput,
    ScrapeInput,
    ScreencastInput,
    ScreenshotInput,
)
from wavexis_mcp.session import SessionManager


def _write_frame(path: str, data: bytes) -> None:
    """Write frame bytes to disk (used via ``asyncio.to_thread``).

    Args:
        path: Destination file path.
        data: Raw frame bytes.
    """
    with open(path, "wb") as f:
        f.write(data)


def register(mcp: FastMCP, session_manager: SessionManager) -> None:
    """Register all capture tools on the FastMCP server.

    Args:
        mcp: The FastMCP server instance.
        session_manager: The shared session manager.
    """

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=True,
        )
    )
    async def wavexis_screenshot(input: ScreenshotInput) -> str:
        """Take a screenshot of a web page or element.

        Args:
            input: Screenshot parameters (URL, selector, format, etc.).

        Returns:
            JSON string with base64 image data or file path.
        """
        try:
            backend, sid = await session_manager.acquire_backend(
                input.session_id,
                backend=input.backend,
                headless=input.headless,
                width=input.width,
                height=input.height,
            )
            try:
                if input.url:
                    wait = session_manager.make_wait(
                        strategy=input.wait_strategy,
                        selector=input.wait_selector,
                        timeout=input.wait_timeout,
                    )
                    await session_manager.call_backend(backend.navigate(input.url, wait))

                if input.js:
                    await session_manager.call_backend(backend.eval(input.js, await_promise=True))

                if input.selector:
                    data = await session_manager.call_backend(
                        backend.screenshot_selector(
                            input.selector, input.format, input.quality
                        )
                    )
                else:
                    params = ScreenshotParams(
                        url=input.url or "",
                        full_page=input.full_page,
                        format=input.format,
                        quality=input.quality,
                        js=input.js,
                        selector=input.selector,
                        device=input.device,
                    )
                    data = await session_manager.call_backend(backend.screenshot(params))

                if input.output_path:
                    result = save_to_file(data, input.output_path)
                    result["status"] = "ok"
                    return format_json_response(result)

                return format_json_response(
                    {
                        "status": "ok",
                        "format": input.format,
                        "base64": encode_base64(data),
                        "size_bytes": len(data),
                    }
                )
            finally:
                await session_manager.release_backend(backend, sid)
        except Exception as e:
            return format_error("wavexis_screenshot", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=True,
        )
    )
    async def wavexis_pdf(input: PDFInput) -> str:
        """Generate a PDF of a web page.

        Args:
            input: PDF parameters (URL, paper size, margins, etc.).

        Returns:
            JSON string with base64 PDF data or file path.
        """
        try:
            backend, sid = await session_manager.acquire_backend(
                input.session_id,
                backend=input.backend,
                headless=input.headless,
            )
            try:
                if input.url:
                    wait = session_manager.make_wait(timeout=input.wait_timeout)
                    await backend.navigate(input.url, wait)

                if input.js:
                    await backend.eval(input.js, await_promise=True)

                params = PDFParams(
                    url=input.url or "",
                    paper=input.paper,
                    landscape=input.landscape,
                    margin=input.margin,
                    no_header_footer=input.no_header_footer,
                    media=input.media,
                    js=input.js,
                )
                data = await backend.pdf(params)

                if input.output_path:
                    result = save_to_file(data, input.output_path)
                    result["status"] = "ok"
                    return format_json_response(result)

                return format_json_response(
                    {
                        "status": "ok",
                        "base64": encode_base64(data),
                        "size_bytes": len(data),
                    }
                )
            finally:
                await session_manager.release_backend(backend, sid)
        except Exception as e:
            return format_error("wavexis_pdf", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=True,
        )
    )
    async def wavexis_scrape(input: ScrapeInput) -> str:
        """Scrape multiple URLs by evaluating a JS expression on each page.

        Args:
            input: Scrape parameters (URLs, expression, pagination).

        Returns:
            JSON string with paginated results and total count.
        """
        try:
            results: list[dict[str, object]] = []
            for url in input.urls:
                backend, sid = await session_manager.acquire_backend(
                    input.session_id,
                    backend=input.backend,
                    headless=input.headless,
                )
                try:
                    wait = session_manager.make_wait(
                        strategy="selector" if input.selector else "load",
                        selector=input.selector,
                        timeout=input.wait_timeout,
                    )
                    await backend.navigate(url, wait)
                    data = await backend.eval(input.expression, await_promise=True)
                    results.append({"url": url, "data": data})
                finally:
                    await session_manager.release_backend(backend, sid)

            paginated = results[input.offset : input.offset + input.limit]
            return format_json_response(
                {
                    "results": paginated,
                    "format": input.output_format,
                    "count": len(paginated),
                    "total": len(results),
                }
            )
        except Exception as e:
            return format_error("wavexis_scrape", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=True,
        )
    )
    async def wavexis_screencast(input: ScreencastInput) -> str:
        """Capture a sequence of screenshots (frame-by-frame).

        Args:
            input: Screencast parameters (duration, format, output dir).

        Returns:
            JSON string with base64 frames or directory path.
        """
        try:
            backend, sid = await session_manager.acquire_backend(
                input.session_id,
                backend=input.backend,
                headless=input.headless,
            )
            try:
                if input.url:
                    wait = session_manager.make_wait(timeout=input.wait_timeout)
                    await backend.navigate(input.url, wait)

                params = ScreencastParams(
                    url=input.url or "",
                    format=input.format,
                    quality=input.quality,
                    max_width=input.max_width,
                    max_height=input.max_height,
                    duration=input.duration,
                )
                frames = await backend.screencast(params)

                if input.output_dir:
                    import asyncio
                    import os

                    os.makedirs(input.output_dir, exist_ok=True)
                    for i, frame in enumerate(frames):
                        frame_path = os.path.join(input.output_dir, f"frame_{i:04d}.{input.format}")
                        await asyncio.to_thread(_write_frame, frame_path, frame)
                    return format_json_response(
                        {
                            "dir": input.output_dir,
                            "count": len(frames),
                        }
                    )

                return format_json_response(
                    {
                        "frames": [encode_base64(f) for f in frames],
                        "count": len(frames),
                    }
                )
            finally:
                await session_manager.release_backend(backend, sid)
        except Exception as e:
            return format_error("wavexis_screencast", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=True,
        )
    )
    async def wavexis_annotated_screenshot(input: AnnotatedScreenshotInput) -> str:
        """Take a screenshot with numbered labels overlaid on elements.

        Injects overlay divs with labels @e1, @e2, ... on each element
        matching the provided selectors, captures a screenshot, removes
        the overlays, and returns the image plus a label-to-selector map.

        Args:
            input: Annotated screenshot parameters (selectors, format).

        Returns:
            JSON string with base64 image data or file path, plus ``labels`` map.
        """
        try:
            session = session_manager.get(input.session_id)
            data, label_map = await session.backend.annotated_screenshot(
                input.selectors, format=input.format
            )

            if input.output_path:
                result = save_to_file(data, input.output_path)
                result["status"] = "ok"
                result["labels"] = label_map
                return format_json_response(result)

            return format_json_response(
                {
                    "status": "ok",
                    "format": input.format,
                    "base64": encode_base64(data),
                    "size_bytes": len(data),
                    "labels": label_map,
                }
            )
        except Exception as e:
            return format_error("wavexis_annotated_screenshot", e)
