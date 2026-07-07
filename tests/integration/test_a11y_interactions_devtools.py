"""Integration test for A11y + Interactions + DevTools tiers.

Requires Chrome and cdpwave installed. Run with:
    pytest tests/integration/test_a11y_interactions_devtools.py -v -m integration
"""

from __future__ import annotations

import json

import pytest

from wavexis_mcp.models import (
    A11ySnapshotInput,
    ConsoleMessagesInput,
    CSSGetComputedInput,
    NavigateInput,
    PerfMetricsInput,
    SessionCloseInput,
    SessionOpenInput,
)
from wavexis_mcp.session import SessionManager


@pytest.mark.integration
@pytest.mark.chrome
async def test_a11y_interactions_devtools_workflow() -> None:
    """Full workflow: session → navigate → a11y → perf → console → CSS → close."""
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.a11y import register as register_a11y
    from wavexis_mcp.tools.devtools import register as register_devtools
    from wavexis_mcp.tools.interactions import register as register_interactions
    from wavexis_mcp.tools.navigation import register as register_nav
    from wavexis_mcp.tools.session import register as register_session

    mcp = FastMCP("test-integration")
    mgr = SessionManager()
    register_session(mcp, mgr)
    register_nav(mcp, mgr)
    register_a11y(mcp, mgr)
    register_interactions(mcp, mgr)
    register_devtools(mcp, mgr)

    open_tool = mcp._tool_manager.get_tool("wavexis_session_open")
    result = await open_tool.fn(SessionOpenInput(backend="cdp", headless=True))
    data = json.loads(result)
    assert data["status"] == "ok"
    session_id = data["session_id"]

    try:
        nav_tool = mcp._tool_manager.get_tool("wavexis_navigate")
        result = await nav_tool.fn(
            NavigateInput(url="https://example.com", session_id=session_id)
        )
        data = json.loads(result)
        assert data["status"] == "ok"

        a11y_tool = mcp._tool_manager.get_tool("wavexis_a11y_snapshot")
        result = await a11y_tool.fn(A11ySnapshotInput(session_id=session_id))
        data = json.loads(result)
        assert data["element_count"] > 0
        assert "el-" in data["text"]

        perf_tool = mcp._tool_manager.get_tool("wavexis_perf_metrics")
        result = await perf_tool.fn(PerfMetricsInput(session_id=session_id))
        data = json.loads(result)
        assert "metrics" in data

        console_tool = mcp._tool_manager.get_tool("wavexis_console_messages")
        result = await console_tool.fn(
            ConsoleMessagesInput(session_id=session_id, all=True)
        )
        data = json.loads(result)
        assert "messages" in data

        css_tool = mcp._tool_manager.get_tool("wavexis_css_get_computed")
        result = await css_tool.fn(
            CSSGetComputedInput(selector="body", session_id=session_id)
        )
        data = json.loads(result)
        assert "computed" in data
    finally:
        close_tool = mcp._tool_manager.get_tool("wavexis_session_close")
        result = await close_tool.fn(SessionCloseInput(session_id=session_id))
        data = json.loads(result)
        assert data["status"] == "ok"
