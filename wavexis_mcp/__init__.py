"""WaveXisMCP — MCP server exposing wavexis browser automation to LLMs."""

from wavexis_mcp.errors import (
    BackendError,
    CapsError,
    OperationTimeoutError,
    SessionExpiredError,
    SessionNotFoundError,
    TimeoutError,
    ToolError,
    WaveXisMCPError,
    get_suggestion,
)
from wavexis_mcp.session import BrowserSession, SessionManager

__version__ = "1.6.6"

__all__ = [
    "__version__",
    "BackendError",
    "BrowserSession",
    "CapsError",
    "get_suggestion",
    "OperationTimeoutError",
    "SessionExpiredError",
    "SessionManager",
    "SessionNotFoundError",
    "TimeoutError",
    "ToolError",
    "WaveXisMCPError",
]
