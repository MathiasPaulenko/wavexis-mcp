"""Unit tests for testing assertion tools."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock

import pytest

from wavexis_mcp.models import (
    AssertTextVisibleInput,
    AssertURLInput,
    AssertVisibleInput,
    GenerateLocatorInput,
)
from wavexis_mcp.session import SessionManager


def _register(mcp, mgr):
    from wavexis_mcp.tools.testing import register

    register(mcp, mgr)


@pytest.mark.unit
async def test_assert_visible_pass(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    session_manager_with_mock.get(mock_session_id).backend.eval = AsyncMock(
        return_value=True
    )

    tool = mcp._tool_manager.get_tool("wavexis_assert_visible")
    result = await tool.fn(
        AssertVisibleInput(session_id=mock_session_id, selector="body", timeout=100)
    )
    data = json.loads(result)
    assert data["passed"] is True
    assert data["selector"] == "body"


@pytest.mark.unit
async def test_assert_visible_fail(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    session_manager_with_mock.get(mock_session_id).backend.eval = AsyncMock(
        return_value=False
    )

    tool = mcp._tool_manager.get_tool("wavexis_assert_visible")
    result = await tool.fn(
        AssertVisibleInput(session_id=mock_session_id, selector=".missing", timeout=100)
    )
    data = json.loads(result)
    assert data["passed"] is False
    assert data["selector"] == ".missing"


@pytest.mark.unit
async def test_assert_text_visible_pass(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    session_manager_with_mock.get(mock_session_id).backend.eval = AsyncMock(
        return_value=True
    )

    tool = mcp._tool_manager.get_tool("wavexis_assert_text_visible")
    result = await tool.fn(
        AssertTextVisibleInput(session_id=mock_session_id, text="Example", timeout=100)
    )
    data = json.loads(result)
    assert data["passed"] is True
    assert data["text"] == "Example"


@pytest.mark.unit
async def test_assert_text_visible_fail(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    session_manager_with_mock.get(mock_session_id).backend.eval = AsyncMock(
        return_value=False
    )

    tool = mcp._tool_manager.get_tool("wavexis_assert_text_visible")
    result = await tool.fn(
        AssertTextVisibleInput(
            session_id=mock_session_id, text="Missing", timeout=100
        )
    )
    data = json.loads(result)
    assert data["passed"] is False


@pytest.mark.unit
async def test_assert_url_pass(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    session_manager_with_mock.get(mock_session_id).backend.eval = AsyncMock(
        return_value="https://example.com/page"
    )

    tool = mcp._tool_manager.get_tool("wavexis_assert_url")
    result = await tool.fn(
        AssertURLInput(session_id=mock_session_id, url_pattern="example.com")
    )
    data = json.loads(result)
    assert data["passed"] is True
    assert data["url"] == "https://example.com/page"


@pytest.mark.unit
async def test_assert_url_fail(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    session_manager_with_mock.get(mock_session_id).backend.eval = AsyncMock(
        return_value="https://other.com/page"
    )

    tool = mcp._tool_manager.get_tool("wavexis_assert_url")
    result = await tool.fn(
        AssertURLInput(session_id=mock_session_id, url_pattern="example.com")
    )
    data = json.loads(result)
    assert data["passed"] is False


@pytest.mark.unit
async def test_generate_locator(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_generate_locator")
    result = await tool.fn(
        GenerateLocatorInput(session_id=mock_session_id, selector="button.submit")
    )
    data = json.loads(result)
    assert data["locator"] == "#submit-btn"
    assert data["alternative"] == "button[type=submit]"
