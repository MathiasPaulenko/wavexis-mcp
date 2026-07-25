"""Unit tests for a11y tools."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from wavexis_mcp.models import A11yAncestorsInput, A11yNodeInput, A11ySnapshotInput
from wavexis_mcp.session import SessionManager
from wavexis_mcp.tools.a11y import _build_a11y_tree, _count_nodes, _format_a11y_tree


@pytest.mark.unit
async def test_a11y_snapshot_stateless(mock_backend: AsyncMock) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.a11y import register

    mcp = FastMCP("test")
    mgr = SessionManager()
    mgr._backend_manager.select = MagicMock(return_value=mock_backend)
    register(mcp, mgr)

    tool = mcp._tool_manager.get_tool("wavexis_a11y_snapshot")
    result = await tool.fn(A11ySnapshotInput(url="https://example.com"))
    data = json.loads(result)
    assert "snapshot" in data
    assert "text" in data
    assert data["element_count"] > 0
    assert "el-" in data["text"]


@pytest.mark.unit
async def test_a11y_snapshot_text_format(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.a11y import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_a11y_snapshot")
    result = await tool.fn(A11ySnapshotInput(session_id=mock_session_id))
    data = json.loads(result)
    text = data["text"]
    assert "[el-" in text
    assert "heading" in text
    assert "button" in text
    assert "Submit" in text


@pytest.mark.unit
async def test_a11y_node(session_manager_with_mock: SessionManager, mock_session_id: str) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.a11y import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_a11y_node")
    result = await tool.fn(A11yNodeInput(node_id="el-1", session_id=mock_session_id))
    data = json.loads(result)
    assert data["node"]["role"] == "button"


@pytest.mark.unit
async def test_a11y_ancestors(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.a11y import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_a11y_ancestors")
    result = await tool.fn(A11yAncestorsInput(node_id="el-1", session_id=mock_session_id))
    data = json.loads(result)
    assert data["count"] == 1
    assert data["ancestors"][0]["role"] == "WebArea"


@pytest.mark.unit
def test_a11y_tree_cycle_detection() -> None:
    """Circular parent/child references must not cause infinite recursion."""
    raw = {
        "nodes": [
            {"nodeId": 1, "childIds": [2], "role": {"value": "WebArea"}, "name": {"value": "root"}},
            {"nodeId": 2, "childIds": [1], "role": {"value": "button"}, "name": {"value": "back"}},
        ]
    }
    nodes = _build_a11y_tree(raw)
    formatted = _format_a11y_tree(nodes)
    count = _count_nodes(formatted)
    assert count >= 1
