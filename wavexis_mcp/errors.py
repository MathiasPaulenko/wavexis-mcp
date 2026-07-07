"""Exception hierarchy for WaveXisMCP.

All exceptions raised by the WaveXisMCP package inherit from
``WaveXisMCPError``, making it easy for callers to catch any
project-specific error in a single ``except`` clause.
"""

from __future__ import annotations


class WaveXisMCPError(Exception):
    """Base exception for all WaveXisMCP errors."""


class SessionNotFoundError(WaveXisMCPError):
    """Raised when a session ID is not found in the SessionManager.

    Attributes:
        session_id: The session ID that was not found.
    """

    def __init__(self, session_id: str) -> None:
        """Initialize the error with the missing session ID.

        Args:
            session_id: The session ID that was not found.
        """
        super().__init__(f"Session '{session_id}' not found.")


class SessionExpiredError(WaveXisMCPError):
    """Raised when a session has expired or been closed.

    Attributes:
        session_id: The session ID that has expired.
    """

    def __init__(self, session_id: str) -> None:
        """Initialize the error with the expired session ID.

        Args:
            session_id: The session ID that has expired.
        """
        super().__init__(f"Session '{session_id}' has expired or been closed.")


class BackendError(WaveXisMCPError):
    """Raised when a backend operation fails."""


class ToolError(WaveXisMCPError):
    """Raised when a tool execution fails."""


class CapsError(WaveXisMCPError):
    """Raised when an invalid capability tier is requested."""


class TimeoutError(WaveXisMCPError):
    """Raised when an operation exceeds its timeout.

    Attributes:
        timeout_ms: The timeout value in milliseconds.
    """

    def __init__(self, timeout_ms: int) -> None:
        """Initialize the error with the timeout value.

        Args:
            timeout_ms: The timeout in milliseconds that was exceeded.
        """
        super().__init__(f"Operation timed out after {timeout_ms}ms.")


# ── Error suggestion mapping ─────────────────────────────────────

_SUGGESTIONS: dict[str, str] = {
    "SessionNotFoundError": ("Call wavexis_session_open first to create a browser session."),
    "SessionExpiredError": (
        "The session was closed. Call wavexis_session_open to start a new one."
    ),
    "BackendError": (
        "Try wavexis_backends to see available backends. "
        "Install with: pip install wavexis[cdp] or wavexis[bidi]."
    ),
    "TimeoutError": ("Increase wait_timeout or check that the page has loaded before acting."),
    "CapsError": ("Restart the server with the required --caps flag (e.g. --caps=core,devtools)."),
    "ToolError": ("Check the error message for details. Verify selectors and page state."),
}


def get_suggestion(error: Exception) -> str:
    """Get an actionable suggestion for an error.

    Args:
        error: The exception to get a suggestion for.

    Returns:
        A human-readable suggestion string.
    """
    error_type = type(error).__name__
    return _SUGGESTIONS.get(error_type, "Check the error message and verify inputs.")
