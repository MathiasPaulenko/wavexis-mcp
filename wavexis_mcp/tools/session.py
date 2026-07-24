"""Session management tools for WaveXisMCP.

Provides tools for opening, closing, and querying browser sessions.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from wavexis_mcp.formatter import format_error, format_json_response
from wavexis_mcp.models import SessionCloseInput, SessionInfoInput, SessionOpenInput
from wavexis_mcp.session import SessionManager


def register(mcp: FastMCP, session_manager: SessionManager) -> None:
    """Register all session tools on the FastMCP server.

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
    async def wavexis_session_open(input: SessionOpenInput) -> str:
        """Launch a persistent browser session for multi-step workflows.

        Args:
            input: Session parameters (backend, headless, viewport).

        Returns:
            JSON string with ``session_id``, ``backend``, and ``status``.
        """
        try:
            session_id = await session_manager.open(
                backend=input.backend,
                headless=input.headless,
                width=input.width,
                height=input.height,
                user_agent=input.user_agent,
                extra_headers=input.extra_headers,
                proxy=input.proxy,
                timeout=input.timeout,
                user_data_dir=input.user_data_dir,
                connect_endpoint=input.browser_url,
                remote_url=input.remote_url,
                stealth=input.stealth,
            )
            return format_json_response(
                {"session_id": session_id, "backend": input.backend, "status": "ok"}
            )
        except Exception as e:
            return format_error("wavexis_session_open", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=True,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def wavexis_session_close(input: SessionCloseInput) -> str:
        """Close a browser session and release resources.

        Args:
            input: Session close parameters.

        Returns:
            JSON string with ``status`` and ``session_id``.
        """
        try:
            await session_manager.close(input.session_id)
            return format_json_response({"status": "ok", "session_id": input.session_id})
        except Exception as e:
            return format_error("wavexis_session_close", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def wavexis_session_info(input: SessionInfoInput) -> str:
        """Get information about an active browser session.

        Args:
            input: Session info parameters.

        Returns:
            JSON string with ``session_id``, ``backend``, ``created_at``,
            and ``current_url``.
        """
        try:
            info = session_manager.info(input.session_id)
            current_url = await session_manager.call_backend(
                session_manager.get_current_url(input.session_id)
            )
            info["current_url"] = current_url
            return format_json_response(info)
        except Exception as e:
            return format_error("wavexis_session_info", e)
