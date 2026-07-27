"""Unit tests for video recording tools."""

from __future__ import annotations

import asyncio
import base64
import json
from typing import Any
from unittest.mock import MagicMock

import pytest

from wavexis_mcp.models import (
    VideoActionOverlayInput,
    VideoAddChapterInput,
    VideoRecordInput,
    VideoStopInput,
)
from wavexis_mcp.session import SessionManager


def _register(mcp, mgr, recordings=None):
    from wavexis_mcp.tools.video import register

    register(mcp, mgr, recordings)


@pytest.mark.unit
async def test_video_record(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    recordings: dict[str, Any] = {}
    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock, recordings)

    tool = mcp._tool_manager.get_tool("wavexis_video_record")
    result = await tool.fn(VideoRecordInput(session_id=mock_session_id))
    data = json.loads(result)
    assert data["status"] == "recording"
    assert "recording_id" in data
    assert data["recording_id"] in recordings


@pytest.mark.unit
async def test_video_stop(session_manager_with_mock: SessionManager, mock_session_id: str) -> None:
    from mcp.server.fastmcp import FastMCP

    recordings: dict[str, Any] = {}
    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock, recordings)

    record_tool = mcp._tool_manager.get_tool("wavexis_video_record")
    result = await record_tool.fn(VideoRecordInput(session_id=mock_session_id))
    data = json.loads(result)
    recording_id = data["recording_id"]

    stop_tool = mcp._tool_manager.get_tool("wavexis_video_stop")
    result = await stop_tool.fn(VideoStopInput(session_id=mock_session_id))
    data = json.loads(result)
    assert "duration_ms" in data
    assert data["size_bytes"] == 0
    assert recording_id not in recordings


@pytest.mark.unit
async def test_video_record_attaches_screencast_handler(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    recordings: dict[str, Any] = {}
    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock, recordings)

    session = session_manager_with_mock.get(mock_session_id)
    cdp_session = MagicMock()
    session.backend._require_session = MagicMock(return_value=cdp_session)

    record_tool = mcp._tool_manager.get_tool("wavexis_video_record")
    result = await record_tool.fn(VideoRecordInput(session_id=mock_session_id))
    data = json.loads(result)
    recording_id = data["recording_id"]

    assert "_screencast_target" in recordings[recording_id]
    cdp_session.on.assert_called_once()

    stop_tool = mcp._tool_manager.get_tool("wavexis_video_stop")
    await stop_tool.fn(VideoStopInput(session_id=mock_session_id))
    cdp_session.off.assert_called_once()


@pytest.mark.unit
async def test_video_add_chapter(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    recordings: dict[str, Any] = {}
    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock, recordings)

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

    assert recordings[recording_id]["chapters"][0]["title"] == "Test chapter"


@pytest.mark.unit
async def test_video_action_overlay(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_video_action_overlay")
    result = await tool.fn(VideoActionOverlayInput(session_id=mock_session_id, show=True))
    data = json.loads(result)
    assert data["status"] == "ok"
    assert data["show"] is True


@pytest.mark.unit
async def test_append_frame_respects_total_limit() -> None:
    """_append_frame must not exceed _MAX_TOTAL_FRAMES under concurrency."""
    from wavexis_mcp.tools.video import _MAX_TOTAL_FRAMES, _append_frame

    recording: dict[str, Any] = {"frames": [], "_stopped": False}
    total_ref: list[int] = [_MAX_TOTAL_FRAMES]
    data = base64.b64encode(b"frame").decode()

    await _append_frame(recording, total_ref, data)
    assert recording["frames"] == []
    assert total_ref[0] == _MAX_TOTAL_FRAMES


@pytest.mark.unit
async def test_append_frame_respects_per_recording_limit() -> None:
    """_append_frame must not exceed _MAX_FRAMES_PER_RECORDING."""
    from wavexis_mcp.tools.video import _MAX_FRAMES_PER_RECORDING, _append_frame

    recording: dict[str, Any] = {"frames": [b"x"] * _MAX_FRAMES_PER_RECORDING, "_stopped": False}
    total_ref: list[int] = [0]
    data = base64.b64encode(b"frame").decode()

    await _append_frame(recording, total_ref, data)
    assert len(recording["frames"]) == _MAX_FRAMES_PER_RECORDING
    assert total_ref[0] == 0


@pytest.mark.unit
async def test_append_frame_respects_stopped_flag() -> None:
    """_append_frame must drop frames once recording is stopped."""
    from wavexis_mcp.tools.video import _append_frame

    recording: dict[str, Any] = {"frames": [], "_stopped": True}
    total_ref: list[int] = [0]
    data = base64.b64encode(b"frame").decode()

    await _append_frame(recording, total_ref, data)
    assert recording["frames"] == []
    assert total_ref[0] == 0


@pytest.mark.unit
async def test_video_add_chapter_is_concurrency_safe(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    """Concurrent add_chapter calls must not lose chapters."""
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.video import register

    recordings: dict[str, Any] = {}
    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock, recordings)

    record_tool = mcp._tool_manager.get_tool("wavexis_video_record")
    result = await record_tool.fn(VideoRecordInput(session_id=mock_session_id))
    recording_id = json.loads(result)["recording_id"]

    chapter_tool = mcp._tool_manager.get_tool("wavexis_video_add_chapter")
    titles = [f"chapter-{i}" for i in range(20)]
    await asyncio.gather(
        *(
            chapter_tool.fn(
                VideoAddChapterInput(
                    session_id=mock_session_id,
                    recording_id=recording_id,
                    title=title,
                    timestamp_ms=i * 100,
                )
            )
            for i, title in enumerate(titles)
        )
    )

    assert len(recordings[recording_id]["chapters"]) == 20
    assert {c["title"] for c in recordings[recording_id]["chapters"]} == set(titles)
