"""Unit tests for data tools."""

from __future__ import annotations

import json
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

from wavexis_mcp.models import (
    CoreWebVitalsInput,
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
@patch("wavexis.actions.record.asyncio.sleep", new_callable=AsyncMock)
async def test_record(
    _mock_sleep: AsyncMock,
    session_manager_with_mock: SessionManager,
    mock_session_id: str,
    mock_backend: AsyncMock,
) -> None:
    """wavexis_record captures events and generates YAML via wavexis.record_events."""
    from mcp.server.fastmcp import FastMCP

    # Simulate recorded events returned by the injected script.
    recorded_events = json.dumps(
        [
            {"type": "click", "selector": "#login", "text": "Login", "url": "https://example.com"},
            {
                "type": "input",
                "selector": "#email",
                "value": "user@example.com",
                "tag": "input",
            },
            {
                "type": "input",
                "selector": "#password",
                "value": "secret123",
                "tag": "input",
            },
            {"type": "click", "selector": "#submit", "text": "Submit"},
        ]
    )

    # Mock eval to return events JSON on the retrieval call, and "Test Page" for title.
    async def _mock_eval(expression, await_promise=True):
        if "JSON.stringify" in str(expression):
            return recorded_events
        if "document.title" in str(expression):
            return "Test Page"
        return None

    mock_backend.eval = AsyncMock(side_effect=_mock_eval)

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_record")
    result = await tool.fn(RecordInput(url="https://example.com", duration=5, headless=True))
    data = json.loads(result)
    assert "yaml" in data
    assert data["events_captured"] == 4
    assert data["actions_generated"] >= 5  # navigate + 4 events
    assert data["title"] == "Test Page"
    # Verify the YAML contains the expected actions.
    assert "navigate" in data["yaml"]
    assert "click" in data["yaml"]


@pytest.mark.unit
@patch("wavexis.actions.record.asyncio.sleep", new_callable=AsyncMock)
async def test_record_no_events(
    _mock_sleep: AsyncMock,
    session_manager_with_mock: SessionManager,
    mock_session_id: str,
    mock_backend: AsyncMock,
) -> None:
    """wavexis_record with no interactions returns just the navigate action."""
    from mcp.server.fastmcp import FastMCP

    async def _mock_eval(expression, await_promise=True):
        if "JSON.stringify" in str(expression):
            return "[]"
        if "document.title" in str(expression):
            return "Empty Page"
        return None

    mock_backend.eval = AsyncMock(side_effect=_mock_eval)

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_record")
    result = await tool.fn(RecordInput(url="https://example.com", duration=5, headless=True))
    data = json.loads(result)
    assert data["events_captured"] == 0
    assert data["actions_generated"] == 1  # just navigate
    assert "navigate" in data["yaml"]


@pytest.mark.unit
async def test_lighthouse(session_manager_with_mock: SessionManager, mock_session_id: str) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_lighthouse")
    result = await tool.fn(LighthouseInput(url="https://example.com", session_id=mock_session_id))
    data = json.loads(result)
    assert "categories" in data
    assert "performance" in data["categories"]
    assert "accessibility" in data["categories"]


@pytest.mark.unit
async def test_extract(session_manager_with_mock: SessionManager, mock_session_id: str) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    session_manager_with_mock.get(mock_session_id).backend.eval = AsyncMock(
        return_value=[{"title": "Example Title"}]
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
async def test_crawl(session_manager_with_mock: SessionManager, mock_session_id: str) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    session_manager_with_mock.get(mock_session_id).backend.eval = AsyncMock(return_value="Example")

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
    session_manager_with_mock: SessionManager, mock_session_id: str, tmp_path: Any
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_visual_diff")
    result = await tool.fn(
        VisualDiffInput(
            url="https://example.com",
            baseline_path=str(tmp_path / "baseline.png"),
            session_id=mock_session_id,
        )
    )
    data = json.loads(result)
    assert data.get("status") == "not_implemented" or "error" in data


@pytest.mark.unit
async def test_core_web_vitals(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    import sys
    from unittest.mock import MagicMock, patch

    mock_instance = MagicMock()
    mock_instance._collect_cwv = AsyncMock(
        return_value={
            "metrics": {"lcp": 1200, "cls": 0.05, "inp": 100},
            "ratings": {"lcp": "good", "cls": "good", "inp": "good"},
            "score": 95,
        }
    )
    mock_action_cls = MagicMock(return_value=mock_instance)

    with patch.dict(
        sys.modules,
        {
            "wavexis.actions.core_web_vitals": type(sys)("wavexis.actions.core_web_vitals"),
            "wavexis.config": type(sys)("wavexis.config"),
        },
    ):
        sys.modules["wavexis.actions.core_web_vitals"].CoreWebVitalsAction = mock_action_cls
        sys.modules["wavexis.actions.core_web_vitals"].CoreWebVitalsParams = type(
            "CoreWebVitalsParams", (), {"__init__": lambda self, **kw: None}
        )
        sys.modules["wavexis.config"].BrowserOptions = type(
            "BrowserOptions", (), {"__init__": lambda self, **kw: None}
        )
        sys.modules["wavexis.config"].WaitStrategy = type(
            "WaitStrategy", (), {"__init__": lambda self, **kw: None}
        )

        tool = mcp._tool_manager.get_tool("wavexis_core_web_vitals")
        result = await tool.fn(
            CoreWebVitalsInput(url="https://example.com", session_id=mock_session_id)
        )
    data = json.loads(result)
    assert "metrics" in data
    assert "ratings" in data
    assert data["score"] == 95
