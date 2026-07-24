"""Unit tests for Playwright parity tools."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from wavexis_mcp.session import SessionManager
from wavexis_mcp.tools.playwright_parity import (
    ClosePageInput,
    ConsoleClearInput,
    CookieGetInput,
    CookieListInput,
    FindInput,
    GetConfigInput,
    KeyDownInput,
    MouseDragXYInput,
    PressKeysInput,
    register,
)


@pytest.mark.unit
async def test_key_down(session_manager_with_mock: SessionManager, mock_session_id: str) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_key_down")
    result = await tool.fn(KeyDownInput(key="Enter", session_id=mock_session_id))
    data = json.loads(result)
    assert data["status"] == "ok"


@pytest.mark.unit
async def test_press_keys(session_manager_with_mock: SessionManager, mock_session_id: str) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.playwright_parity import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_press_keys")
    result = await tool.fn(PressKeysInput(text="hi", session_id=mock_session_id))
    data = json.loads(result)
    assert data["status"] == "ok"
    assert data["typed"] == "hi"


@pytest.mark.unit
async def test_mouse_drag_xy(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.playwright_parity import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_mouse_drag_xy")
    result = await tool.fn(
        MouseDragXYInput(start_x=0, start_y=0, end_x=100, end_y=100, session_id=mock_session_id)
    )
    data = json.loads(result)
    assert data["status"] == "ok"


@pytest.mark.unit
async def test_console_clear(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.playwright_parity import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_console_clear")
    result = await tool.fn(ConsoleClearInput(session_id=mock_session_id))
    data = json.loads(result)
    assert data["status"] == "ok"


@pytest.mark.unit
async def test_cookie_get(session_manager_with_mock: SessionManager, mock_session_id: str) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.playwright_parity import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    session_manager_with_mock.get(mock_session_id).backend.get_cookies = AsyncMock(
        return_value=[{"name": "sid", "value": "123", "domain": ".example.com", "path": "/"}]
    )

    tool = mcp._tool_manager.get_tool("wavexis_cookie_get")
    result = await tool.fn(CookieGetInput(name="sid", session_id=mock_session_id))
    data = json.loads(result)
    assert data["cookie"]["name"] == "sid"


@pytest.mark.unit
async def test_cookie_list(session_manager_with_mock: SessionManager, mock_session_id: str) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.playwright_parity import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    session_manager_with_mock.get(mock_session_id).backend.get_cookies = AsyncMock(
        return_value=[{"name": "a", "value": "1", "domain": "example.com", "path": "/"}]
    )

    tool = mcp._tool_manager.get_tool("wavexis_cookie_list")
    result = await tool.fn(CookieListInput(session_id=mock_session_id))
    data = json.loads(result)
    assert data["count"] == 1


@pytest.mark.unit
async def test_close_page(session_manager_with_mock: SessionManager, mock_session_id: str) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.playwright_parity import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    backend = session_manager_with_mock.get(mock_session_id).backend
    backend.target_get_targets = AsyncMock(
        return_value=[{"type": "page", "attached": True, "targetId": "t1"}]
    )
    backend.target_close_target = AsyncMock()

    tool = mcp._tool_manager.get_tool("wavexis_close_page")
    result = await tool.fn(ClosePageInput(session_id=mock_session_id))
    data = json.loads(result)
    assert data["status"] == "ok"
    assert data["closed"] == "t1"


@pytest.mark.unit
async def test_find(session_manager_with_mock: SessionManager, mock_session_id: str) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.playwright_parity import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    backend = session_manager_with_mock.get(mock_session_id).backend
    backend.a11y_tree = AsyncMock(
        return_value={
            "nodes": [
                {
                    "nodeId": "1",
                    "role": {"value": "button"},
                    "name": {"value": "Submit"},
                    "childIds": [],
                }
            ]
        }
    )

    tool = mcp._tool_manager.get_tool("wavexis_find")
    result = await tool.fn(FindInput(text="submit", session_id=mock_session_id))
    data = json.loads(result)
    assert data["count"] == 1


@pytest.mark.unit
async def test_get_config(session_manager_with_mock: SessionManager, mock_session_id: str) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.playwright_parity import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    mock_mgr = MagicMock()
    mock_mgr.list_available = MagicMock(return_value=["cdp"])
    mock_mgr.install_check = MagicMock(return_value={"cdp": "1.0"})

    with patch("wavexis.backend.manager.BackendManager", return_value=mock_mgr):
        tool = mcp._tool_manager.get_tool("wavexis_get_config")
        result = await tool.fn(GetConfigInput())
        data = json.loads(result)
        assert data["available_backends"] == ["cdp"]
