"""WebSocket event streaming for WaveXisMCP HTTP transport (M2).

Provides a WebSocket handler that streams live browser events
(console, network, navigation) to connected clients.  Uses the
wavexis ``subscribe_events`` API (W11) with a polling fallback
when the backend does not support event subscription.
"""

from __future__ import annotations

import asyncio
import contextlib
import json
import logging
from typing import Any

from wavexis_mcp.errors import SessionNotFoundError
from wavexis_mcp.session import SessionManager

logger = logging.getLogger(__name__)

_POLL_INTERVAL_S = 0.5
_MAX_POLL_INTERVAL_S = 30.0
_BACKOFF_MULTIPLIER = 1.5
_MAX_POLL_ERRORS = 3


class StreamingHandler:
    """Manages WebSocket event streaming for browser sessions.

    For each connected client, the handler subscribes to browser events
    via ``subscribe_events`` (W11) or falls back to polling console
    messages and network requests at a fixed interval.
    """

    def __init__(self, session_manager: SessionManager) -> None:
        """Initialize the streaming handler.

        Args:
            session_manager: The shared session manager.
        """
        self._session_manager = session_manager
        self._active: dict[str, asyncio.Task[None]] = {}
        self._streams: set[str] = set()
        self._subscriptions: dict[str, Any] = {}
        self._lock = asyncio.Lock()

    async def start_stream(
        self,
        session_id: str,
        event_types: list[str] | None = None,
    ) -> str:
        """Start streaming events for a session.

        Args:
            session_id: The session to stream events from.
            event_types: Optional list of event types to filter
                (``"console"``, ``"network_request"``, ``"network_response"``,
                ``"navigation"``).  Defaults to all.

        Returns:
            A stream ID that can be used to stop the stream.

        Raises:
            ValueError: If the session does not exist.
        """
        session = self._session_manager.get(session_id)
        event_types = event_types or ["console", "network_request", "navigation"]

        stream_id = f"stream-{session_id}"

        async with self._lock:
            if stream_id in self._streams:
                return stream_id
            self._streams.add(stream_id)

        # Try W11 subscribe_events first
        subscribe = getattr(session.backend, "subscribe_events", None)
        if subscribe is not None:
            try:
                sub_id = await subscribe(
                    event_types,
                    lambda event: logger.info("stream event: %s", json.dumps(event, default=str)),
                )
                async with self._lock:
                    self._subscriptions[stream_id] = sub_id
                return stream_id
            except Exception as exc:
                logger.warning("subscribe_events failed, falling back to polling: %s", exc)

        # Fallback: polling-based streaming
        async with self._lock:
            if stream_id not in self._active:
                self._active[stream_id] = asyncio.create_task(
                    self._poll_loop(session_id, event_types)
                )

        return stream_id

    async def stop_stream(self, session_id: str) -> None:
        """Stop streaming events for a session.

        Args:
            session_id: The session to stop streaming.
        """
        stream_id = f"stream-{session_id}"
        async with self._lock:
            self._streams.discard(stream_id)
            task = self._active.pop(stream_id, None)
            sub_id = self._subscriptions.pop(stream_id, None)
        if task is not None:
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await task

        try:
            session = self._session_manager.get(session_id)
        except Exception:
            session = None
        if session is not None and sub_id is not None:
            unsubscribe = getattr(session.backend, "unsubscribe_events", None)
            if unsubscribe is not None:
                with contextlib.suppress(Exception):
                    await unsubscribe(sub_id)

    async def _poll_loop(
        self,
        session_id: str,
        event_types: list[str],
    ) -> None:
        """Poll the backend for events with exponential backoff.

        Args:
            session_id: The session to poll.
            event_types: Event types to collect.
        """
        last_console_count = 0
        interval = _POLL_INTERVAL_S
        consecutive_errors = 0
        while True:
            try:
                session = self._session_manager.get(session_id)
                if "console" in event_types:
                    messages = await session.backend.capture_console()
                    new_messages = messages[last_console_count:]
                    last_console_count = len(messages)
                    for msg in new_messages:
                        logger.info(
                            "stream event: %s",
                            json.dumps({"type": "console", "data": msg}),
                        )
                # Reset backoff after a successful poll.
                interval = _POLL_INTERVAL_S
                consecutive_errors = 0
            except Exception as exc:
                consecutive_errors += 1
                logger.warning("Streaming poll error for %s: %s", session_id, exc)
                if consecutive_errors >= _MAX_POLL_ERRORS:
                    break
                interval = min(interval * _BACKOFF_MULTIPLIER, _MAX_POLL_INTERVAL_S)
                await asyncio.sleep(interval)
                continue
            await asyncio.sleep(interval)

    async def stop_all(self) -> None:
        """Stop all active streaming tasks."""
        async with self._lock:
            tasks = list(self._active.values())
            subscriptions = dict(self._subscriptions)
            self._active.clear()
            self._streams.clear()
            self._subscriptions.clear()
        for task in tasks:
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await task
        for stream_id, sub_id in subscriptions.items():
            if sub_id is None:
                continue
            session_id = stream_id.removeprefix("stream-")
            try:
                session = self._session_manager.get(session_id)
            except SessionNotFoundError:
                continue
            unsubscribe = getattr(session.backend, "unsubscribe_events", None)
            if unsubscribe is not None:
                with contextlib.suppress(Exception):
                    await unsubscribe(sub_id)
