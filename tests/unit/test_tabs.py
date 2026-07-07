"""Unit tests for tab tools."""

from __future__ import annotations

import json

import pytest

from wavexis_mcp.models import (
    ActivateTabInput,
    CloseTabInput,
    ListTabsInput,
    NewTabInput,
)


@pytest.mark.unit
async def test_list_tabs(session_manager_with_mock, mock_session_id: str) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.tabs import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_list_tabs")
    result = await tool.fn(ListTabsInput(session_id=mock_session_id))
    data = json.loads(result)
    assert "tabs" in data
    assert data["count"] == 1


@pytest.mark.unit
async def test_new_tab(session_manager_with_mock, mock_session_id: str) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.tabs import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_new_tab")
    result = await tool.fn(NewTabInput(session_id=mock_session_id, url="https://example.com"))
    data = json.loads(result)
    assert data["tab_id"] == "tab-2"


@pytest.mark.unit
async def test_close_tab(session_manager_with_mock, mock_session_id: str) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.tabs import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_close_tab")
    result = await tool.fn(CloseTabInput(session_id=mock_session_id, tab_id="tab-2"))
    data = json.loads(result)
    assert data["status"] == "ok"


@pytest.mark.unit
async def test_activate_tab(session_manager_with_mock, mock_session_id: str) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.tabs import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_activate_tab")
    result = await tool.fn(ActivateTabInput(session_id=mock_session_id, tab_id="tab-2"))
    data = json.loads(result)
    assert data["status"] == "ok"
