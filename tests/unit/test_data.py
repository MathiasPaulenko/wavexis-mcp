"""Unit tests for data tools."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock

import pytest

from wavexis_mcp.models import (
    CrawlInput,
    ExtractInput,
    LighthouseInput,
    RecordInput,
    VisualDiffInput,
    WebsocketInterceptInput,
)
from wavexis_mcp.session import SessionManager


def _register(mcp, mgr):
    from wavexis_mcp.tools.data import register

    register(mcp, mgr)


@pytest.mark.unit
async def test_record(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_record")
    result = await tool.fn(
        RecordInput(url="https://example.com", duration=5, headless=True)
    )
    data = json.loads(result)
    assert "yaml" in data
    assert data["events_captured"] == 2


@pytest.mark.unit
async def test_lighthouse(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_lighthouse")
    result = await tool.fn(
        LighthouseInput(url="https://example.com", session_id=mock_session_id)
    )
    data = json.loads(result)
    assert "categories" in data
    assert "performance" in data["categories"]
    assert "accessibility" in data["categories"]


@pytest.mark.unit
async def test_extract(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    session_manager_with_mock.get(mock_session_id).backend.eval = AsyncMock(
        return_value="Example Title"
    )

    tool = mcp._tool_manager.get_tool("wavexis_extract")
    result = await tool.fn(
        ExtractInput(
            url="https://example.com",
            schema={"title": "h1"},
            session_id=mock_session_id,
        )
    )
    data = json.loads(result)
    assert "data" in data
    assert data["rows"] == 1
    assert data["data"][0]["title"] == "Example Title"


@pytest.mark.unit
async def test_websocket_intercept(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_websocket_intercept")
    result = await tool.fn(
        WebsocketInterceptInput(
            url="https://example.com",
            duration_ms=500,
            session_id=mock_session_id,
        )
    )
    data = json.loads(result)
    assert "sent" in data
    assert "received" in data


@pytest.mark.unit
async def test_crawl(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    session_manager_with_mock.get(mock_session_id).backend.eval = AsyncMock(
        return_value="Example"
    )

    tool = mcp._tool_manager.get_tool("wavexis_crawl")
    result = await tool.fn(
        CrawlInput(
            start_url="https://example.com",
            max_depth=1,
            max_pages=1,
            session_id=mock_session_id,
        )
    )
    data = json.loads(result)
    assert "pages" in data
    assert data["pages_crawled"] == 1


@pytest.mark.unit
async def test_visual_diff_not_implemented(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_visual_diff")
    result = await tool.fn(
        VisualDiffInput(
            url="https://example.com",
            baseline_path="/tmp/baseline.png",
            session_id=mock_session_id,
        )
    )
    data = json.loads(result)
    assert data["status"] == "not_implemented"
