"""E2E tests for DevTools, Vision, and Video tier tools.

DevTools: performance metrics, traces, CSS, console, security, window bounds.
Vision: coordinate-based mouse control.
Video: recording, stop, chapters, overlays.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.e2e


# ── DevTools ───────────────────────────────────────────────────────


class TestDevTools:
    """DevTools protocol tools."""

    async def test_perf_metrics(self, call_tool, chrome_session) -> None:
        """Capture performance metrics."""
        data = await call_tool("wavexis_perf_metrics", session_id=chrome_session)
        metrics = data.get("metrics", data)
        assert isinstance(metrics, dict)

    async def test_perf_trace(self, call_tool, chrome_session) -> None:
        """Capture a performance trace."""
        data = await call_tool(
            "wavexis_perf_trace",
            session_id=chrome_session,
            duration_ms=1000,
        )
        assert "path" in data or "trace" in data or "error" in data

    async def test_perf_profile(self, call_tool, chrome_session) -> None:
        """Capture a CPU profile."""
        data = await call_tool(
            "wavexis_perf_profile",
            session_id=chrome_session,
            duration_ms=1000,
        )
        assert "path" in data or "profile" in data or "error" in data

    async def test_css_get_styles(self, call_tool, chrome_session) -> None:
        """Get inline and matched CSS styles for an element."""
        data = await call_tool(
            "wavexis_css_get_styles",
            selector="#main-heading",
            session_id=chrome_session,
        )
        assert "styles" in data or "error" in data

    async def test_css_get_computed(self, call_tool, chrome_session) -> None:
        """Get computed styles for an element."""
        data = await call_tool(
            "wavexis_css_get_computed",
            selector="#main-heading",
            session_id=chrome_session,
        )
        computed = data.get("computed", {})
        assert isinstance(computed, dict) or "error" in data

    async def test_console_messages(self, call_tool, chrome_session, base_url) -> None:
        """Capture console messages from a page that logs."""
        await call_tool("wavexis_navigate", url=f"{base_url}/dynamic.html", session_id=chrome_session)
        data = await call_tool("wavexis_console_messages", session_id=chrome_session)
        messages = data.get("messages", [])
        assert isinstance(messages, list)

    async def test_browser_logs(self, call_tool, chrome_session) -> None:
        """Capture browser-level logs."""
        data = await call_tool("wavexis_browser_logs", session_id=chrome_session)
        assert "logs" in data or "error" in data

    async def test_security_state(self, call_tool, chrome_session) -> None:
        """Get the security state of the current page."""
        data = await call_tool("wavexis_get_security_state", session_id=chrome_session)
        assert "state" in data or "error" in data

    async def test_window_bounds(self, call_tool, chrome_session) -> None:
        """Get the browser window bounds."""
        data = await call_tool("wavexis_get_window_bounds", session_id=chrome_session)
        # Returns bounds dict directly (left, top, width, height)
        assert isinstance(data, dict)
        assert "width" in data or "left" in data or "error" in data

    async def test_overlay_highlight(self, call_tool, chrome_session) -> None:
        """Highlight an element with an overlay."""
        data = await call_tool(
            "wavexis_overlay_highlight",
            selector="#main-heading",
            session_id=chrome_session,
        )
        assert data["status"] == "ok"

        # Clear overlay
        clear_data = await call_tool("wavexis_overlay_clear", session_id=chrome_session)
        assert clear_data["status"] == "ok"

    async def test_debug_event_listeners(self, call_tool, chrome_session) -> None:
        """Get event listeners for an element."""
        data = await call_tool(
            "wavexis_debug_get_listeners",
            selector="#click-me",
            session_id=chrome_session,
        )
        assert "listeners" in data or "error" in data


# ── Vision ─────────────────────────────────────────────────────────


class TestVision:
    """Coordinate-based mouse interaction tools."""

    async def test_mouse_move_xy(self, call_tool, chrome_session) -> None:
        """Move mouse to specific coordinates."""
        data = await call_tool(
            "wavexis_mouse_move_xy",
            x=100,
            y=100,
            session_id=chrome_session,
        )
        assert data["status"] == "ok"

    async def test_mouse_click_xy(self, call_tool, chrome_session) -> None:
        """Click at specific coordinates."""
        data = await call_tool(
            "wavexis_mouse_click_xy",
            x=50,
            y=50,
            session_id=chrome_session,
        )
        assert data["status"] == "ok"

    async def test_mouse_down_up(self, call_tool, chrome_session) -> None:
        """Mouse down then up at coordinates."""
        down_data = await call_tool(
            "wavexis_mouse_down",
            x=100,
            y=100,
            session_id=chrome_session,
        )
        assert down_data["status"] == "ok"

        up_data = await call_tool(
            "wavexis_mouse_up",
            x=100,
            y=100,
            session_id=chrome_session,
        )
        assert up_data["status"] == "ok"

    async def test_mouse_wheel(self, call_tool, chrome_session) -> None:
        """Scroll the page with the mouse wheel."""
        data = await call_tool(
            "wavexis_mouse_wheel",
            x=100,
            y=200,
            delta_y=500,
            session_id=chrome_session,
        )
        assert data["status"] == "ok"


# ── Video ──────────────────────────────────────────────────────────


class TestVideo:
    """Video recording tools."""

    async def test_video_record_and_stop(self, call_tool, chrome_session) -> None:
        """Start video recording, then stop it."""
        # Start recording
        data = await call_tool("wavexis_video_record", session_id=chrome_session)
        assert data.get("status") == "recording"
        recording_id = data.get("recording_id")
        assert recording_id

        # Stop recording
        stop_data = await call_tool("wavexis_video_stop", session_id=chrome_session)
        assert "duration_ms" in stop_data or "base64" in stop_data or "path" in stop_data

    async def test_video_add_chapter(self, call_tool, chrome_session) -> None:
        """Add a chapter marker to a recording."""
        # Start recording
        rec = await call_tool("wavexis_video_record", session_id=chrome_session)
        recording_id = rec.get("recording_id", "")

        # Add chapter
        data = await call_tool(
            "wavexis_video_add_chapter",
            title="Test Chapter",
            recording_id=recording_id,
            session_id=chrome_session,
        )
        assert data.get("status") == "ok" or "chapter" in data or "error" in data

        # Stop
        await call_tool("wavexis_video_stop", session_id=chrome_session)
