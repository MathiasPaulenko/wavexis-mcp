"""Unit tests for input tools."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from wavexis_mcp.models import (
    CheckInput,
    ClickInput,
    DoubleClickInput,
    DragInput,
    DropInput,
    FillFormInput,
    FillInput,
    FindByTextInput,
    FormField,
    HoverInput,
    KeyPressInput,
    NLClickInput,
    NLFillInput,
    RightClickInput,
    SelectOptionInput,
    SetFilesInput,
    TapInput,
    TypeInput,
)
from wavexis_mcp.session import SessionManager


@pytest.mark.unit
async def test_click(mock_backend: AsyncMock) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.input import register

    mcp = FastMCP("test")
    mgr = SessionManager()
    mgr._backend_manager.select = MagicMock(return_value=mock_backend)
    register(mcp, mgr)

    tool = mcp._tool_manager.get_tool("wavexis_click")
    result = await tool.fn(ClickInput(selector="button", url="https://example.com"))
    data = json.loads(result)
    assert data["status"] == "ok"


@pytest.mark.unit
async def test_type(mock_backend: AsyncMock) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.input import register

    mcp = FastMCP("test")
    mgr = SessionManager()
    mgr._backend_manager.select = MagicMock(return_value=mock_backend)
    register(mcp, mgr)

    tool = mcp._tool_manager.get_tool("wavexis_type")
    result = await tool.fn(TypeInput(selector="input", text="hello", url="https://example.com"))
    data = json.loads(result)
    assert data["status"] == "ok"


@pytest.mark.unit
async def test_fill(mock_backend: AsyncMock) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.input import register

    mcp = FastMCP("test")
    mgr = SessionManager()
    mgr._backend_manager.select = MagicMock(return_value=mock_backend)
    register(mcp, mgr)

    tool = mcp._tool_manager.get_tool("wavexis_fill")
    result = await tool.fn(FillInput(selector="input", value="test", url="https://example.com"))
    data = json.loads(result)
    assert data["status"] == "ok"


@pytest.mark.unit
async def test_fill_form(session_manager_with_mock: SessionManager, mock_session_id: str) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.input import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_fill_form")
    result = await tool.fn(
        FillFormInput(
            fields=[
                FormField(selector="#name", value="Alice"),
                FormField(selector="#email", value="a@b.com"),
            ],
            session_id=mock_session_id,
        )
    )
    data = json.loads(result)
    assert data["status"] == "ok"
    assert data["fields_filled"] == 2


@pytest.mark.unit
async def test_select_option(mock_backend: AsyncMock) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.input import register

    mcp = FastMCP("test")
    mgr = SessionManager()
    mgr._backend_manager.select = MagicMock(return_value=mock_backend)
    register(mcp, mgr)

    tool = mcp._tool_manager.get_tool("wavexis_select_option")
    result = await tool.fn(
        SelectOptionInput(selector="select", value="opt1", url="https://example.com")
    )
    data = json.loads(result)
    assert data["status"] == "ok"


@pytest.mark.unit
async def test_hover(mock_backend: AsyncMock) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.input import register

    mcp = FastMCP("test")
    mgr = SessionManager()
    mgr._backend_manager.select = MagicMock(return_value=mock_backend)
    register(mcp, mgr)

    tool = mcp._tool_manager.get_tool("wavexis_hover")
    result = await tool.fn(HoverInput(selector="div", url="https://example.com"))
    data = json.loads(result)
    assert data["status"] == "ok"


@pytest.mark.unit
async def test_key_press(session_manager_with_mock: SessionManager, mock_session_id: str) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.input import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_key_press")
    result = await tool.fn(KeyPressInput(key="Enter", session_id=mock_session_id))
    data = json.loads(result)
    assert data["status"] == "ok"


@pytest.mark.unit
async def test_drag(mock_backend: AsyncMock) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.input import register

    mcp = FastMCP("test")
    mgr = SessionManager()
    mgr._backend_manager.select = MagicMock(return_value=mock_backend)
    register(mcp, mgr)

    tool = mcp._tool_manager.get_tool("wavexis_drag")
    result = await tool.fn(DragInput(source="#a", target="#b", url="https://example.com"))
    data = json.loads(result)
    assert data["status"] == "ok"


@pytest.mark.unit
async def test_tap(mock_backend: AsyncMock) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.input import register

    mcp = FastMCP("test")
    mgr = SessionManager()
    mgr._backend_manager.select = MagicMock(return_value=mock_backend)
    register(mcp, mgr)

    tool = mcp._tool_manager.get_tool("wavexis_tap")
    result = await tool.fn(TapInput(selector="button", url="https://example.com"))
    data = json.loads(result)
    assert data["status"] == "ok"


@pytest.mark.unit
async def test_set_files(mock_backend: AsyncMock) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.input import register

    mcp = FastMCP("test")
    mgr = SessionManager()
    mgr._backend_manager.select = MagicMock(return_value=mock_backend)
    register(mcp, mgr)

    tool = mcp._tool_manager.get_tool("wavexis_set_files")
    result = await tool.fn(
        SetFilesInput(selector="input[type=file]", files=["/tmp/a.txt"], url="https://example.com")
    )
    data = json.loads(result)
    assert data["status"] == "ok"


@pytest.mark.unit
async def test_check(session_manager_with_mock: SessionManager, mock_session_id: str) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.input import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    session_manager_with_mock.get(mock_session_id).backend.eval = AsyncMock(return_value=True)

    tool = mcp._tool_manager.get_tool("wavexis_check")
    result = await tool.fn(CheckInput(selector="input[type=checkbox]", session_id=mock_session_id))
    data = json.loads(result)
    assert data["status"] == "ok"
    assert data["checked"] is True


@pytest.mark.unit
async def test_uncheck(session_manager_with_mock: SessionManager, mock_session_id: str) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.input import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_uncheck")
    result = await tool.fn(CheckInput(selector="input[type=checkbox]", session_id=mock_session_id))
    data = json.loads(result)
    assert data["status"] == "ok"


@pytest.mark.unit
async def test_find_by_text(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.input import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_find_by_text")
    result = await tool.fn(FindByTextInput(query="Submit", session_id=mock_session_id))
    data = json.loads(result)
    assert "selector" in data


@pytest.mark.unit
async def test_find_by_text_all(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.input import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    session_manager_with_mock.get(mock_session_id).backend.find_by_text = AsyncMock(
        return_value=["button#a", "button#b"]
    )

    tool = mcp._tool_manager.get_tool("wavexis_find_by_text")
    result = await tool.fn(FindByTextInput(query="Submit", all=True, session_id=mock_session_id))
    data = json.loads(result)
    assert "selectors" in data
    assert data["count"] == 2


@pytest.mark.unit
async def test_nl_click(session_manager_with_mock: SessionManager, mock_session_id: str) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.input import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_nl_click")
    result = await tool.fn(NLClickInput(query="the submit button", session_id=mock_session_id))
    data = json.loads(result)
    assert data["status"] == "ok"


@pytest.mark.unit
async def test_nl_fill(session_manager_with_mock: SessionManager, mock_session_id: str) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.input import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_nl_fill")
    result = await tool.fn(
        NLFillInput(query="the email field", value="user@example.com", session_id=mock_session_id)
    )
    data = json.loads(result)
    assert data["status"] == "ok"


@pytest.mark.unit
async def test_double_click(mock_backend: AsyncMock) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.input import register

    mcp = FastMCP("test")
    mgr = SessionManager()
    mgr._backend_manager.select = MagicMock(return_value=mock_backend)
    register(mcp, mgr)

    tool = mcp._tool_manager.get_tool("wavexis_double_click")
    result = await tool.fn(DoubleClickInput(selector="button", url="https://example.com"))
    data = json.loads(result)
    assert data["status"] == "ok"


@pytest.mark.unit
async def test_right_click(mock_backend: AsyncMock) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.input import register

    mcp = FastMCP("test")
    mgr = SessionManager()
    mgr._backend_manager.select = MagicMock(return_value=mock_backend)
    register(mcp, mgr)

    tool = mcp._tool_manager.get_tool("wavexis_right_click")
    result = await tool.fn(RightClickInput(selector="button", url="https://example.com"))
    data = json.loads(result)
    assert data["status"] == "ok"


@pytest.mark.unit
async def test_drop(mock_backend: AsyncMock) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.input import register

    mcp = FastMCP("test")
    mgr = SessionManager()
    mgr._backend_manager.select = MagicMock(return_value=mock_backend)
    register(mcp, mgr)

    mock_backend.eval = AsyncMock(return_value={"x": 100, "y": 200})
    mock_backend.input_dispatch_drag_event = AsyncMock(return_value=None)

    tool = mcp._tool_manager.get_tool("wavexis_drop")
    result = await tool.fn(
        DropInput(
            selector="#dropzone",
            data={"text/plain": "hello"},
            paths=["d:\\\\file.txt"],
            url="https://example.com",
        )
    )
    data = json.loads(result)
    assert data["status"] == "ok"
    assert data["selector"] == "#dropzone"
    assert mock_backend.input_dispatch_drag_event.call_count == 3
