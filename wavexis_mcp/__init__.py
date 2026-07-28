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

__version__ = "1.6.19"

__all__ = [
    "BackendError",
    "BrowserSession",
    "CapsError",
    "OperationTimeoutError",
    "SessionExpiredError",
    "SessionManager",
    "SessionNotFoundError",
    "TimeoutError",
    "ToolError",
    "WaveXisMCPError",
    "__version__",
    "get_suggestion",
]
