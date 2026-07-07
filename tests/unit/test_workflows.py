"""Unit tests for workflow tools."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock

import pytest

from wavexis_mcp.models import (
    BrowserContextCloseInput,
    BrowserContextCreateInput,
    MultiActionInput,
    RawBiDiInput,
    RawCDPInput,
)
from wavexis_mcp.session import SessionManager


def _register(mcp, mgr):
    from wavexis_mcp.tools.workflows import register

    register(mcp, mgr)


@pytest.mark.unit
async def test_raw_cdp(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_raw_cdp")
    result = await tool.fn(
        RawCDPInput(session_id=mock_session_id, method="Page.reload")
    )
    data = json.loads(result)
    assert "result" in data


@pytest.mark.unit
async def test_raw_bidi(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_raw_bidi")
    result = await tool.fn(
        RawBiDiInput(
            session_id=mock_session_id,
            method="browsingContext.navigate",
            params={"url": "https://example.com"},
        )
    )
    data = json.loads(result)
    assert "result" in data


@pytest.mark.unit
async def test_browser_context_create(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    session_manager_with_mock.get(mock_session_id).backend.raw = AsyncMock(
        return_value={"browserContextId": "ctx-123"}
    )

    tool = mcp._tool_manager.get_tool("wavexis_browser_context_create")
    result = await tool.fn(
        BrowserContextCreateInput(session_id=mock_session_id)
    )
    data = json.loads(result)
    assert data["context_id"] == "ctx-123"


@pytest.mark.unit
async def test_browser_context_close(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_browser_context_close")
    result = await tool.fn(
        BrowserContextCloseInput(
            session_id=mock_session_id, context_id="ctx-123"
        )
    )
    data = json.loads(result)
    assert data["status"] == "ok"


@pytest.mark.unit
async def test_multi_action_yaml(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    yaml_config = (
        "actions:\n"
        "  - navigate:\n"
        "      url: https://example.com\n"
        "  - eval:\n"
        "      expression: document.title\n"
    )

    tool = mcp._tool_manager.get_tool("wavexis_multi_action")
    result = await tool.fn(
        MultiActionInput(config=yaml_config, session_id=mock_session_id)
    )
    data = json.loads(result)
    assert data["status"] == "ok"
    assert data["actions"] == 2
    assert len(data["results"]) == 2
