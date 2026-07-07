"""MCP resources for WaveXisMCP (M3).

Exposes read-only browser state as MCP resources using the
``wavexis://session/{session_id}/...`` URI scheme.
"""

from __future__ import annotations

import json

from mcp.server.fastmcp import FastMCP

from wavexis_mcp.session import SessionManager


def register(mcp: FastMCP, session_manager: SessionManager) -> None:
    """Register all MCP resources on the FastMCP server.

    Args:
        mcp: The FastMCP server instance.
        session_manager: The shared session manager.
    """

    @mcp.resource("wavexis://session/{session_id}/url")
    async def get_session_url(session_id: str) -> str:
        """Current URL of the session."""
        try:
            session = session_manager.get(session_id)
            url = await session.backend.eval("window.location.href")
            return str(url) if url else ""
        except Exception as e:
            return json.dumps({"error": str(e)})

    @mcp.resource("wavexis://session/{session_id}/cookies")
    async def get_session_cookies(session_id: str) -> str:
        """Cookies for the session as JSON."""
        try:
            session = session_manager.get(session_id)
            cookies = await session.backend.get_cookies()
            return json.dumps(cookies, default=str, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": str(e)})

    @mcp.resource("wavexis://session/{session_id}/console")
    async def get_session_console(session_id: str) -> str:
        """Console messages for the session."""
        try:
            session = session_manager.get(session_id)
            messages = await session.backend.capture_console()
            return json.dumps(messages, default=str, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": str(e)})

    @mcp.resource("wavexis://session/{session_id}/tabs")
    async def get_session_tabs(session_id: str) -> str:
        """Open tabs for the session."""
        try:
            session = session_manager.get(session_id)
            tabs = await session.backend.list_tabs()
            return json.dumps(tabs, default=str, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": str(e)})
