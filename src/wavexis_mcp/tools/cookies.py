"""Cookie management tools for WaveXisMCP.

Provides tools for getting, setting, deleting, and clearing
browser cookies.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from wavexis.config import CookieParams

from wavexis_mcp.formatter import format_error, format_json_response
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

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    ))
    async def wavexis_cookies_get(input: CookiesGetInput) -> str:
        """Get all cookies for the current page.

        Args:
            input: Cookie query parameters.

        Returns:
            JSON string with ``cookies`` list and ``count``.
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
                cookies = await backend.get_cookies()
                return format_json_response({"cookies": cookies, "count": len(cookies)})
            finally:
                await session_manager.release_backend(backend, sid)
        except Exception as e:
            return format_error("wavexis_cookies_get", e)

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=False,
        openWorldHint=True,
    ))
    async def wavexis_cookies_set(input: CookiesSetInput) -> str:
        """Set a cookie in the browser.

        Args:
            input: Cookie parameters (name, value, domain, etc.).

        Returns:
            JSON string with status ``"ok"``.
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
                await backend.set_cookie(CookieParams(
                    name=input.name,
                    value=input.value,
                    domain=input.domain,
                    path=input.path,
                    secure=input.secure,
                    http_only=input.http_only,
                    same_site=input.same_site,
                ))
                return format_json_response({"status": "ok"})
            finally:
                await session_manager.release_backend(backend, sid)
        except Exception as e:
            return format_error("wavexis_cookies_set", e)

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=True,
        idempotentHint=True,
        openWorldHint=True,
    ))
    async def wavexis_cookies_delete(input: CookiesDeleteInput) -> str:
        """Delete cookies matching name and domain.

        Args:
            input: Cookie deletion parameters.

        Returns:
            JSON string with status ``"ok"``.
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
                await backend.delete_cookie(input.name, input.domain)
                return format_json_response({"status": "ok"})
            finally:
                await session_manager.release_backend(backend, sid)
        except Exception as e:
            return format_error("wavexis_cookies_delete", e)

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=True,
        idempotentHint=True,
        openWorldHint=False,
    ))
    async def wavexis_cookies_clear(input: CookiesClearInput) -> str:
        """Clear all browser cookies.

        Args:
            input: Session reference parameters.

        Returns:
            JSON string with status ``"ok"``.
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.clear_cookies()
            return format_json_response({"status": "ok"})
        except Exception as e:
            return format_error("wavexis_cookies_clear", e)
