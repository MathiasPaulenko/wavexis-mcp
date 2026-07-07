"""Unit tests for WebSocket event streaming (M2)."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock

import pytest

from wavexis_mcp.session import SessionManager
from wavexis_mcp.streaming import StreamingHandler


@pytest.mark.unit
async def test_start_stream_with_subscribe(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    handler = StreamingHandler(session_manager_with_mock)
    session = session_manager_with_mock.get(mock_session_id)
    session.backend.subscribe_events = AsyncMock()
    session.backend.unsubscribe_events = AsyncMock()

    stream_id = await handler.start_stream(mock_session_id)
    assert stream_id == f"stream-{mock_session_id}"
    session.backend.subscribe_events.assert_awaited_once()


@pytest.mark.unit
async def test_start_stream_polling_fallback(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    handler = StreamingHandler(session_manager_with_mock)
    session = session_manager_with_mock.get(mock_session_id)
    session.backend.subscribe_events = AsyncMock(side_effect=RuntimeError("not supported"))

    stream_id = await handler.start_stream(mock_session_id)
    assert stream_id == f"stream-{mock_session_id}"

    await asyncio.sleep(0.1)
    await handler.stop_all()


@pytest.mark.unit
async def test_start_stream_no_subscribe_method(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    handler = StreamingHandler(session_manager_with_mock)
    session = session_manager_with_mock.get(mock_session_id)
    if hasattr(session.backend, "subscribe_events"):
        delattr(session.backend, "subscribe_events")

    stream_id = await handler.start_stream(mock_session_id, ["console"])
    assert stream_id == f"stream-{mock_session_id}"

    await asyncio.sleep(0.1)
    await handler.stop_all()


@pytest.mark.unit
async def test_stop_stream(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    handler = StreamingHandler(session_manager_with_mock)
    session = session_manager_with_mock.get(mock_session_id)
    session.backend.subscribe_events = AsyncMock(side_effect=RuntimeError("nope"))
    session.backend.unsubscribe_events = AsyncMock()

    await handler.start_stream(mock_session_id)
    await asyncio.sleep(0.1)
    await handler.stop_stream(mock_session_id)
    assert f"stream-{mock_session_id}" not in handler._active


@pytest.mark.unit
async def test_stop_stream_no_active_task(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    handler = StreamingHandler(session_manager_with_mock)
    session = session_manager_with_mock.get(mock_session_id)
    session.backend.unsubscribe_events = AsyncMock()

    await handler.stop_stream(mock_session_id)
    session.backend.unsubscribe_events.assert_awaited_once()


@pytest.mark.unit
async def test_stop_all(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    handler = StreamingHandler(session_manager_with_mock)
    session = session_manager_with_mock.get(mock_session_id)
    session.backend.subscribe_events = AsyncMock(side_effect=RuntimeError("nope"))

    await handler.start_stream(mock_session_id)
    await asyncio.sleep(0.1)
    assert len(handler._active) == 1

    await handler.stop_all()
    assert len(handler._active) == 0


@pytest.mark.unit
async def test_start_stream_invalid_session() -> None:
    from wavexis_mcp.errors import SessionNotFoundError

    mgr = SessionManager()
    handler = StreamingHandler(mgr)
    with pytest.raises(SessionNotFoundError):
        await handler.start_stream("nonexistent")


@pytest.mark.unit
async def test_poll_loop_breaks_on_error(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    handler = StreamingHandler(session_manager_with_mock)
    session = session_manager_with_mock.get(mock_session_id)
    session.backend.capture_console = AsyncMock(side_effect=RuntimeError("disconnected"))

    task = asyncio.create_task(handler._poll_loop(mock_session_id, ["console"]))
    await asyncio.sleep(0.2)
    assert task.done() or task.cancelled()
    if not task.done():
        task.cancel()
        with contextlib_suppress():
            await task


def contextlib_suppress():
    import contextlib
    return contextlib.suppress(asyncio.CancelledError)
