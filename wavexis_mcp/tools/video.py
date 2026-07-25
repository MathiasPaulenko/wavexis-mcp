"""Video recording tools for WaveXisMCP.

Provides tools for starting and stopping video recordings, adding
chapter markers, and toggling action overlays.  All tools require
an active session.
"""

from __future__ import annotations

import asyncio
import base64
import contextlib
import inspect
import json
import logging
import time
import uuid
from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from wavexis_mcp.formatter import encode_base64, format_error, format_json_response, save_to_file
from wavexis_mcp.models import (
    VideoActionOverlayInput,
    VideoAddChapterInput,
    VideoRecordInput,
    VideoStopInput,
)
from wavexis_mcp.session import SessionManager

_MAX_VIDEO_RECORDINGS = 100
_MAX_FRAMES_PER_RECORDING = 1000
_MAX_TOTAL_FRAMES = 10000

_logger = logging.getLogger(__name__)
_recordings_lock = asyncio.Lock()


def _make_frame_handler(
    recording: dict[str, Any],
    total_ref: list[int],
) -> Any:
    """Create a CDP ``Page.screencastFrame`` handler for *recording*."""

    def handler(params: Any) -> None:
        """Decode and store a screencast frame while respecting limits."""
        if len(recording.get("frames", [])) >= _MAX_FRAMES_PER_RECORDING:
            return
        if total_ref[0] >= _MAX_TOTAL_FRAMES:
            return
        data = params.get("data") if isinstance(params, dict) else None
        if not data:
            return
        try:
            recording["frames"].append(base64.b64decode(data))
            total_ref[0] += 1
        except Exception:
            _logger.exception("Failed to process screencast frame")

    return handler


def _attach_screencast_handler(
    backend: Any,
    recording: dict[str, Any],
    total_ref: list[int],
) -> bool:
    """Attach a ``Page.screencastFrame`` listener to the backend if possible.

    CDP backends expose the event through the CDP session.  BiDi backends
    expose it through the CDP bridge on the BiDi client.  If neither path
    is available the tool still starts/stops the screencast, but no frames
    will be captured.
    """
    target: Any | None = None

    require_session = getattr(backend, "_require_session", None)
    if require_session is not None and not inspect.iscoroutinefunction(require_session):
        try:
            target = require_session()
        except Exception:
            target = None

    if target is None:
        require_launched = getattr(backend, "_require_launched", None)
        if require_launched is not None and not inspect.iscoroutinefunction(require_launched):
            try:
                client = require_launched()
            except Exception:
                client = None
            if client is not None:
                target = getattr(client, "cdp", None)

    if target is None or not hasattr(target, "on") or not hasattr(target, "off"):
        return False

    handler = _make_frame_handler(recording, total_ref)
    try:
        target.on("Page.screencastFrame", handler)
        recording["_screencast_target"] = target
        recording["_screencast_handler"] = handler
        return True
    except Exception:
        return False


def _detach_screencast_handler(recording: dict[str, Any]) -> None:
    """Detach the screencast frame handler if one was attached."""
    target = recording.pop("_screencast_target", None)
    handler = recording.pop("_screencast_handler", None)
    if target is not None and handler is not None:
        with contextlib.suppress(Exception):
            target.off("Page.screencastFrame", handler)


def register(
    mcp: FastMCP,
    session_manager: SessionManager,
    recordings: dict[str, dict[str, Any]] | None = None,
) -> None:
    """Register all video tools on the FastMCP server.

    Args:
        mcp: The FastMCP server instance.
        session_manager: The shared session manager.
        recordings: Optional shared recordings dictionary for testing.
    """
    if recordings is None:
        recordings = {}
    mcp._wavexis_video_recordings = recordings  # type: ignore[attr-defined]
    total_frames: list[int] = [0]

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=True,
        )
    )
    async def wavexis_video_record(input: VideoRecordInput) -> str:
        """Start recording a video of the page.

        Args:
            input: Recording parameters (output_path, width, height).

        Returns:
            JSON string with ``recording_id`` and ``status``.
        """
        try:
            session = session_manager.get(input.session_id)
            recording_id = f"rec-{uuid.uuid4().hex}"
            recording: dict[str, Any] = {
                "session_id": input.session_id,
                "start_time": time.time(),
                "output_path": input.output_path,
                "frames": [],
            }

            # Attach the frame listener before starting the screencast so the
            # first frame is not lost.
            _attach_screencast_handler(session.backend, recording, total_frames)

            start = getattr(session.backend, "page_start_screencast", None)
            if start is not None:
                await start("jpeg", 80, input.width, input.height)
            else:
                await session.backend.raw(
                    "Page.startScreencast",
                    {
                        "format": "jpeg",
                        "quality": 80,
                        "maxWidth": input.width,
                        "maxHeight": input.height,
                        "everyNthFrame": 1,
                    },
                )

            async with _recordings_lock:
                recordings[recording_id] = recording
                while len(recordings) > _MAX_VIDEO_RECORDINGS:
                    oldest = min(recordings, key=lambda rid: recordings[rid]["start_time"])
                    oldest_rec = recordings.pop(oldest)
                    total_frames[0] -= len(oldest_rec.get("frames", []))
            return format_json_response(
                {
                    "recording_id": recording_id,
                    "status": "recording",
                }
            )
        except Exception as e:
            return format_error("wavexis_video_record", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=True,
        )
    )
    async def wavexis_video_stop(input: VideoStopInput) -> str:
        """Stop recording and return the video as base64 or save to file.

        Args:
            input: Stop parameters (output_path).

        Returns:
            JSON string with ``base64`` video data or file ``path``,
            plus ``duration_ms`` and ``size_bytes``.
        """
        try:
            session = session_manager.get(input.session_id)

            stop = getattr(session.backend, "page_stop_screencast", None)
            if stop is not None:
                await stop()
            else:
                await session.backend.raw("Page.stopScreencast", {})

            async with _recordings_lock:
                recording_id = next(
                    (
                        rid
                        for rid, rec in recordings.items()
                        if rec["session_id"] == input.session_id
                    ),
                    None,
                )
                if recording_id is None:
                    return format_error(
                        "wavexis_video_stop",
                        RuntimeError("No active recording for this session"),
                    )

                rec = recordings.pop(recording_id)
                total_frames[0] -= len(rec.get("frames", []))
                _detach_screencast_handler(rec)
            start_time = rec["start_time"]
            duration_ms = int((time.time() - start_time) * 1000)

            frames = rec["frames"]
            video_data = b"".join(frames) if frames else b""

            output_path = input.output_path or rec.get("output_path")
            if output_path and video_data:
                meta = await save_to_file(video_data, output_path)
                return format_json_response(
                    {
                        "path": meta["path"],
                        "duration_ms": duration_ms,
                        "size_bytes": meta["size_bytes"],
                    }
                )

            if video_data:
                b64 = encode_base64(video_data)
                return format_json_response(
                    {
                        "base64": b64,
                        "duration_ms": duration_ms,
                        "size_bytes": len(video_data),
                    }
                )

            return format_json_response(
                {
                    "duration_ms": duration_ms,
                    "size_bytes": 0,
                }
            )
        except Exception as e:
            return format_error("wavexis_video_stop", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def wavexis_video_add_chapter(input: VideoAddChapterInput) -> str:
        """Add a chapter marker to an active recording.

        Args:
            input: Chapter parameters (recording_id, title, timestamp_ms).

        Returns:
            JSON string with ``status`` and ``chapter`` info.
        """
        try:
            rec = recordings.get(input.recording_id)
            if rec is None:
                return format_error(
                    "wavexis_video_add_chapter",
                    RuntimeError(f"Recording {input.recording_id} not found"),
                )

            timestamp_ms = input.timestamp_ms
            if timestamp_ms is None:
                timestamp_ms = int((time.time() - rec["start_time"]) * 1000)

            chapter = {"title": input.title, "timestamp_ms": timestamp_ms}
            chapters: list[Any] = rec.get("chapters", [])
            chapters.append(chapter)
            rec["chapters"] = chapters

            return format_json_response(
                {
                    "status": "ok",
                    "chapter": chapter,
                }
            )
        except Exception as e:
            return format_error("wavexis_video_add_chapter", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def wavexis_video_action_overlay(input: VideoActionOverlayInput) -> str:
        """Enable or disable action overlay on the video recording.

        Args:
            input: Overlay parameters (show).

        Returns:
            JSON string with status ``"ok"`` and ``show``.
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.eval(f"window.__wavexisOverlay = {json.dumps(input.show)};")
            return format_json_response(
                {
                    "status": "ok",
                    "show": input.show,
                }
            )
        except Exception as e:
            return format_error("wavexis_video_action_overlay", e)
