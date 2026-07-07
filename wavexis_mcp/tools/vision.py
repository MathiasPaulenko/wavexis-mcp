"""Vision (coordinate-based mouse) tools for WaveXisMCP.

Provides pixel-precise mouse operations: move by selector, move by
coordinates, mouse down/up, click by coordinates, and double-click
by coordinates.  All tools require an active session.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from wavexis_mcp.formatter import format_error, format_json_response
from wavexis_mcp.models import (
    MouseClickXYInput,
    MouseDoubleClickXYInput,
    MouseDownInput,
    MouseMoveInput,
    MouseMoveXYInput,
    MouseUpInput,
)
from wavexis_mcp.session import SessionManager


def register(mcp: FastMCP, session_manager: SessionManager) -> None:
    """Register all vision tools on the FastMCP server.

    Args:
        mcp: The FastMCP server instance.
        session_manager: The shared session manager.
    """

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=True,
        )
    )
    async def wavexis_mouse_move(input: MouseMoveInput) -> str:
        """Move the mouse to an element matching a CSS selector.

        Args:
            input: Mouse move parameters (selector).

        Returns:
            JSON string with status ``"ok"`` and ``selector``.
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.hover(input.selector)
            return format_json_response({"status": "ok", "selector": input.selector})
        except Exception as e:
            return format_error("wavexis_mouse_move", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=True,
        )
    )
    async def wavexis_mouse_move_xy(input: MouseMoveXYInput) -> str:
        """Move the mouse to absolute pixel coordinates.

        Args:
            input: Mouse move parameters (x, y).

        Returns:
            JSON string with status ``"ok"`` and coordinates.
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.raw(
                "Input.dispatchMouseEvent",
                {"type": "mouseMoved", "x": input.x, "y": input.y},
            )
            return format_json_response(
                {
                    "status": "ok",
                    "x": input.x,
                    "y": input.y,
                }
            )
        except Exception as e:
            return format_error("wavexis_mouse_move_xy", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=True,
            idempotentHint=False,
            openWorldHint=True,
        )
    )
    async def wavexis_mouse_down(input: MouseDownInput) -> str:
        """Press a mouse button at the given coordinates.

        Args:
            input: Mouse down parameters (button, x, y).

        Returns:
            JSON string with status ``"ok"``.
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.raw(
                "Input.dispatchMouseEvent",
                {
                    "type": "mousePressed",
                    "x": input.x,
                    "y": input.y,
                    "button": input.button,
                    "clickCount": 1,
                },
            )
            return format_json_response({"status": "ok"})
        except Exception as e:
            return format_error("wavexis_mouse_down", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=True,
            idempotentHint=False,
            openWorldHint=True,
        )
    )
    async def wavexis_mouse_up(input: MouseUpInput) -> str:
        """Release a mouse button at the given coordinates.

        Args:
            input: Mouse up parameters (button, x, y).

        Returns:
            JSON string with status ``"ok"``.
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.raw(
                "Input.dispatchMouseEvent",
                {
                    "type": "mouseReleased",
                    "x": input.x,
                    "y": input.y,
                    "button": input.button,
                    "clickCount": 1,
                },
            )
            return format_json_response({"status": "ok"})
        except Exception as e:
            return format_error("wavexis_mouse_up", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=True,
            idempotentHint=False,
            openWorldHint=True,
        )
    )
    async def wavexis_mouse_click_xy(input: MouseClickXYInput) -> str:
        """Click at absolute pixel coordinates (press + release).

        Args:
            input: Click parameters (x, y, button, click_count).

        Returns:
            JSON string with status ``"ok"`` and coordinates.
        """
        try:
            session = session_manager.get(input.session_id)
            for _ in range(input.click_count):
                await session.backend.raw(
                    "Input.dispatchMouseEvent",
                    {
                        "type": "mousePressed",
                        "x": input.x,
                        "y": input.y,
                        "button": input.button,
                        "clickCount": 1,
                    },
                )
                await session.backend.raw(
                    "Input.dispatchMouseEvent",
                    {
                        "type": "mouseReleased",
                        "x": input.x,
                        "y": input.y,
                        "button": input.button,
                        "clickCount": 1,
                    },
                )
            return format_json_response(
                {
                    "status": "ok",
                    "x": input.x,
                    "y": input.y,
                    "click_count": input.click_count,
                }
            )
        except Exception as e:
            return format_error("wavexis_mouse_click_xy", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=True,
            idempotentHint=False,
            openWorldHint=True,
        )
    )
    async def wavexis_mouse_double_click_xy(input: MouseDoubleClickXYInput) -> str:
        """Double-click at absolute pixel coordinates.

        Args:
            input: Double-click parameters (x, y, button).

        Returns:
            JSON string with status ``"ok"`` and coordinates.
        """
        try:
            session = session_manager.get(input.session_id)
            for _ in range(2):
                await session.backend.raw(
                    "Input.dispatchMouseEvent",
                    {
                        "type": "mousePressed",
                        "x": input.x,
                        "y": input.y,
                        "button": input.button,
                        "clickCount": 2,
                    },
                )
                await session.backend.raw(
                    "Input.dispatchMouseEvent",
                    {
                        "type": "mouseReleased",
                        "x": input.x,
                        "y": input.y,
                        "button": input.button,
                        "clickCount": 2,
                    },
                )
            return format_json_response(
                {
                    "status": "ok",
                    "x": input.x,
                    "y": input.y,
                }
            )
        except Exception as e:
            return format_error("wavexis_mouse_double_click_xy", e)
