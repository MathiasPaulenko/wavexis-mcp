"""Tab management tools for WaveXisMCP.

Provides list, new, close, and activate tools for managing
browser tabs within a session.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from wavexis_mcp.formatter import format_error, format_json_response
from wavexis_mcp.models import (
    ActivateTabInput,
    CloseTabInput,
    ListTabsInput,
    NewTabInput,
)
from wavexis_mcp.session import SessionManager


def register(mcp: FastMCP, session_manager: SessionManager) -> None:
    """Register all tab tools on the FastMCP server.

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
    async def wavexis_list_tabs(input: ListTabsInput) -> str:
        """List all open browser tabs.

        Args:
            input: Session reference parameters.

        Returns:
            JSON string with ``tabs`` list and ``count``.
        """
        try:
            session = session_manager.get(input.session_id)
            tabs = await session.backend.list_tabs()
            return format_json_response({"tabs": tabs, "count": len(tabs)})
        except Exception as e:
            return format_error("wavexis_list_tabs", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=True,
        )
    )
    async def wavexis_new_tab(input: NewTabInput) -> str:
        """Create a new browser tab.

        Args:
            input: New tab parameters (URL).

        Returns:
            JSON string with ``tab_id``.
        """
        try:
            session = session_manager.get(input.session_id)
            tab_id = await session.backend.new_tab(input.url)
            return format_json_response({"tab_id": tab_id, "url": input.url})
        except Exception as e:
            return format_error("wavexis_new_tab", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=True,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def wavexis_close_tab(input: CloseTabInput) -> str:
        """Close a tab by its ID.

        Args:
            input: Close tab parameters (tab_id).

        Returns:
            JSON string with status ``"ok"``.
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.close_tab(input.tab_id)
            return format_json_response({"status": "ok"})
        except Exception as e:
            return format_error("wavexis_close_tab", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def wavexis_activate_tab(input: ActivateTabInput) -> str:
        """Activate (focus) a tab by its ID.

        Args:
            input: Activate tab parameters (tab_id).

        Returns:
            JSON string with status ``"ok"``.
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.activate_tab(input.tab_id)
            return format_json_response({"status": "ok"})
        except Exception as e:
            return format_error("wavexis_activate_tab", e)
