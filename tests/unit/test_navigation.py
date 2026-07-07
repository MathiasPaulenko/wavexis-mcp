"""Unit tests for navigation tools."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from wavexis_mcp.models import NavigateInput, ReloadInput, SimpleNavInput, WaitInput
from wavexis_mcp.session import SessionManager


@pytest.mark.unit
async def test_navigate_stateless(mock_backend: AsyncMock) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.navigation import register

    mcp = FastMCP("test")
    mgr = SessionManager()
    mgr._backend_manager.select = MagicMock(return_value=mock_backend)
    register(mcp, mgr)

    tool = mcp._tool_manager.get_tool("wavexis_navigate")
    result = await tool.fn(NavigateInput(url="https://example.com"))
    data = json.loads(result)
    assert data["status"] == "ok"
    assert data["url"] == "https://example.com"
    mock_backend.navigate.assert_called_once()
    mock_backend.close.assert_called_once()


@pytest.mark.unit
async def test_navigate_session(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.navigation import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_navigate")
    result = await tool.fn(NavigateInput(url="https://example.com", session_id=mock_session_id))
    data = json.loads(result)
    assert data["status"] == "ok"
    session_manager_with_mock.get(mock_session_id).backend.navigate.assert_called_once()


@pytest.mark.unit
async def test_back(session_manager_with_mock: SessionManager, mock_session_id: str) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.navigation import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_back")
    result = await tool.fn(SimpleNavInput(session_id=mock_session_id))
    data = json.loads(result)
    assert data["status"] == "ok"


@pytest.mark.unit
async def test_forward(session_manager_with_mock: SessionManager, mock_session_id: str) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.navigation import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_forward")
    result = await tool.fn(SimpleNavInput(session_id=mock_session_id))
    data = json.loads(result)
    assert data["status"] == "ok"


@pytest.mark.unit
async def test_reload(session_manager_with_mock: SessionManager, mock_session_id: str) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.navigation import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_reload")
    result = await tool.fn(ReloadInput(session_id=mock_session_id, ignore_cache=True))
    data = json.loads(result)
    assert data["status"] == "ok"


@pytest.mark.unit
async def test_stop(session_manager_with_mock: SessionManager, mock_session_id: str) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.navigation import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_stop")
    result = await tool.fn(SimpleNavInput(session_id=mock_session_id))
    data = json.loads(result)
    assert data["status"] == "ok"


@pytest.mark.unit
async def test_wait(session_manager_with_mock: SessionManager, mock_session_id: str) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.navigation import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_wait")
    result = await tool.fn(
        WaitInput(session_id=mock_session_id, strategy="selector", selector="h1")
    )
    data = json.loads(result)
    assert data["status"] == "ok"
    assert "elapsed_ms" in data
