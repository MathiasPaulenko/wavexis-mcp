"""Navigation tools for WaveXisMCP.

Provides navigate, back, forward, reload, stop, and wait tools
for controlling browser navigation.
"""

from __future__ import annotations

import time

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from wavexis_mcp.formatter import format_error, format_json_response, validate_url
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
        """Navigate the browser to a URL with a configurable wait strategy.

        Use for direct URL navigation; use wavexis_back/wavexis_forward for
        history navigation, or wavexis_act for natural-language interaction
        instead.

        Side effects: Issues a network request to the target URL and replaces
        the current page content; may auto-create a stateless session if
        session_id is omitted.
        Returns: JSON string with keys: 'status' ('ok'/'error'), 'url' (str).
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
                validate_url(input.url)
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
        """Navigate backward one step in the browser history.

        Use for history navigation instead of wavexis_navigate when the target
        is the previous page.

        Side effects: Changes the active page to the previous history entry;
        may trigger network requests if that page was not cached.
        Returns: JSON string with keys: 'status' ('ok'/'error').
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
        """Navigate forward one step in the browser history.

        Use after wavexis_back to restore a page; use wavexis_navigate for
        direct URL navigation instead.

        Side effects: Changes the active page to the next history entry; may
        trigger network requests if that page was not cached.
        Returns: JSON string with keys: 'status' ('ok'/'error').
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
        """Reload the current page, optionally bypassing the cache.

        Use to refresh stale content or retry a failed load; use
        wavexis_navigate to go to a different URL instead.

        Side effects: Re-issues network requests for the current page and its
        resources; discards in-memory page state.
        Returns: JSON string with keys: 'status' ('ok'/'error').
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
        """Stop all pending navigations and resource loads in the session.

        Use when a page load is hanging or no longer needed; use wavexis_wait
        to wait for a load to complete instead.

        Side effects: Aborts in-flight network requests and pending
        navigations; the page is left in its current partial state.
        Returns: JSON string with keys: 'status' ('ok'/'error').
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
        """Block until a page condition (load, selector, URL, network idle) is met.

        Use after wavexis_navigate when the wait strategy was 'none', or to
        wait for dynamic content; use wavexis_stop to cancel a load instead.

        Side effects: None — read-only polling with no page mutations; blocks
        the tool call up to the configured timeout.
        Returns: JSON string with keys: 'status' ('ok'/'error'),
        'elapsed_ms' (int).
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
