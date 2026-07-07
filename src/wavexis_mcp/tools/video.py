"""Video recording tools for WaveXisMCP.

Provides tools for starting and stopping video recordings, adding
chapter markers, and toggling action overlays.  All tools require
an active session.
"""

from __future__ import annotations

import time
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

_recordings: dict[str, dict[str, Any]] = {}


def register(mcp: FastMCP, session_manager: SessionManager) -> None:
    """Register all video tools on the FastMCP server.

    Args:
        mcp: The FastMCP server instance.
        session_manager: The shared session manager.
    """

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=False,
        openWorldHint=True,
    ))
    async def wavexis_video_record(input: VideoRecordInput) -> str:
        """Start recording a video of the page.

        Args:
            input: Recording parameters (output_path, width, height).

        Returns:
            JSON string with ``recording_id`` and ``status``.
        """
        try:
            session = session_manager.get(input.session_id)
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
            recording_id = f"rec-{int(time.time() * 1000)}"
            _recordings[recording_id] = {
                "session_id": input.session_id,
                "start_time": time.time(),
                "output_path": input.output_path,
                "frames": [],
            }
            return format_json_response({
                "recording_id": recording_id,
                "status": "recording",
            })
        except Exception as e:
            return format_error("wavexis_video_record", e)

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=False,
        openWorldHint=True,
    ))
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
            await session.backend.raw("Page.stopScreencast", {})

            recording_id = next(
                (rid for rid, rec in _recordings.items()
                 if rec["session_id"] == input.session_id),
                None,
            )
            if recording_id is None:
                return format_error(
                    "wavexis_video_stop",
                    RuntimeError("No active recording for this session"),
                )

            rec = _recordings.pop(recording_id)
            start_time = rec["start_time"]
            duration_ms = int((time.time() - start_time) * 1000)

            frames = rec["frames"]
            video_data = b"".join(frames) if frames else b""

            output_path = input.output_path or rec.get("output_path")
            if output_path and video_data:
                meta = save_to_file(video_data, output_path)
                return format_json_response({
                    "path": meta["path"],
                    "duration_ms": duration_ms,
                    "size_bytes": meta["size_bytes"],
                })

            if video_data:
                b64 = encode_base64(video_data)
                return format_json_response({
                    "base64": b64,
                    "duration_ms": duration_ms,
                    "size_bytes": len(video_data),
                })

            return format_json_response({
                "duration_ms": duration_ms,
                "size_bytes": 0,
            })
        except Exception as e:
            return format_error("wavexis_video_stop", e)

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ))
    async def wavexis_video_add_chapter(input: VideoAddChapterInput) -> str:
        """Add a chapter marker to an active recording.

        Args:
            input: Chapter parameters (recording_id, title, timestamp_ms).

        Returns:
            JSON string with ``status`` and ``chapter`` info.
        """
        try:
            rec = _recordings.get(input.recording_id)
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

            return format_json_response({
                "status": "ok",
                "chapter": chapter,
            })
        except Exception as e:
            return format_error("wavexis_video_add_chapter", e)

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ))
    async def wavexis_video_action_overlay(input: VideoActionOverlayInput) -> str:
        """Enable or disable action overlay on the video recording.

        Args:
            input: Overlay parameters (show).

        Returns:
            JSON string with status ``"ok"`` and ``show``.
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.eval(
                f"window.__wavexisOverlay = {'true' if input.show else 'false'};"
            )
            return format_json_response({
                "status": "ok",
                "show": input.show,
            })
        except Exception as e:
            return format_error("wavexis_video_action_overlay", e)
