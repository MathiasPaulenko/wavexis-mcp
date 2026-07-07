"""Integration test for vision + video + testing workflow.

Requires Chrome and cdpwave installed. Run with:
    pytest tests/integration/test_vision_video_testing.py -v -m integration
"""

from __future__ import annotations

import json

import pytest

from wavexis_mcp.models import (
    AssertTextVisibleInput,
    AssertURLInput,
    AssertVisibleInput,
    GenerateLocatorInput,
    MouseMoveXYInput,
    NavigateInput,
    SessionCloseInput,
    SessionOpenInput,
    VideoAddChapterInput,
    VideoRecordInput,
    VideoStopInput,
)
from wavexis_mcp.session import SessionManager


@pytest.mark.integration
@pytest.mark.chrome
async def test_vision_video_testing_workflow() -> None:
    """Full workflow: session → navigate → mouse move → video → assertions → close."""
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.capture import register as register_capture
    from wavexis_mcp.tools.navigation import register as register_nav
    from wavexis_mcp.tools.session import register as register_session
    from wavexis_mcp.tools.testing import register as register_testing
    from wavexis_mcp.tools.video import register as register_video
    from wavexis_mcp.tools.vision import register as register_vision

    mcp = FastMCP("test-integration")
    mgr = SessionManager()
    register_session(mcp, mgr)
    register_nav(mcp, mgr)
    register_capture(mcp, mgr)
    register_vision(mcp, mgr)
    register_video(mcp, mgr)
    register_testing(mcp, mgr)

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

        move_tool = mcp._tool_manager.get_tool("wavexis_mouse_move_xy")
        result = await move_tool.fn(
            MouseMoveXYInput(session_id=session_id, x=100, y=100)
        )
        data = json.loads(result)
        assert data["status"] == "ok"

        record_tool = mcp._tool_manager.get_tool("wavexis_video_record")
        result = await record_tool.fn(VideoRecordInput(session_id=session_id))
        data = json.loads(result)
        assert data["status"] == "recording"
        recording_id = data["recording_id"]

        chapter_tool = mcp._tool_manager.get_tool("wavexis_video_add_chapter")
        result = await chapter_tool.fn(
            VideoAddChapterInput(
                session_id=session_id,
                recording_id=recording_id,
                title="clicked",
            )
        )
        data = json.loads(result)
        assert data["status"] == "ok"

        stop_tool = mcp._tool_manager.get_tool("wavexis_video_stop")
        result = await stop_tool.fn(VideoStopInput(session_id=session_id))
        data = json.loads(result)
        assert "duration_ms" in data

        assert_visible_tool = mcp._tool_manager.get_tool("wavexis_assert_visible")
        result = await assert_visible_tool.fn(
            AssertVisibleInput(session_id=session_id, selector="body", timeout=5000)
        )
        data = json.loads(result)
        assert data["passed"] is True

        assert_text_tool = mcp._tool_manager.get_tool("wavexis_assert_text_visible")
        result = await assert_text_tool.fn(
            AssertTextVisibleInput(
                session_id=session_id, text="Example", timeout=5000
            )
        )
        data = json.loads(result)
        assert data["passed"] is True

        assert_url_tool = mcp._tool_manager.get_tool("wavexis_assert_url")
        result = await assert_url_tool.fn(
            AssertURLInput(session_id=session_id, url_pattern="example.com")
        )
        data = json.loads(result)
        assert data["passed"] is True

        locator_tool = mcp._tool_manager.get_tool("wavexis_generate_locator")
        result = await locator_tool.fn(
            GenerateLocatorInput(
                session_id=session_id, selector="h1", description="main heading"
            )
        )
        data = json.loads(result)
        assert "locator" in data

    finally:
        close_tool = mcp._tool_manager.get_tool("wavexis_session_close")
        result = await close_tool.fn(SessionCloseInput(session_id=session_id))
        data = json.loads(result)
        assert data["status"] == "ok"
