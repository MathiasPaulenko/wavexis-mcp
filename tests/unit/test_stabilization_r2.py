"""Regression tests for the second stabilization pass.

Covers: check/uncheck state semantics, scrape CSV output, console
message totals, per-subscription event logs, Chrome process cleanup
on failed opens, session closing races via the backend proxy, video
recording lifecycle, bluetooth validation, crawl URL validation,
CLI port validation, and ephemeral backend global config parity.
"""

from __future__ import annotations

import asyncio
import json
import time
import uuid
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from mcp.server.fastmcp import FastMCP
from pydantic import ValidationError

from wavexis_mcp.models import (
    BluetoothAdapterStateInput,
    BrowserVersionInput,
    CheckInput,
    ConsoleMessagesInput,
    CrawlInput,
    ScrapeInput,
    SubscribeEventsInput,
    UnsubscribeEventsInput,
    VideoAddChapterInput,
    VideoRecordInput,
    VideoStopInput,
)
from wavexis_mcp.session import BrowserSession, SessionManager


def _session_id(mgr: SessionManager) -> str:
    return next(iter(mgr._sessions))


@pytest.mark.unit
class TestCheckUncheckSemantics:
    """wavexis_check/uncheck must enforce state, not blindly toggle."""

    def _tool(self, mgr: SessionManager, name: str) -> Any:
        from wavexis_mcp.tools.input import register

        mcp = FastMCP("test")
        register(mcp, mgr)
        return mcp._tool_manager.get_tool(name)

    async def test_check_does_not_click_when_already_checked(
        self, session_manager_with_mock: SessionManager, mock_backend: AsyncMock
    ) -> None:
        mock_backend.eval = AsyncMock(return_value=True)
        sid = _session_id(session_manager_with_mock)
        tool = self._tool(session_manager_with_mock, "wavexis_check")

        result = json.loads(await tool.fn(CheckInput(selector="#cb", session_id=sid)))

        assert result["status"] == "ok"
        assert result["checked"] is True
        mock_backend.click.assert_not_awaited()

    async def test_check_clicks_when_unchecked(
        self, session_manager_with_mock: SessionManager, mock_backend: AsyncMock
    ) -> None:
        state = {"checked": False}

        async def _eval(expr: str, **kwargs: Any) -> bool:
            return state["checked"]

        async def _click(sel: str) -> None:
            state["checked"] = True

        mock_backend.eval = AsyncMock(side_effect=_eval)
        mock_backend.click = AsyncMock(side_effect=_click)
        sid = _session_id(session_manager_with_mock)
        tool = self._tool(session_manager_with_mock, "wavexis_check")

        result = json.loads(await tool.fn(CheckInput(selector="#cb", session_id=sid)))

        assert result["status"] == "ok"
        assert result["checked"] is True
        mock_backend.click.assert_awaited_once()

    async def test_uncheck_does_not_click_when_already_unchecked(
        self, session_manager_with_mock: SessionManager, mock_backend: AsyncMock
    ) -> None:
        mock_backend.eval = AsyncMock(return_value=False)
        sid = _session_id(session_manager_with_mock)
        tool = self._tool(session_manager_with_mock, "wavexis_uncheck")

        result = json.loads(await tool.fn(CheckInput(selector="#cb", session_id=sid)))

        assert result["status"] == "ok"
        assert result["checked"] is False
        mock_backend.click.assert_not_awaited()

    async def test_uncheck_clicks_when_checked(
        self, session_manager_with_mock: SessionManager, mock_backend: AsyncMock
    ) -> None:
        state = {"checked": True}

        async def _eval(expr: str, **kwargs: Any) -> bool:
            return state["checked"]

        async def _click(sel: str) -> None:
            state["checked"] = False

        mock_backend.eval = AsyncMock(side_effect=_eval)
        mock_backend.click = AsyncMock(side_effect=_click)
        sid = _session_id(session_manager_with_mock)
        tool = self._tool(session_manager_with_mock, "wavexis_uncheck")

        result = json.loads(await tool.fn(CheckInput(selector="#cb", session_id=sid)))

        assert result["status"] == "ok"
        assert result["checked"] is False
        mock_backend.click.assert_awaited_once()


@pytest.mark.unit
async def test_scrape_csv_output(session_manager_with_mock: SessionManager) -> None:
    """output_format='csv' produces CSV text instead of a JSON list."""
    from wavexis_mcp.tools.capture import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)
    tool = mcp._tool_manager.get_tool("wavexis_scrape")

    sid = _session_id(session_manager_with_mock)
    result = await tool.fn(
        ScrapeInput(
            urls=["https://a.example", "https://b.example"],
            session_id=sid,
            output_format="csv",
        )
    )
    data = json.loads(result)
    assert data["format"] == "csv"
    assert "csv" in data
    lines = data["csv"].strip().splitlines()
    assert lines[0] == "url,data"
    assert len(lines) == 3


@pytest.mark.unit
async def test_console_messages_total_not_truncated(
    session_manager_with_mock: SessionManager, mock_backend: AsyncMock
) -> None:
    """`total` must reflect the full message count, not the truncated page."""
    from wavexis_mcp.tools.devtools import register

    mock_backend.capture_console = AsyncMock(
        return_value=[{"level": "info", "text": f"m{i}"} for i in range(10)]
    )
    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)
    tool = mcp._tool_manager.get_tool("wavexis_console_messages")

    sid = _session_id(session_manager_with_mock)
    result = await tool.fn(ConsoleMessagesInput(session_id=sid, all=False, limit=3, offset=0))
    data = json.loads(result)
    assert data["total"] == 10
    assert data["count"] == 3


@pytest.mark.unit
class TestEventSubscriptionIsolation:
    """Concurrent subscriptions must keep independent event buffers."""

    async def test_unsubscribe_drains_only_own_buffer(
        self, session_manager_with_mock: SessionManager, mock_backend: AsyncMock
    ) -> None:
        from wavexis_mcp.tools.devtools import register

        callbacks: list[Any] = []
        counter = {"n": 0}

        async def _subscribe(types: list[str], callback: Any) -> str:
            counter["n"] += 1
            callbacks.append(callback)
            return f"sub-{counter['n']}"

        mock_backend.subscribe_events = AsyncMock(side_effect=_subscribe)
        mock_backend.unsubscribe_events = AsyncMock()

        mcp = FastMCP("test")
        register(mcp, session_manager_with_mock)
        sid = _session_id(session_manager_with_mock)

        sub_tool = mcp._tool_manager.get_tool("wavexis_subscribe_events")
        unsub_tool = mcp._tool_manager.get_tool("wavexis_unsubscribe_events")

        sub_inp = SubscribeEventsInput(session_id=sid, event_types=["console"])
        r1 = json.loads(await sub_tool.fn(sub_inp))
        r2 = json.loads(await sub_tool.fn(sub_inp))
        sub1, sub2 = r1["subscription_id"], r2["subscription_id"]

        # Feed an event to each subscription's callback.
        callbacks[0]({"type": "console", "text": "for-sub-1"})
        callbacks[1]({"type": "console", "text": "for-sub-2"})

        out1 = json.loads(
            await unsub_tool.fn(UnsubscribeEventsInput(session_id=sid, subscription_id=sub1))
        )
        out2 = json.loads(
            await unsub_tool.fn(UnsubscribeEventsInput(session_id=sid, subscription_id=sub2))
        )

        assert [e["text"] for e in out1["events"]] == ["for-sub-1"]
        assert [e["text"] for e in out2["events"]] == ["for-sub-2"]


@pytest.mark.unit
class TestChromeProcessCleanup:
    """A Chrome process launched by connect_existing must never leak."""

    async def test_chrome_terminated_when_backend_launch_fails(
        self, mock_backend: AsyncMock
    ) -> None:
        mgr = SessionManager()
        mock_proc = MagicMock()
        mock_proc.terminate = MagicMock()
        mock_proc.wait = AsyncMock()
        mock_backend.launch = AsyncMock(side_effect=RuntimeError("launch failed"))
        mgr._backend_manager.select = MagicMock(return_value=mock_backend)

        with (
            patch("wavexis_mcp.session._find_free_debug_port", return_value=9223),
            patch(
                "wavexis_mcp.session._launch_chrome_with_debug_port",
                new_callable=AsyncMock,
                return_value=mock_proc,
            ),
            pytest.raises(RuntimeError, match="launch failed"),
        ):
            await mgr.open(backend="cdp", connect_existing=True)

        mock_proc.terminate.assert_called_once()

    async def test_chrome_terminated_when_shutting_down(self, mock_backend: AsyncMock) -> None:
        mgr = SessionManager()
        mgr._shutting_down = True
        mock_proc = MagicMock()
        mock_proc.terminate = MagicMock()
        mock_proc.wait = AsyncMock()

        with (
            patch("wavexis_mcp.session._find_free_debug_port", return_value=9223),
            patch(
                "wavexis_mcp.session._launch_chrome_with_debug_port",
                new_callable=AsyncMock,
                return_value=mock_proc,
            ),
            pytest.raises(RuntimeError, match="shutting down"),
        ):
            await mgr.open(backend="cdp", connect_existing=True)

        mock_proc.terminate.assert_called_once()


@pytest.mark.unit
class TestSessionCloseRaces:
    """close() must wait for in-flight backend calls and reject new ones."""

    class _FakeBackend:
        """Minimal async backend (not an AsyncMock) so the proxy wraps it."""

        def __init__(self) -> None:
            self.slow_started = asyncio.Event()
            self.slow_finished = asyncio.Event()
            self.closed = False

        async def slow_op(self) -> str:
            self.slow_started.set()
            await asyncio.sleep(0.2)
            self.slow_finished.set()
            return "done"

        async def close(self) -> None:
            self.closed = True

    def _manager_with_fake(self) -> tuple[SessionManager, str, Any]:
        mgr = SessionManager()
        sid = str(uuid.uuid4())
        backend = self._FakeBackend()
        mgr._sessions[sid] = BrowserSession(
            session_id=sid,
            backend=backend,  # type: ignore[arg-type]
            backend_name="cdp",
            created_at=time.time(),
        )
        return mgr, sid, backend

    async def test_close_waits_for_inflight_proxy_call(self) -> None:
        mgr, sid, backend = self._manager_with_fake()
        session = mgr.get(sid)

        call = asyncio.ensure_future(session.backend.slow_op())
        await backend.slow_started.wait()

        await mgr.close(sid)
        result = await call

        assert result == "done"
        assert backend.slow_finished.is_set()
        assert backend.closed is True

    async def test_call_on_closing_session_is_rejected(self) -> None:
        mgr, sid, backend = self._manager_with_fake()
        session = mgr.get(sid)

        # Start a close while an op is in flight.
        call = asyncio.ensure_future(session.backend.slow_op())
        await backend.slow_started.wait()
        close_task = asyncio.ensure_future(mgr.close(sid))
        # Let close() mark the session as closing before the second call.
        await asyncio.sleep(0)

        # A second call started after close began must be rejected.
        from wavexis_mcp.errors import SessionNotFoundError

        with pytest.raises(SessionNotFoundError):
            await session.backend.slow_op()

        await call
        await close_task

    async def test_get_rejects_closing_session(self) -> None:
        mgr, sid, backend = self._manager_with_fake()
        session = mgr.get(sid)

        call = asyncio.ensure_future(session.backend.slow_op())
        await backend.slow_started.wait()
        close_task = asyncio.ensure_future(mgr.close(sid))
        await asyncio.sleep(0.05)

        from wavexis_mcp.errors import SessionNotFoundError

        with pytest.raises(SessionNotFoundError):
            mgr.get(sid)
        with pytest.raises(SessionNotFoundError):
            await mgr.acquire_backend(sid)

        await call
        await close_task


@pytest.mark.unit
class TestVideoLifecycle:
    async def test_record_detaches_handler_when_start_fails(
        self, session_manager_with_mock: SessionManager, mock_backend: AsyncMock
    ) -> None:
        from wavexis_mcp.tools.video import register

        recordings: dict[str, Any] = {}
        mcp = FastMCP("test")
        register(mcp, session_manager_with_mock, recordings)

        target = MagicMock()
        mock_backend._require_session = MagicMock(return_value=target)
        mock_backend.page_start_screencast = AsyncMock(side_effect=RuntimeError("no screencast"))

        sid = _session_id(session_manager_with_mock)
        tool = mcp._tool_manager.get_tool("wavexis_video_record")
        result = json.loads(await tool.fn(VideoRecordInput(session_id=sid)))

        assert "error" in result
        assert not recordings
        target.off.assert_called_with("Page.screencastFrame", target.on.call_args[0][1])

    async def test_stop_without_recording_does_not_stop_screencast(
        self, session_manager_with_mock: SessionManager, mock_backend: AsyncMock
    ) -> None:
        from wavexis_mcp.tools.video import register

        recordings: dict[str, Any] = {}
        mcp = FastMCP("test")
        register(mcp, session_manager_with_mock, recordings)

        mock_backend.page_stop_screencast = AsyncMock()
        sid = _session_id(session_manager_with_mock)
        tool = mcp._tool_manager.get_tool("wavexis_video_stop")
        result = json.loads(await tool.fn(VideoStopInput(session_id=sid)))

        assert "error" in result
        mock_backend.page_stop_screencast.assert_not_awaited()
        for c in mock_backend.raw.await_args_list:
            assert c.args[0] != "Page.stopScreencast"

    async def test_chapter_limit_enforced(
        self, session_manager_with_mock: SessionManager, mock_backend: AsyncMock
    ) -> None:
        from wavexis_mcp.tools.video import register

        recordings: dict[str, Any] = {}
        mcp = FastMCP("test")
        register(mcp, session_manager_with_mock, recordings)

        sid = _session_id(session_manager_with_mock)
        rec_id = "rec-full"
        recordings[rec_id] = {
            "session_id": sid,
            "start_time": time.time(),
            "frames": [],
            "chapters": [{"title": f"ch{i}", "timestamp_ms": i} for i in range(500)],
            "_stopped": False,
        }
        tool = mcp._tool_manager.get_tool("wavexis_video_add_chapter")
        result = json.loads(
            await tool.fn(
                VideoAddChapterInput(session_id=sid, recording_id=rec_id, title="one more")
            )
        )
        assert "error" in result
        assert len(recordings[rec_id]["chapters"]) == 500


@pytest.mark.unit
def test_bluetooth_state_pattern() -> None:
    with pytest.raises(ValidationError):
        BluetoothAdapterStateInput(session_id="s", state="bogus")
    ok = BluetoothAdapterStateInput(session_id="s", state="powered-on")
    assert ok.state == "powered-on"


@pytest.mark.unit
async def test_crawl_rejects_invalid_start_url(
    session_manager_with_mock: SessionManager,
) -> None:
    from wavexis_mcp.tools.data import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)
    tool = mcp._tool_manager.get_tool("wavexis_crawl")

    result = await tool.fn(CrawlInput(start_url="javascript:alert(1)"))
    data = json.loads(result)
    assert "error" in data


@pytest.mark.unit
def test_main_rejects_invalid_port(capsys: Any) -> None:
    from wavexis_mcp.server import main

    with pytest.raises(SystemExit) as exc:
        main(["--port", "0"])
    assert exc.value.code == 2
    with pytest.raises(SystemExit):
        main(["--port", "70000"])


@pytest.mark.unit
async def test_browser_version_reports_session_backend(
    session_manager_with_mock: SessionManager,
) -> None:
    """A session must report its own backend name, not the request's."""
    from wavexis_mcp.tools.utility import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)
    tool = mcp._tool_manager.get_tool("wavexis_browser_version")

    sid = _session_id(session_manager_with_mock)
    result = await tool.fn(BrowserVersionInput(session_id=sid, backend="bidi"))
    data = json.loads(result)
    assert data["backend"] == "cdp"


@pytest.mark.unit
async def test_ephemeral_acquire_applies_blocked_origins(mock_backend: AsyncMock) -> None:
    """--blocked-origins must apply to stateless backends, not only sessions."""
    mgr = SessionManager()
    mgr.blocked_origins = ["*.ads.example.com"]
    mgr._backend_manager.select = MagicMock(return_value=mock_backend)

    backend, sid = await mgr.acquire_backend(None)
    try:
        mock_backend.block_requests.assert_awaited_once_with(["*.ads.example.com"])
    finally:
        await mgr.release_backend(backend, sid)


@pytest.mark.unit
def test_secure_output_path_rejects_windows_device_names(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Any
) -> None:
    """NUL/CON/COM1 must be rejected — they open device handles on Windows."""
    import wavexis_mcp.formatter as fmt

    if fmt.os.name != "nt":
        pytest.skip("Windows-specific device-name check")
    monkeypatch.setenv("WAVEXIS_MCP_OUTPUT_DIR", str(tmp_path))
    monkeypatch.setattr(fmt.os, "name", "nt")
    for name in ("NUL", "con.txt", "COM1", "lpt3"):
        with pytest.raises(ValueError, match="device"):
            fmt.secure_output_path(name)


@pytest.mark.unit
async def test_a11y_snapshot_navigates_within_session(
    session_manager_with_mock: SessionManager, mock_backend: AsyncMock
) -> None:
    """Passing url + session_id must navigate the session (parity with capture tools)."""
    from wavexis_mcp.models import A11ySnapshotInput
    from wavexis_mcp.tools.a11y import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)
    tool = mcp._tool_manager.get_tool("wavexis_a11y_snapshot")

    sid = _session_id(session_manager_with_mock)
    result = await tool.fn(A11ySnapshotInput(session_id=sid, url="https://example.com"))
    data = json.loads(result)
    assert data["status"] == "ok"
    mock_backend.navigate.assert_awaited_once()


@pytest.mark.unit
async def test_network_log_subscribed_once_under_concurrency(
    session_manager_with_mock: SessionManager, mock_backend: AsyncMock
) -> None:
    """Concurrent _ensure_network_log calls must subscribe only once."""
    from wavexis_mcp.tools.network import _ensure_network_log

    mock_backend.subscribe_events = AsyncMock(return_value="sub-1")
    session = session_manager_with_mock.get(_session_id(session_manager_with_mock))

    await asyncio.gather(*[_ensure_network_log(session) for _ in range(5)])
    mock_backend.subscribe_events.assert_awaited_once()
