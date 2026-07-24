"""Unit tests for utility tools."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from wavexis_mcp.models import BrowserVersionInput, InvokeInput
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


@pytest.mark.unit
async def test_invoke_with_session(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.utility import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    session_manager_with_mock.get(mock_session_id).backend.page_print_to_pdf = AsyncMock(
        return_value="base64pdf"
    )

    tool = mcp._tool_manager.get_tool("wavexis_invoke")
    result = await tool.fn(
        InvokeInput(
            session_id=mock_session_id,
            method="page_print_to_pdf",
            params={"landscape": True, "display_header_footer": False},
        )
    )
    data = json.loads(result)
    assert data["status"] == "ok"
    assert data["result"] == "base64pdf"


@pytest.mark.unit
async def test_invoke_private_method(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.utility import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_invoke")
    result = await tool.fn(InvokeInput(session_id=mock_session_id, method="_private", params={}))
    data = json.loads(result)
    assert "error" in data
    assert data["tool"] == "wavexis_invoke"
