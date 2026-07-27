"""Pytest configuration and fixtures for WaveXisMCP E2E tests.

E2E tests spin up:
  1. A local HTTP server serving HTML fixture pages + mock API endpoints.
  2. A full WaveXisMCP server (create_server with --caps=all).
  3. A real Chrome browser session via wavexis/cdpwave.

Tests call MCP tools directly through the FastMCP tool manager,
exercising the complete stack: Pydantic validation → tool handler →
SessionManager → wavexis backend → CDP → Chrome.
"""

from __future__ import annotations

import json
import logging
import os
import socket
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from typing import Any

import pytest

# E2E tests need to navigate to 127.0.0.1 — allow internal URLs.
os.environ.setdefault("WAVEXIS_MCP_ALLOW_INTERNAL_URLS", "1")
# Allow raw CDP commands in E2E tests.
os.environ.setdefault("WAVEXIS_MCP_ALLOW_RAW_COMMANDS", "all")

from mcp.server.fastmcp import FastMCP

from wavexis_mcp.server import create_server
from wavexis_mcp.session import SessionManager

_logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def _find_free_port() -> int:
    """Return a free TCP port for the local HTTP server."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class _FixtureHandler(SimpleHTTPRequestHandler):
    """HTTP handler that serves fixture pages and mock API endpoints."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, directory=str(FIXTURES_DIR), **kwargs)

    def _send_json(self, status: int, payload: Any) -> None:
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/api/data":
            self._send_json(200, {"message": "hello", "value": 42, "items": [1, 2, 3]})
        elif self.path == "/api/text":
            body = b"This is a plain text response from the API."
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path == "/api/notfound":
            self._send_json(404, {"error": "Resource not found"})
        elif self.path == "/api/headers":
            self._send_json(200, dict(self.headers))
        else:
            super().do_GET()

    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length else b""
        self._send_json(200, {"received": body.decode("utf-8", errors="replace"), "method": "POST"})

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        pass  # suppress noisy request logs


class _HTTPServerThread(threading.Thread):
    """Run an HTTP server in a background thread."""

    def __init__(self, port: int) -> None:
        super().__init__(daemon=True)
        self.port = port
        self.server: HTTPServer | None = None
        self._started = threading.Event()

    def run(self) -> None:
        self.server = HTTPServer(("127.0.0.1", self.port), _FixtureHandler)
        self._started.set()
        self.server.serve_forever()

    def wait_started(self, timeout: float = 5.0) -> None:
        self._started.wait(timeout)

    def stop(self) -> None:
        if self.server:
            self.server.shutdown()
            self.server.server_close()


# ---------------------------------------------------------------------------
# Session-scoped fixtures: HTTP server + MCP server
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def http_server_port() -> int:
    """Start a local HTTP server and return its port."""
    port = _find_free_port()
    thread = _HTTPServerThread(port)
    thread.start()
    thread.wait_started()
    yield port
    thread.stop()


@pytest.fixture(scope="session")
def base_url(http_server_port: int) -> str:
    """Base URL for the local HTTP server."""
    return f"http://127.0.0.1:{http_server_port}"


@pytest.fixture(scope="session")
def mcp_server() -> FastMCP:
    """Create a full WaveXisMCP server with all capability tiers enabled."""
    return create_server(caps="all")


@pytest.fixture(scope="session")
def session_manager(mcp_server: FastMCP) -> SessionManager:
    """Extract the SessionManager from the MCP server."""
    return mcp_server._wavexis_session_manager  # type: ignore[attr-defined]


# ---------------------------------------------------------------------------
# Function-scoped fixtures: real Chrome session per test
# ---------------------------------------------------------------------------


@pytest.fixture
async def chrome_session(
    mcp_server: FastMCP,
    base_url: str,
) -> str:
    """Open a real Chrome session and navigate to the index page.

    Yields the session_id.  The session is closed after the test.
    """
    open_tool = mcp_server._tool_manager.get_tool("wavexis_session_open")
    from wavexis_mcp.models import SessionOpenInput

    result = await open_tool.fn(SessionOpenInput(backend="cdp", headless=True))
    data = json.loads(result)
    assert data["status"] == "ok", f"Failed to open session: {data}"
    session_id: str = data["session_id"]

    # Navigate to the index page
    from wavexis_mcp.models import NavigateInput

    nav_tool = mcp_server._tool_manager.get_tool("wavexis_navigate")
    await nav_tool.fn(NavigateInput(url=f"{base_url}/index.html", session_id=session_id))

    try:
        yield session_id
    finally:
        from wavexis_mcp.models import SessionCloseInput

        close_tool = mcp_server._tool_manager.get_tool("wavexis_session_close")
        await close_tool.fn(SessionCloseInput(session_id=session_id))


# ---------------------------------------------------------------------------
# Helper: call a tool and parse JSON response
# ---------------------------------------------------------------------------


@pytest.fixture
def call_tool(mcp_server: FastMCP):
    """Return a helper that calls an MCP tool by name and returns parsed JSON.

    Usage::

        data = await call_tool("wavexis_navigate", url="https://...", session_id=sid)
    """

    async def _call(tool_name: str, **kwargs: Any) -> dict[str, Any]:
        tool = mcp_server._tool_manager.get_tool(tool_name)
        # FastMCP wraps the actual input model in an outer model with an
        # ``input`` field, so we pass {"input": kwargs} to tool.run().
        result = await tool.run({"input": kwargs})
        return json.loads(result)

    return _call


# ---------------------------------------------------------------------------
# Autouse: skip E2E tests if Chrome/cdpwave is not available
# ---------------------------------------------------------------------------


def _chrome_available() -> bool:
    """Check if a Chrome browser is available via wavexis BackendManager."""
    try:
        from wavexis.backend.manager import BackendManager

        mgr = BackendManager()
        available = mgr.list_available()
        return "cdp" in available
    except Exception:
        return False


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Skip E2E tests if Chrome is not available."""
    if not _chrome_available():
        skip_marker = pytest.mark.skip(reason="Chrome/cdpwave not available — skipping E2E tests")
        for item in items:
            if "e2e" in item.keywords:
                item.add_marker(skip_marker)
