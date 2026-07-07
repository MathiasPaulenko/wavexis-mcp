"""Integration test: session lifecycle — open, use, close, verify cleanup."""

from __future__ import annotations

import json
from unittest.mock import patch

import pytest
from mcp.server.fastmcp import FastMCP

from wavexis_mcp.models import (
    NavigateInput,
    SessionCloseInput,
    SessionInfoInput,
    SessionOpenInput,
)
from wavexis_mcp.session import SessionManager
from wavexis_mcp.tools import capture, navigation
from wavexis_mcp.tools import session as session_mod


@pytest.mark.integration
async def test_session_lifecycle(mock_backend: object) -> None:
    """Open a session, use it, close it, verify cleanup."""
    mcp = FastMCP("test")
    sm = SessionManager()

    session_mod.register(mcp, sm)
    navigation.register(mcp, sm)
    capture.register(mcp, sm)

    with patch.object(sm._backend_manager, "select", return_value=mock_backend):
        open_tool = mcp._tool_manager.get_tool("wavexis_session_open")
        result = await open_tool.fn(SessionOpenInput(backend="cdp", headless=True))
        data = json.loads(result)
        assert data["status"] == "ok"
        session_id = data["session_id"]

        nav_tool = mcp._tool_manager.get_tool("wavexis_navigate")
        result = await nav_tool.fn(
            NavigateInput(url="https://example.com", session_id=session_id)
        )
        nav_data = json.loads(result)
        assert nav_data["status"] == "ok"

        close_tool = mcp._tool_manager.get_tool("wavexis_session_close")
        result = await close_tool.fn(SessionCloseInput(session_id=session_id))
        close_data = json.loads(result)
        assert close_data["status"] == "ok"

        assert session_id not in sm._sessions


@pytest.mark.integration
async def test_session_info(mock_backend: object) -> None:
    """Verify session_info returns correct metadata."""
    mcp = FastMCP("test")
    sm = SessionManager()

    session_mod.register(mcp, sm)

    with patch.object(sm._backend_manager, "select", return_value=mock_backend):
        open_tool = mcp._tool_manager.get_tool("wavexis_session_open")
        result = await open_tool.fn(SessionOpenInput(backend="cdp", headless=True))
        data = json.loads(result)
        session_id = data["session_id"]

        info_tool = mcp._tool_manager.get_tool("wavexis_session_info")
        result = await info_tool.fn(SessionInfoInput(session_id=session_id))
        info_data = json.loads(result)
        assert info_data["session_id"] == session_id

        close_tool = mcp._tool_manager.get_tool("wavexis_session_close")
        await close_tool.fn(SessionCloseInput(session_id=session_id))


@pytest.mark.integration
async def test_session_list(mock_backend: object) -> None:
    """Verify session_list shows active sessions."""
    mcp = FastMCP("test")
    sm = SessionManager()

    session_mod.register(mcp, sm)

    with patch.object(sm._backend_manager, "select", return_value=mock_backend):
        open_tool = mcp._tool_manager.get_tool("wavexis_session_open")
        await open_tool.fn(SessionOpenInput(backend="cdp", headless=True))
        await open_tool.fn(SessionOpenInput(backend="cdp", headless=True))

        assert len(sm._sessions) == 2

        await sm.cleanup_all()
        assert len(sm._sessions) == 0
