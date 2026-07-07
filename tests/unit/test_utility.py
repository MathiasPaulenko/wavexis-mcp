"""Unit tests for utility tools."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from wavexis_mcp.models import BrowserVersionInput
from wavexis_mcp.session import SessionManager


@pytest.mark.unit
async def test_browser_version(mock_backend: AsyncMock) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.utility import register

    mcp = FastMCP("test")
    mgr = SessionManager()
    mgr._backend_manager.select = MagicMock(return_value=mock_backend)
    register(mcp, mgr)

    tool = mcp._tool_manager.get_tool("wavexis_browser_version")
    result = await tool.fn(BrowserVersionInput())
    data = json.loads(result)
    assert "version" in data
    assert data["backend"] == "cdp"


@pytest.mark.unit
async def test_backends() -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.utility import register

    mcp = FastMCP("test")
    mgr = SessionManager()
    register(mcp, mgr)

    tool = mcp._tool_manager.get_tool("wavexis_backends")
    result = await tool.fn()
    data = json.loads(result)
    assert "backends" in data
    assert "available" in data
