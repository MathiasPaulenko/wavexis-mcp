"""Navigation tools for WaveXisMCP.

Provides navigate, back, forward, reload, stop, and wait tools
for controlling browser navigation.
"""

from __future__ import annotations

import time

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from wavexis_mcp.formatter import format_error, format_json_response
from wavexis_mcp.models import NavigateInput, ReloadInput, SimpleNavInput, WaitInput
from wavexis_mcp.session import SessionManager


def register(mcp: FastMCP, session_manager: SessionManager) -> None:
    """Register all navigation tools on the FastMCP server.

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
    async def wavexis_navigate(input: NavigateInput) -> str:
        """Navigate to a URL in the browser.

        Args:
            input: Navigation parameters (URL, wait strategy).

        Returns:
            JSON string with status ``"ok"`` and ``url``.
        """
        try:
            backend, sid = await session_manager.acquire_backend(
                input.session_id,
                backend=input.backend,
                headless=input.headless,
            )
            try:
                wait = session_manager.make_wait(
                    strategy=input.wait_strategy,
                    selector=input.wait_selector,
                    url_pattern=input.wait_url_pattern,
                    timeout=input.wait_timeout,
                )
                await backend.navigate(input.url, wait)
                return format_json_response({"status": "ok", "url": input.url})
            finally:
                await session_manager.release_backend(backend, sid)
        except Exception as e:
            return format_error("wavexis_navigate", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        )
    )
    async def wavexis_back(input: SimpleNavInput) -> str:
        """Navigate back in browser history.

        Args:
            input: Session reference parameters.

        Returns:
            JSON string with status ``"ok"``.
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.go_back()
            return format_json_response({"status": "ok"})
        except Exception as e:
            return format_error("wavexis_back", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        )
    )
    async def wavexis_forward(input: SimpleNavInput) -> str:
        """Navigate forward in browser history.

        Args:
            input: Session reference parameters.

        Returns:
            JSON string with status ``"ok"``.
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.go_forward()
            return format_json_response({"status": "ok"})
        except Exception as e:
            return format_error("wavexis_forward", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        )
    )
    async def wavexis_reload(input: ReloadInput) -> str:
        """Reload the current page.

        Args:
            input: Reload parameters (ignore_cache).

        Returns:
            JSON string with status ``"ok"``.
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.reload(ignore_cache=input.ignore_cache)
            return format_json_response({"status": "ok"})
        except Exception as e:
            return format_error("wavexis_reload", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def wavexis_stop(input: SimpleNavInput) -> str:
        """Stop all pending navigations and resource loads.

        Args:
            input: Session reference parameters.

        Returns:
            JSON string with status ``"ok"``.
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.stop_loading()
            return format_json_response({"status": "ok"})
        except Exception as e:
            return format_error("wavexis_stop", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def wavexis_wait(input: WaitInput) -> str:
        """Wait for a specific condition on the page.

        Args:
            input: Wait parameters (strategy, selector, timeout).

        Returns:
            JSON string with status ``"ok"`` and ``elapsed_ms``.
        """
        try:
            session = session_manager.get(input.session_id)
            wait = session_manager.make_wait(
                strategy=input.strategy,
                selector=input.selector,
                url_pattern=input.url_pattern,
                timeout=input.timeout,
            )
            start = time.monotonic()
            await session.backend.wait_for(wait)
            elapsed = int((time.monotonic() - start) * 1000)
            return format_json_response({"status": "ok", "elapsed_ms": elapsed})
        except Exception as e:
            return format_error("wavexis_wait", e)
