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


@pytest.mark.unit
async def test_multi_action_all_types(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    yaml_config = (
        "actions:\n"
        "  - navigate:\n"
        "      url: https://example.com\n"
        "  - screenshot:\n"
        "      full_page: true\n"
        "  - eval:\n"
        "      expression: document.title\n"
        "  - click:\n"
        "      selector: '#btn'\n"
        "  - type:\n"
        "      selector: '#input'\n"
        "      text: hello\n"
        "  - fill:\n"
        "      selector: '#field'\n"
        "      value: test\n"
    )

    tool = mcp._tool_manager.get_tool("wavexis_multi_action")
    result = await tool.fn(
        MultiActionInput(config=yaml_config, session_id=mock_session_id)
    )
    data = json.loads(result)
    assert data["status"] == "ok"
    assert data["actions"] == 6
    assert len(data["results"]) == 6
    types = [r["type"] for r in data["results"]]
    assert "navigate" in types
    assert "screenshot" in types
    assert "eval" in types
    assert "click" in types
    assert "type" in types
    assert "fill" in types


@pytest.mark.unit
async def test_multi_action_unknown_action(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    yaml_config = (
        "actions:\n"
        "  - scroll:\n"
        "      amount: 500\n"
    )

    tool = mcp._tool_manager.get_tool("wavexis_multi_action")
    result = await tool.fn(
        MultiActionInput(config=yaml_config, session_id=mock_session_id)
    )
    data = json.loads(result)
    assert data["status"] == "ok"
    assert data["results"][0]["status"] == "unknown"


@pytest.mark.unit
async def test_multi_action_continue_on_error(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    session_manager_with_mock.get(mock_session_id).backend.click = AsyncMock(
        side_effect=RuntimeError("element not found")
    )

    yaml_config = (
        "actions:\n"
        "  - click:\n"
        "      selector: '#missing'\n"
        "  - eval:\n"
        "      expression: 1+1\n"
    )

    tool = mcp._tool_manager.get_tool("wavexis_multi_action")
    result = await tool.fn(
        MultiActionInput(
            config=yaml_config,
            continue_on_error=True,
            session_id=mock_session_id,
        )
    )
    data = json.loads(result)
    assert data["status"] == "ok"
    assert len(data["errors"]) == 1
    assert len(data["results"]) == 1


@pytest.mark.unit
async def test_multi_action_stop_on_error(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    session_manager_with_mock.get(mock_session_id).backend.click = AsyncMock(
        side_effect=RuntimeError("element not found")
    )

    yaml_config = (
        "actions:\n"
        "  - click:\n"
        "      selector: '#missing'\n"
        "  - eval:\n"
        "      expression: 1+1\n"
    )

    tool = mcp._tool_manager.get_tool("wavexis_multi_action")
    result = await tool.fn(
        MultiActionInput(
            config=yaml_config,
            continue_on_error=False,
            session_id=mock_session_id,
        )
    )
    data = json.loads(result)
    assert len(data["errors"]) == 1
    assert len(data["results"]) == 0


@pytest.mark.unit
async def test_multi_action_empty_config(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_multi_action")
    result = await tool.fn(
        MultiActionInput(config="", session_id=mock_session_id)
    )
    data = json.loads(result)
    assert data["status"] == "ok"
    assert data["actions"] == 0


@pytest.mark.unit
async def test_multi_action_invalid_yaml(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_multi_action")
    result = await tool.fn(
        MultiActionInput(config="{{invalid yaml", session_id=mock_session_id)
    )
    data = json.loads(result)
    assert "error" in data
    assert data["tool"] == "wavexis_multi_action"


@pytest.mark.unit
async def test_browser_context_create(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    session_manager_with_mock.get(mock_session_id).backend.raw = AsyncMock(
        return_value={"browserContextId": "ctx-abc"}
    )

    tool = mcp._tool_manager.get_tool("wavexis_browser_context_create")
    result = await tool.fn(
        BrowserContextCreateInput(session_id=mock_session_id)
    )
    data = json.loads(result)
    assert data["context_id"] == "ctx-abc"


@pytest.mark.unit
async def test_browser_context_create_error(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    session_manager_with_mock.get(mock_session_id).backend.raw = AsyncMock(
        side_effect=RuntimeError("failed")
    )

    tool = mcp._tool_manager.get_tool("wavexis_browser_context_create")
    result = await tool.fn(
        BrowserContextCreateInput(session_id=mock_session_id)
    )
    data = json.loads(result)
    assert "error" in data
    assert data["tool"] == "wavexis_browser_context_create"


@pytest.mark.unit
async def test_browser_context_close(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    session_manager_with_mock.get(mock_session_id).backend.close_context = AsyncMock()

    tool = mcp._tool_manager.get_tool("wavexis_browser_context_close")
    result = await tool.fn(
        BrowserContextCloseInput(session_id=mock_session_id, context_id="ctx-1")
    )
    data = json.loads(result)
    assert data["status"] == "ok"
