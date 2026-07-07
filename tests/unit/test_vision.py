"""Unit tests for vision (coordinate-based mouse) tools."""

from __future__ import annotations

import json

import pytest

from wavexis_mcp.models import (
    MouseClickXYInput,
    MouseDoubleClickXYInput,
    MouseDownInput,
    MouseMoveInput,
    MouseMoveXYInput,
    MouseUpInput,
)
from wavexis_mcp.session import SessionManager


def _register(mcp, mgr):
    from wavexis_mcp.tools.vision import register

    register(mcp, mgr)


# ── mouse_move (by selector) ──


@pytest.mark.unit
async def test_mouse_move(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_mouse_move")
    result = await tool.fn(MouseMoveInput(session_id=mock_session_id, selector="button"))
    data = json.loads(result)
    assert data["status"] == "ok"
    assert data["selector"] == "button"


# ── mouse_move_xy ──


@pytest.mark.unit
async def test_mouse_move_xy(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_mouse_move_xy")
    result = await tool.fn(MouseMoveXYInput(session_id=mock_session_id, x=100, y=200))
    data = json.loads(result)
    assert data["status"] == "ok"
    assert data["x"] == 100
    assert data["y"] == 200


# ── mouse_down ──


@pytest.mark.unit
async def test_mouse_down(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_mouse_down")
    result = await tool.fn(MouseDownInput(session_id=mock_session_id, x=50, y=50))
    data = json.loads(result)
    assert data["status"] == "ok"


# ── mouse_up ──


@pytest.mark.unit
async def test_mouse_up(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_mouse_up")
    result = await tool.fn(MouseUpInput(session_id=mock_session_id, x=50, y=50))
    data = json.loads(result)
    assert data["status"] == "ok"


# ── mouse_click_xy ──


@pytest.mark.unit
async def test_mouse_click_xy(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_mouse_click_xy")
    result = await tool.fn(
        MouseClickXYInput(session_id=mock_session_id, x=100, y=100, click_count=2)
    )
    data = json.loads(result)
    assert data["status"] == "ok"
    assert data["x"] == 100
    assert data["y"] == 100
    assert data["click_count"] == 2


# ── mouse_double_click_xy ──


@pytest.mark.unit
async def test_mouse_double_click_xy(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_mouse_double_click_xy")
    result = await tool.fn(
        MouseDoubleClickXYInput(session_id=mock_session_id, x=150, y=150)
    )
    data = json.loads(result)
    assert data["status"] == "ok"
    assert data["x"] == 150
    assert data["y"] == 150
