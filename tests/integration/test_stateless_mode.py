"""Integration test: stateless mode — call tools without session."""

from __future__ import annotations

import json
from unittest.mock import patch

import pytest
from mcp.server.fastmcp import FastMCP

from wavexis_mcp.models import NavigateInput, ScreenshotInput
from wavexis_mcp.session import SessionManager
from wavexis_mcp.tools import capture, navigation


@pytest.mark.integration
async def test_stateless_screenshot(mock_backend: object) -> None:
    """Stateless screenshot: pass url, no session_id, browser launches and closes."""
    mcp = FastMCP("test")
    sm = SessionManager()

    capture.register(mcp, sm)

    with patch.object(sm._backend_manager, "select", return_value=mock_backend):
        tool = mcp._tool_manager.get_tool("wavexis_screenshot")
        result = await tool.fn(ScreenshotInput(url="https://example.com", headless=True))
        data = json.loads(result)
        assert data["status"] == "ok"
        assert "base64" in data


@pytest.mark.integration
async def test_stateless_navigate(mock_backend: object) -> None:
    """Stateless navigate: pass url, no session_id."""
    mcp = FastMCP("test")
    sm = SessionManager()

    navigation.register(mcp, sm)

    with patch.object(sm._backend_manager, "select", return_value=mock_backend):
        tool = mcp._tool_manager.get_tool("wavexis_navigate")
        result = await tool.fn(NavigateInput(url="https://example.com", headless=True))
        data = json.loads(result)
        assert data["status"] == "ok"
        assert data["url"] == "https://example.com"


@pytest.mark.integration
async def test_stateless_cleanup(mock_backend: object) -> None:
    """Verify ephemeral backend is closed after stateless call."""
    mcp = FastMCP("test")
    sm = SessionManager()

    capture.register(mcp, sm)

    with patch.object(sm._backend_manager, "select", return_value=mock_backend) as mock_select:
        tool = mcp._tool_manager.get_tool("wavexis_screenshot")
        await tool.fn(ScreenshotInput(url="https://example.com", headless=True))
        assert mock_select.called
        assert len(sm._sessions) == 0
