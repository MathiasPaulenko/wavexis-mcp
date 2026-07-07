"""Unit tests for video recording tools."""

from __future__ import annotations

import json

import pytest

from wavexis_mcp.models import (
    VideoActionOverlayInput,
    VideoAddChapterInput,
    VideoRecordInput,
    VideoStopInput,
)
from wavexis_mcp.session import SessionManager
from wavexis_mcp.tools.video import _recordings


def _register(mcp, mgr):
    from wavexis_mcp.tools.video import register

    register(mcp, mgr)


@pytest.mark.unit
async def test_video_record(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    _recordings.clear()
    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_video_record")
    result = await tool.fn(VideoRecordInput(session_id=mock_session_id))
    data = json.loads(result)
    assert data["status"] == "recording"
    assert "recording_id" in data


@pytest.mark.unit
async def test_video_stop(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    _recordings.clear()
    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    record_tool = mcp._tool_manager.get_tool("wavexis_video_record")
    result = await record_tool.fn(VideoRecordInput(session_id=mock_session_id))
    data = json.loads(result)
    recording_id = data["recording_id"]

    stop_tool = mcp._tool_manager.get_tool("wavexis_video_stop")
    result = await stop_tool.fn(VideoStopInput(session_id=mock_session_id))
    data = json.loads(result)
    assert "duration_ms" in data
    assert data["size_bytes"] == 0
    assert recording_id not in _recordings


@pytest.mark.unit
async def test_video_add_chapter(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    _recordings.clear()
    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    record_tool = mcp._tool_manager.get_tool("wavexis_video_record")
    result = await record_tool.fn(VideoRecordInput(session_id=mock_session_id))
    data = json.loads(result)
    recording_id = data["recording_id"]

    chapter_tool = mcp._tool_manager.get_tool("wavexis_video_add_chapter")
    result = await chapter_tool.fn(
        VideoAddChapterInput(
            session_id=mock_session_id,
            recording_id=recording_id,
            title="Test chapter",
            timestamp_ms=1000,
        )
    )
    data = json.loads(result)
    assert data["status"] == "ok"
    assert data["chapter"]["title"] == "Test chapter"
    assert data["chapter"]["timestamp_ms"] == 1000

    _recordings.clear()


@pytest.mark.unit
async def test_video_action_overlay(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_video_action_overlay")
    result = await tool.fn(
        VideoActionOverlayInput(session_id=mock_session_id, show=True)
    )
    data = json.loads(result)
    assert data["status"] == "ok"
    assert data["show"] is True
