"""Utility tools for WaveXisMCP.

Provides ``wavexis_browser_version`` and ``wavexis_backends``
for querying browser and backend information.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from wavexis_mcp.formatter import format_error, format_json_response
from wavexis_mcp.models import BrowserVersionInput
from wavexis_mcp.session import SessionManager


def register(mcp: FastMCP, session_manager: SessionManager) -> None:
    """Register all utility tools on the FastMCP server.

    Args:
        mcp: The FastMCP server instance.
        session_manager: The shared session manager.
    """

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def wavexis_browser_version(input: BrowserVersionInput) -> str:
        """Get the browser version string.

        Args:
            input: Browser version parameters.

        Returns:
            JSON string with ``version`` and ``backend``.
        """
        try:
            backend, sid = await session_manager.acquire_backend(
                input.session_id,
                backend=input.backend,
            )
            try:
                version = await backend.browser_version()
                return format_json_response({"version": version, "backend": input.backend})
            finally:
                await session_manager.release_backend(backend, sid)
        except Exception as e:
            return format_error("wavexis_browser_version", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def wavexis_backends() -> str:
        """List available browser backends and their versions.

        Returns:
            JSON string with ``backends`` and ``available`` lists.
        """
        try:
            from wavexis.backend.manager import BackendManager

            mgr = BackendManager()
            available = mgr.list_available()
            versions = mgr.install_check()
            return format_json_response({"backends": versions, "available": available})
        except Exception as e:
            return format_error("wavexis_backends", e)
