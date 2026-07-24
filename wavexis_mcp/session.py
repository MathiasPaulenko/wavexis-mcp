"""Session management for WaveXisMCP.

Provides ``SessionManager`` and ``BrowserSession`` to support both
stateless (one-shot) and session-based (persistent browser) tool
execution.  The manager handles backend lifecycle, session lookup,
and ephemeral backend creation for stateless calls.
"""

from __future__ import annotations

import asyncio
import contextlib
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from wavexis.backend.base import AbstractBackend
from wavexis.backend.manager import BackendManager
from wavexis.config import BrowserOptions, WaitStrategy

from wavexis_mcp.errors import SessionNotFoundError

DEFAULT_BACKEND_TIMEOUT = 30.0


@dataclass
class BrowserSession:
    """A persistent browser session with an active backend.

    Attributes:
        session_id: Unique identifier for this session.
        backend: The wavexis backend instance.
        backend_name: Human-readable backend name (e.g. ``"cdp"``).
        created_at: Unix timestamp of session creation.
        last_used: Unix timestamp of last activity.
    """

    session_id: str
    backend: AbstractBackend
    backend_name: str
    created_at: float
    last_used: float = field(default_factory=time.time)


class SessionManager:
    """Manages browser sessions for stateful and stateless tool execution.

    Holds a registry of active ``BrowserSession`` objects and a
    ``BackendManager`` for creating new backends.  Provides methods to
    open/close sessions, acquire backends (ephemeral or persistent),
    and clean up all sessions on shutdown.
    """

    def __init__(self) -> None:
        self._sessions: dict[str, BrowserSession] = {}
        self._backend_manager = BackendManager()

    async def open(
        self,
        backend: str = "cdp",
        headless: bool = True,
        width: int = 1280,
        height: int = 800,
        user_agent: str | None = None,
        extra_headers: dict[str, str] | None = None,
        proxy: str | None = None,
        timeout: int = 30000,
        user_data_dir: str | None = None,
        connect_endpoint: str | None = None,
        remote_url: str | None = None,
        stealth: bool = False,
    ) -> str:
        """Launch a browser session and return its session ID.

        Args:
            backend: Backend type (``"cdp"``, ``"bidi"``, or ``"auto"``).
            headless: Whether to run the browser in headless mode.
            width: Initial viewport width in pixels.
            height: Initial viewport height in pixels.
            user_agent: Custom User-Agent string, or ``None`` for default.
            extra_headers: Additional HTTP headers to send with every request.
            proxy: Proxy URL, or ``None`` for no proxy.
            timeout: Default navigation timeout in milliseconds.
            user_data_dir: Chrome user data directory, or ``None``.
            connect_endpoint: WebSocket endpoint to connect to an existing browser.
            remote_url: Cloud browser WebSocket endpoint, or ``None``.
            stealth: Enable anti-bot stealth mode.

        Returns:
            A unique session ID string.
        """
        preferred = backend if backend != "auto" else None
        backend_instance = self._backend_manager.select(preferred)
        backend_name = backend_instance.__class__.__name__.replace("Backend", "").lower()

        opts = BrowserOptions(
            headless=headless,
            width=width,
            height=height,
            user_agent=user_agent,
            extra_headers=extra_headers or {},
            proxy=proxy,
            timeout=timeout,
            user_data_dir=user_data_dir,
            browser_url=connect_endpoint,
            remote_url=remote_url,
            stealth=stealth,
        )
        await backend_instance.launch(opts)

        session_id = str(uuid.uuid4())
        now = time.time()
        self._sessions[session_id] = BrowserSession(
            session_id=session_id,
            backend=backend_instance,
            backend_name=backend_name,
            created_at=now,
            last_used=now,
        )
        return session_id

    async def close(self, session_id: str) -> None:
        """Close a browser session and remove it from the manager.

        Args:
            session_id: ID of the session to close.

        Raises:
            SessionNotFoundError: If *session_id* is not registered.
        """
        session = self._sessions.pop(session_id, None)
        if session is None:
            raise SessionNotFoundError(session_id)
        await session.backend.close()

    def get(self, session_id: str) -> BrowserSession:
        """Return the session for the given ID and update ``last_used``.

        Args:
            session_id: ID of the session to retrieve.

        Returns:
            The ``BrowserSession`` associated with *session_id*.

        Raises:
            SessionNotFoundError: If *session_id* is not registered.
        """
        session = self._sessions.get(session_id)
        if session is None:
            raise SessionNotFoundError(session_id)
        session.last_used = time.time()
        return session

    @staticmethod
    async def call_backend(
        coro: Any,
        timeout: float = DEFAULT_BACKEND_TIMEOUT,
    ) -> Any:
        """Await a backend coroutine with a timeout to prevent hangs.

        If the backend call does not complete within *timeout* seconds,
        an ``asyncio.TimeoutError`` is raised, which tool handlers catch
        and convert to an error response.

        Args:
            coro: The coroutine to await.
            timeout: Maximum wait time in seconds.

        Returns:
            The result of the coroutine.

        Raises:
            asyncio.TimeoutError: If the call exceeds *timeout*.
        """
        return await asyncio.wait_for(coro, timeout=timeout)

    def info(self, session_id: str) -> dict[str, Any]:
        """Return session metadata without touching the backend.

        Args:
            session_id: ID of the session to inspect.

        Returns:
            A dict with ``session_id``, ``backend``, and ``created_at``.
        """
        session = self.get(session_id)
        return {
            "session_id": session.session_id,
            "backend": session.backend_name,
            "created_at": session.created_at,
        }

    async def get_current_url(self, session_id: str) -> str:
        """Return the current URL of the session's browser.

        Args:
            session_id: ID of the session to query.

        Returns:
            The current URL string, or an empty string on error.
        """
        session = self.get(session_id)
        try:
            url = await asyncio.wait_for(session.backend.eval("window.location.href"), timeout=10.0)
            return str(url) if url else ""
        except Exception:
            return ""

    async def acquire_backend(
        self,
        session_id: str | None = None,
        *,
        backend: str = "cdp",
        headless: bool = True,
        width: int = 1280,
        height: int = 800,
        user_agent: str | None = None,
        extra_headers: dict[str, str] | None = None,
        proxy: str | None = None,
        timeout: int = 30000,
        user_data_dir: str | None = None,
        connect_endpoint: str | None = None,
        remote_url: str | None = None,
        stealth: bool = False,
    ) -> tuple[AbstractBackend, str | None]:
        """Get a backend from an existing session or create an ephemeral one.

        When *session_id* is provided the corresponding session's backend
        is returned and the session ID is passed back so the caller knows
        not to close it.  When *session_id* is ``None`` a new ephemeral
        backend is launched and must be released by the caller.

        Args:
            session_id: Existing session ID, or ``None`` for ephemeral.
            backend: Backend type for ephemeral creation.
            headless: Whether to run ephemeral browser in headless mode.
            width: Initial viewport width for ephemeral backend.
            height: Initial viewport height for ephemeral backend.
            user_agent: Custom User-Agent string, or ``None``.
            extra_headers: Additional HTTP headers.
            proxy: Proxy URL, or ``None``.
            timeout: Navigation timeout in milliseconds.
            user_data_dir: Chrome user data directory, or ``None``.
            connect_endpoint: WebSocket endpoint for existing browser.
            remote_url: Cloud browser WebSocket endpoint, or ``None``.
            stealth: Enable anti-bot stealth mode.

        Returns:
            A tuple of ``(backend, session_id_or_None)``.
        """
        if session_id:
            session = self.get(session_id)
            return session.backend, session_id

        preferred = backend if backend != "auto" else None
        backend_instance = self._backend_manager.select(preferred)

        opts = BrowserOptions(
            headless=headless,
            width=width,
            height=height,
            user_agent=user_agent,
            extra_headers=extra_headers or {},
            proxy=proxy,
            timeout=timeout,
            user_data_dir=user_data_dir,
            browser_url=connect_endpoint,
            remote_url=remote_url,
            stealth=stealth,
        )
        await backend_instance.launch(opts)
        return backend_instance, None

    @staticmethod
    async def release_backend(backend: AbstractBackend, session_id: str | None) -> None:
        """Close the backend if it was ephemeral (no session).

        Args:
            backend: The backend instance to potentially close.
            session_id: The session ID, or ``None`` if ephemeral.
        """
        if session_id is None:
            await backend.close()

    async def cleanup_all(self) -> None:
        """Close all active sessions.

        Called during server shutdown to ensure no browser processes
        are left running.
        """
        ids = list(self._sessions.keys())
        for sid in ids:
            with contextlib.suppress(Exception):
                await self.close(sid)

    def make_wait(
        self,
        strategy: str = "load",
        selector: str | None = None,
        url_pattern: str | None = None,
        timeout: int = 30000,
    ) -> WaitStrategy:
        """Build a ``WaitStrategy`` from common tool parameters.

        Args:
            strategy: Wait strategy name (``"load"``, ``"selector"``, ``"none"``, etc.).
            selector: CSS selector for ``"selector"`` strategy.
            url_pattern: URL pattern for URL-based strategies.
            timeout: Maximum wait time in milliseconds.

        Returns:
            A configured ``WaitStrategy`` instance.
        """
        return WaitStrategy(
            strategy=strategy,
            selector=selector,
            url_pattern=url_pattern,
            timeout=timeout,
        )
