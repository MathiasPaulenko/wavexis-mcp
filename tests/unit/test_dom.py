"""Unit tests for DOM tools."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from wavexis_mcp.models import (
    DOMFocusInput,
    DOMGetAttrInput,
    DOMGetInput,
    DOMQueryInput,
    DOMRemoveAttrInput,
    DOMRemoveInput,
    DOMScrollInput,
    DOMSetAttrInput,
    DOMSnapshotInput,
)
from wavexis_mcp.session import SessionManager


@pytest.mark.unit
async def test_dom_get(mock_backend: AsyncMock) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.dom import register

    mcp = FastMCP("test")
    mgr = SessionManager()
    mgr._backend_manager.select = MagicMock(return_value=mock_backend)
    register(mcp, mgr)

    tool = mcp._tool_manager.get_tool("wavexis_dom_get")
    result = await tool.fn(DOMGetInput(selector="h1", url="https://example.com"))
    data = json.loads(result)
    assert "html" in data
    assert data["selector"] == "h1"


@pytest.mark.unit
async def test_dom_query_pagination(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.dom import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    session_manager_with_mock.get(mock_session_id).backend.dom_query = AsyncMock(
        return_value=[{"tag": f"div{i}"} for i in range(10)]
    )

    tool = mcp._tool_manager.get_tool("wavexis_dom_query")
    result = await tool.fn(
        DOMQueryInput(selector="div", session_id=mock_session_id, all=True, limit=3, offset=2)
    )
    data = json.loads(result)
    assert data["count"] == 3
    assert data["total"] == 10


@pytest.mark.unit
async def test_dom_set_attr(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.dom import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_dom_set_attr")
    result = await tool.fn(
        DOMSetAttrInput(selector="h1", name="class", value="title", session_id=mock_session_id)
    )
    data = json.loads(result)
    assert data["status"] == "ok"


@pytest.mark.unit
async def test_dom_get_attr(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.dom import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_dom_get_attr")
    result = await tool.fn(
        DOMGetAttrInput(selector="h1", name="id", session_id=mock_session_id)
    )
    data = json.loads(result)
    assert data["value"] == "value"


@pytest.mark.unit
async def test_dom_remove_attr(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.dom import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_dom_remove_attr")
    result = await tool.fn(
        DOMRemoveAttrInput(selector="h1", name="class", session_id=mock_session_id)
    )
    data = json.loads(result)
    assert data["status"] == "ok"


@pytest.mark.unit
async def test_dom_remove(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.dom import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_dom_remove")
    result = await tool.fn(DOMRemoveInput(selector="div", session_id=mock_session_id))
    data = json.loads(result)
    assert data["status"] == "ok"


@pytest.mark.unit
async def test_dom_focus(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.dom import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_dom_focus")
    result = await tool.fn(DOMFocusInput(selector="input", session_id=mock_session_id))
    data = json.loads(result)
    assert data["status"] == "ok"


@pytest.mark.unit
async def test_dom_scroll(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.dom import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_dom_scroll")
    result = await tool.fn(DOMScrollInput(session_id=mock_session_id, y=500))
    data = json.loads(result)
    assert data["status"] == "ok"


@pytest.mark.unit
async def test_dom_snapshot(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.dom import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_dom_snapshot")
    result = await tool.fn(DOMSnapshotInput(session_id=mock_session_id))
    data = json.loads(result)
    assert "snapshot" in data
