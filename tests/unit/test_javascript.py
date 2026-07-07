"""Unit tests for JavaScript evaluation tool."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock

import pytest

from wavexis_mcp.models import EvalInput
from wavexis_mcp.session import SessionManager


def _register(mcp, mgr):
    from wavexis_mcp.tools.javascript import register

    register(mcp, mgr)


@pytest.mark.unit
async def test_eval_basic(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_eval")
    result = await tool.fn(
        EvalInput(expression="1 + 2", session_id=mock_session_id)
    )
    data = json.loads(result)
    assert data["result"] == "result"
    assert data["type"] == "str"


@pytest.mark.unit
async def test_eval_with_url(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_eval")
    result = await tool.fn(
        EvalInput(
            expression="document.title",
            url="https://example.com",
            session_id=mock_session_id,
        )
    )
    data = json.loads(result)
    assert data["result"] == "result"
    session_manager_with_mock.get(mock_session_id).backend.navigate.assert_awaited()


@pytest.mark.unit
async def test_eval_none_result(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    session_manager_with_mock.get(mock_session_id).backend.eval = AsyncMock(return_value=None)

    tool = mcp._tool_manager.get_tool("wavexis_eval")
    result = await tool.fn(
        EvalInput(expression="undefined_var", session_id=mock_session_id)
    )
    data = json.loads(result)
    assert data["result"] is None
    assert data["type"] == "undefined"


@pytest.mark.unit
async def test_eval_await_promise(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_eval")
    result = await tool.fn(
        EvalInput(
            expression="Promise.resolve(42)",
            await_promise=True,
            session_id=mock_session_id,
        )
    )
    data = json.loads(result)
    assert data["result"] == "result"


@pytest.mark.unit
async def test_eval_error(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    session_manager_with_mock.get(mock_session_id).backend.eval = AsyncMock(
        side_effect=RuntimeError("JS error")
    )

    tool = mcp._tool_manager.get_tool("wavexis_eval")
    result = await tool.fn(
        EvalInput(expression="throw new Error()", session_id=mock_session_id)
    )
    data = json.loads(result)
    assert "error" in data
    assert data["tool"] == "wavexis_eval"


@pytest.mark.unit
async def test_eval_stateless_mode(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_eval")
    result = await tool.fn(
        EvalInput(
            expression="document.title",
            backend="cdp",
            headless=True,
        )
    )
    data = json.loads(result)
    assert "result" in data
    assert "type" in data
