"""Integration test for core workflow: session → navigate → screenshot → close.

Requires Chrome and cdpwave installed. Run with:
    pytest tests/integration/test_core_workflow.py -v -m integration
"""

from __future__ import annotations

import json

import pytest

from wavexis_mcp.models import (
    NavigateInput,
    ScreenshotInput,
    SessionCloseInput,
    SessionInfoInput,
    SessionOpenInput,
)
from wavexis_mcp.session import SessionManager


@pytest.mark.integration
@pytest.mark.chrome
async def test_session_navigate_screenshot_close() -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.capture import register as register_capture
    from wavexis_mcp.tools.navigation import register as register_nav
    from wavexis_mcp.tools.session import register as register_session

    mcp = FastMCP("test-integration")
    mgr = SessionManager()
    register_session(mcp, mgr)
    register_nav(mcp, mgr)
    register_capture(mcp, mgr)

    open_tool = mcp._tool_manager.get_tool("wavexis_session_open")
    result = await open_tool.fn(SessionOpenInput(backend="cdp", headless=True))
    data = json.loads(result)
    assert data["status"] == "ok"
    session_id = data["session_id"]

    try:
        nav_tool = mcp._tool_manager.get_tool("wavexis_navigate")
        result = await nav_tool.fn(NavigateInput(url="https://example.com", session_id=session_id))
        data = json.loads(result)
        assert data["status"] == "ok"

        info_tool = mcp._tool_manager.get_tool("wavexis_session_info")
        result = await info_tool.fn(SessionInfoInput(session_id=session_id))
        data = json.loads(result)
        assert data["session_id"] == session_id

        shot_tool = mcp._tool_manager.get_tool("wavexis_screenshot")
        result = await shot_tool.fn(ScreenshotInput(session_id=session_id))
        data = json.loads(result)
        assert data["status"] == "ok"
        assert "base64" in data
    finally:
        close_tool = mcp._tool_manager.get_tool("wavexis_session_close")
        result = await close_tool.fn(SessionCloseInput(session_id=session_id))
        data = json.loads(result)
        assert data["status"] == "ok"


@pytest.mark.integration
@pytest.mark.chrome
async def test_stateless_screenshot() -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.capture import register

    mcp = FastMCP("test-integration")
    mgr = SessionManager()
    register(mcp, mgr)

    tool = mcp._tool_manager.get_tool("wavexis_screenshot")
    result = await tool.fn(ScreenshotInput(url="https://example.com", headless=True))
    data = json.loads(result)
    assert data["status"] == "ok"
    assert "base64" in data
