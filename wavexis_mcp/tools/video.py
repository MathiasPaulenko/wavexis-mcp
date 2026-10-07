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

_OVERLAY_ENABLE_JS = """(function(){
if (window.__wavexisOverlayEl) { window.__wavexisOverlayEl.style.display='block'; return; }
var el = document.createElement('div');
el.id = '__wavexis_overlay';
el.style.cssText = 'position:fixed;bottom:12px;right:12px;z-index:2147483647;'
  + 'background:rgba(0,0,0,.75);color:#0f0;font:12px monospace;padding:6px 10px;'
  + 'border-radius:4px;pointer-events:none;opacity:0;transition:opacity .3s;';
document.documentElement.appendChild(el);
window.__wavexisOverlayEl = el;
function flash(text){
  el.textContent = text;
  el.style.opacity = '1';
  clearTimeout(window.__wavexisOverlayTimer);
  window.__wavexisOverlayTimer = setTimeout(function(){ el.style.opacity='0'; }, 1200);
}
window.__wavexisOverlayFlash = flash;
document.addEventListener('click', function(e){
  var t = e.target; var name = (t.tagName||'') + (t.id ? '#'+t.id : '');
  flash('click ' + name);
}, true);
document.addEventListener('keydown', function(e){ flash('key ' + e.key); }, true);
document.addEventListener('input', function(e){
  var t = e.target; var name = (t.name||t.id||t.tagName||'');
  flash('input ' + name);
}, true);
})()"""

_OVERLAY_DISABLE_JS = """(function(){
var el = window.__wavexisOverlayEl;
if (el && el.parentNode) { el.parentNode.removeChild(el); }
window.__wavexisOverlayEl = null;
})()"""


async def _append_frame(
    recording: dict[str, Any],
    total_ref: list[int],
    data: str,
) -> None:
    """Decode and append a screencast frame to *recording* under the lock."""
    if recording.get("_stopped"):
        return
    try:
        decoded = base64.b64decode(data)
    except Exception:
        _logger.exception("Failed to decode screencast frame")
        return
    async with _recordings_lock:
        if recording.get("_stopped"):
            return
        if total_ref[0] >= _MAX_TOTAL_FRAMES:
            return
        frames = recording.get("frames", [])
        if len(frames) >= _MAX_FRAMES_PER_RECORDING:
            return
        frames.append(decoded)
        total_ref[0] += 1


async def _ack_frame(target: Any, session_id: int) -> None:
    """Send ``Page.screencastFrameAck`` so Chrome keeps emitting frames."""
    send = getattr(target, "send", None) or getattr(target, "send_command", None)
    if send is not None:
        with contextlib.suppress(Exception):
            result = send("Page.screencastFrameAck", {"sessionId": session_id})
            if inspect.isawaitable(result):
                await result


def _make_frame_handler(
    recording: dict[str, Any],
    total_ref: list[int],
    target: Any,
) -> Any:
    """Create a CDP ``Page.screencastFrame`` handler for *recording*."""

    def handler(params: Any) -> None:
        """Decode, store, and ack a screencast frame while respecting limits."""
        data = params.get("data") if isinstance(params, dict) else None
        if not data:
            return
        session_id = params.get("sessionId", 0)
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            _logger.warning("No running event loop; dropping screencast frame")
            return

        async def _process() -> None:
            # Ack must be sent regardless of whether the frame was kept —
            # Chrome stops emitting frames until each one is acked.
            await _ack_frame(target, session_id)
            await _append_frame(recording, total_ref, data)

        future = asyncio.run_coroutine_threadsafe(_process(), loop)
        future.add_done_callback(
            lambda f: (
                _logger.exception("Frame append failed: %s", f.exception())
                if f.exception()
                else None
            )
        )

    return handler


async def _attach_screencast_handler(
    backend: Any,
    recording: dict[str, Any],
    total_ref: list[int],
) -> bool:
    """Attach a ``Page.screencastFrame`` listener to the backend if possible.

    CDP backends expose the event through the CDP session.  BiDi backends
    expose it through the CDP bridge on the BiDi client.  Returns ``False``
    when no event-capable target exists — callers must not pretend a
    recording is running in that case.
    """
    target: Any | None = None

    require_session = getattr(backend, "_require_session", None)
    if require_session is not None:
        try:
            target = require_session()
            if inspect.isawaitable(target):
                target = await target
        except Exception:
            target = None

    if target is None:
        require_launched = getattr(backend, "_require_launched", None)
        if require_launched is not None:
            try:
                client = require_launched()
                if inspect.isawaitable(client):
                    client = await client
            except Exception:
                client = None
            if client is not None:
                target = getattr(client, "cdp", None)

    if target is None or not hasattr(target, "on") or not hasattr(target, "off"):
        return False

    handler = _make_frame_handler(recording, total_ref, target)
    try:
        res = target.on("Page.screencastFrame", handler)
        if inspect.isawaitable(res):
            await res
        recording["_screencast_target"] = target
        recording["_screencast_handler"] = handler
        return True
    except Exception:
        return False


async def _detach_screencast_handler(recording: dict[str, Any]) -> None:
    """Detach the screencast frame handler if one was attached."""
    target = recording.pop("_screencast_target", None)
    handler = recording.pop("_screencast_handler", None)
    if target is not None and handler is not None:
        with contextlib.suppress(Exception):
            res = target.off("Page.screencastFrame", handler)
            if inspect.isawaitable(res):
                await res


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
                "_stopped": False,
            }

            # Attach the frame listener before starting the screencast so the
            # first frame is not lost.
            if not await _attach_screencast_handler(session.backend, recording, total_frames):
                return format_error(
                    "wavexis_video_record",
                    RuntimeError(
                        "Frame capture requires a backend that exposes CDP event "
                        "subscriptions (CDP backend, or BiDi with a CDP bridge)."
                    ),
                )

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
                    recordings[oldest]["_stopped"] = True
                    oldest_rec = recordings.pop(oldest)
                    await _detach_screencast_handler(oldest_rec)
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
        """Stop recording and return the captured frames as an MJPEG stream.

        The output is a Motion JPEG stream (concatenated JPEG frames) — a
        format playable by VLC/ffmpeg and encodable to mp4/webm.  It is not
        a containerized mp4/webm.

        Args:
            input: Stop parameters (recording_id, output_path).

        Returns:
            JSON string with ``base64`` MJPEG data or file ``path``,
            plus ``duration_ms``, ``size_bytes``, ``frames``, ``format``
            and ``chapters``.
        """
        try:
            session = session_manager.get(input.session_id)

            stop = getattr(session.backend, "page_stop_screencast", None)
            if stop is not None:
                await stop()
            else:
                await session.backend.raw("Page.stopScreencast", {})

            async with _recordings_lock:
                if input.recording_id:
                    recording_id = input.recording_id if input.recording_id in recordings else None
                else:
                    # Most recent recording for this session wins.
                    candidates = [
                        (rid, rec)
                        for rid, rec in recordings.items()
                        if rec["session_id"] == input.session_id
                    ]
                    recording_id = (
                        max(candidates, key=lambda kv: kv[1]["start_time"])[0]
                        if candidates
                        else None
                    )
                if recording_id is None:
                    return format_error(
                        "wavexis_video_stop",
                        RuntimeError("No active recording for this session"),
                    )

                rec = recordings.pop(recording_id)
                rec["_stopped"] = True
                total_frames[0] -= len(rec.get("frames", []))
                await _detach_screencast_handler(rec)
            start_time = rec["start_time"]
            duration_ms = int((time.time() - start_time) * 1000)

            frames = rec["frames"]
            video_data = b"".join(frames) if frames else b""
            chapters = rec.get("chapters", [])

            output_path = input.output_path or rec.get("output_path")
            if output_path and video_data:
                meta = await save_to_file(video_data, output_path)
                return format_json_response(
                    {
                        "path": meta["path"],
                        "format": "mjpeg",
                        "recording_id": recording_id,
                        "frames": len(frames),
                        "chapters": chapters,
                        "duration_ms": duration_ms,
                        "size_bytes": meta["size_bytes"],
                    }
                )

            if video_data:
                b64 = encode_base64(video_data)
                return format_json_response(
                    {
                        "base64": b64,
                        "format": "mjpeg",
                        "recording_id": recording_id,
                        "frames": len(frames),
                        "chapters": chapters,
                        "duration_ms": duration_ms,
                        "size_bytes": len(video_data),
                    }
                )

            return format_json_response(
                {
                    "format": "mjpeg",
                    "recording_id": recording_id,
                    "frames": 0,
                    "chapters": chapters,
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
            async with _recordings_lock:
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
        """Enable or disable the on-page action overlay for recordings.

        When enabled, a small fixed badge is injected into the page that
        flashes the last user action (click, keypress, input) so it is
        visible in captured screencast frames.

        Args:
            input: Overlay parameters (show).

        Returns:
            JSON string with status ``"ok"`` and ``show``.
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.eval(
                _OVERLAY_ENABLE_JS if input.show else _OVERLAY_DISABLE_JS,
                await_promise=False,
            )
            return format_json_response(
                {
                    "status": "ok",
                    "show": input.show,
                }
            )
        except Exception as e:
            return format_error("wavexis_video_action_overlay", e)
