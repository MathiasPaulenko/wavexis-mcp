"""Unit tests for cookie tools."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from wavexis_mcp.models import (
    CookiesClearInput,
    CookiesDeleteInput,
    CookiesGetInput,
    CookiesSetInput,
)
from wavexis_mcp.session import SessionManager


@pytest.mark.unit
async def test_cookies_get(mock_backend: AsyncMock) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.cookies import register

    mcp = FastMCP("test")
    mgr = SessionManager()
    mgr._backend_manager.select = MagicMock(return_value=mock_backend)
    register(mcp, mgr)

    tool = mcp._tool_manager.get_tool("wavexis_cookies_get")
    result = await tool.fn(CookiesGetInput(url="https://example.com"))
    data = json.loads(result)
    assert "cookies" in data
    assert data["count"] == 1


@pytest.mark.unit
async def test_cookies_set(mock_backend: AsyncMock) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.cookies import register

    mcp = FastMCP("test")
    mgr = SessionManager()
    mgr._backend_manager.select = MagicMock(return_value=mock_backend)
    register(mcp, mgr)

    tool = mcp._tool_manager.get_tool("wavexis_cookies_set")
    result = await tool.fn(
        CookiesSetInput(name="token", value="abc", domain="example.com", url="https://example.com")
    )
    data = json.loads(result)
    assert data["status"] == "ok"


@pytest.mark.unit
async def test_cookies_delete(mock_backend: AsyncMock) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.cookies import register

    mcp = FastMCP("test")
    mgr = SessionManager()
    mgr._backend_manager.select = MagicMock(return_value=mock_backend)
    register(mcp, mgr)

    tool = mcp._tool_manager.get_tool("wavexis_cookies_delete")
    result = await tool.fn(
        CookiesDeleteInput(name="token", domain="example.com", url="https://example.com")
    )
    data = json.loads(result)
    assert data["status"] == "ok"


@pytest.mark.unit
async def test_cookies_clear(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.cookies import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_cookies_clear")
    result = await tool.fn(CookiesClearInput(session_id=mock_session_id))
    data = json.loads(result)
    assert data["status"] == "ok"
