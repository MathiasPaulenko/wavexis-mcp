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

from wavexis_mcp.session import SessionManager

logger = logging.getLogger(__name__)

_POLL_INTERVAL_S = 0.5


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

        # Try W11 subscribe_events first
        subscribe = getattr(session.backend, "subscribe_events", None)
        if subscribe is not None:
            try:
                await subscribe(event_types)
                return stream_id
            except Exception:
                logger.warning("subscribe_events failed, falling back to polling")

        # Fallback: polling-based streaming
        if stream_id not in self._active:
            task = asyncio.create_task(self._poll_loop(session_id, event_types))
            self._active[stream_id] = task

        return stream_id

    async def stop_stream(self, session_id: str) -> None:
        """Stop streaming events for a session.

        Args:
            session_id: The session to stop streaming.
        """
        stream_id = f"stream-{session_id}"
        task = self._active.pop(stream_id, None)
        if task is not None:
            task.cancel()

        session = self._session_manager.get(session_id)
        unsubscribe = getattr(session.backend, "unsubscribe_events", None)
        if unsubscribe is not None:
            with contextlib.suppress(Exception):
                await unsubscribe()

    async def _poll_loop(
        self,
        session_id: str,
        event_types: list[str],
    ) -> None:
        """Poll the backend for events at a fixed interval.

        Args:
            session_id: The session to poll.
            event_types: Event types to collect.
        """
        last_console_count = 0
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
            except Exception:
                break
            await asyncio.sleep(_POLL_INTERVAL_S)

    async def stop_all(self) -> None:
        """Stop all active streaming tasks."""
        for stream_id in list(self._active.keys()):
            task = self._active.pop(stream_id, None)
            if task is not None:
                task.cancel()
