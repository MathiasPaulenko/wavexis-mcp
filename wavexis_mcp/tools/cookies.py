"""Cookie management tools for WaveXisMCP.

Provides tools for getting, setting, deleting, and clearing
browser cookies.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from wavexis.config import CookieParams

from wavexis_mcp.formatter import format_error, format_json_response, validate_url
from wavexis_mcp.models import (
    CookiesClearInput,
    CookiesDeleteInput,
    CookiesGetInput,
    CookiesSetInput,
)
from wavexis_mcp.session import SessionManager


def register(mcp: FastMCP, session_manager: SessionManager) -> None:
    """Register all cookie tools on the FastMCP server.

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
    async def wavexis_cookies_get(input: CookiesGetInput) -> str:
        """Retrieve all cookies for the current page context.

        Use ``wavexis_cookies_set`` to add a cookie, or
        ``wavexis_cookies_clear`` to remove all cookies at once.

        Side effects: launches/acquires a browser backend, navigates to ``url``
        if provided; read-only with respect to browser state.
        Returns: JSON string with keys: 'status' ('ok'/'error'), 'cookies'
        (list[dict]), 'count' (int).
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
                    validate_url(input.url)
                    await backend.navigate(input.url, wait)
                cookies = await backend.get_cookies()
                return format_json_response({"cookies": cookies, "count": len(cookies)})
            finally:
                await session_manager.release_backend(backend, sid)
        except Exception as e:
            return format_error("wavexis_cookies_get", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=True,
        )
    )
    async def wavexis_cookies_set(input: CookiesSetInput) -> str:
        """Set a single cookie in the browser for the current page.

        Use ``wavexis_cookies_get`` to read cookies, or
        ``wavexis_cookies_delete`` to remove a specific cookie.

        Side effects: launches/acquires a browser backend, navigates to ``url``
        if provided, mutates browser cookie state.
        Returns: JSON string with keys: 'status' ('ok'/'error').
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
                    validate_url(input.url)
                    await backend.navigate(input.url, wait)
                await backend.set_cookie(
                    CookieParams(
                        name=input.name,
                        value=input.value,
                        domain=input.domain,
                        path=input.path,
                        secure=input.secure,
                        http_only=input.http_only,
                        same_site=input.same_site,
                    )
                )
                return format_json_response({"status": "ok"})
            finally:
                await session_manager.release_backend(backend, sid)
        except Exception as e:
            return format_error("wavexis_cookies_set", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=True,
            idempotentHint=True,
            openWorldHint=True,
        )
    )
    async def wavexis_cookies_delete(input: CookiesDeleteInput) -> str:
        """Delete cookies matching a name and domain in the browser.

        Use ``wavexis_cookies_clear`` to remove all cookies, or
        ``wavexis_cookies_set`` to add a new cookie.

        Side effects: launches/acquires a browser backend, navigates to ``url``
        if provided, destructively removes matching cookies from browser state.
        Returns: JSON string with keys: 'status' ('ok'/'error').
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
                    validate_url(input.url)
                    await backend.navigate(input.url, wait)
                await backend.delete_cookie(input.name, input.domain)
                return format_json_response({"status": "ok"})
            finally:
                await session_manager.release_backend(backend, sid)
        except Exception as e:
            return format_error("wavexis_cookies_delete", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=True,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def wavexis_cookies_clear(input: CookiesClearInput) -> str:
        """Clear all cookies from the browser session.

        Use ``wavexis_cookies_delete`` to remove a specific cookie, or
        ``wavexis_cookies_get`` to inspect cookies before clearing.

        Side effects: uses an existing session backend, destructively removes
        all cookies from the browser.
        Returns: JSON string with keys: 'status' ('ok'/'error').
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.clear_cookies()
            return format_json_response({"status": "ok"})
        except Exception as e:
            return format_error("wavexis_cookies_clear", e)
