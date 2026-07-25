"""Security regression tests for WaveXisMCP."""

from __future__ import annotations

import json

import pytest

from wavexis_mcp.models import (
    A11ySnapshotInput,
    RawBiDiInput,
    RawCDPInput,
    ScrapeInput,
    WebsocketInterceptInput,
)
from wavexis_mcp.session import SessionManager


@pytest.mark.parametrize(
    ("module_name", "tool_name", "input_kwargs"),
    [
        ("wavexis_mcp.tools.input", "wavexis_click", {"selector": "button"}),
        ("wavexis_mcp.tools.capture", "wavexis_screenshot", {}),
        ("wavexis_mcp.tools.capture", "wavexis_pdf", {}),
        ("wavexis_mcp.tools.dom", "wavexis_dom_get", {"selector": "h1"}),
        ("wavexis_mcp.tools.cookies", "wavexis_cookies_get", {}),
        ("wavexis_mcp.tools.utility", "wavexis_invoke", {"method": "browser_version"}),
    ],
)
@pytest.mark.unit
async def test_tools_reject_internal_url_with_session(
    session_manager_with_mock: SessionManager,
    mock_session_id: str,
    module_name: str,
    tool_name: str,
    input_kwargs: dict[str, str],
) -> None:
    from mcp.server.fastmcp import FastMCP

    mod = __import__(module_name, fromlist=["register"])
    mcp = FastMCP("test")
    mod.register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool(tool_name)
    assert tool is not None
    kwargs = {"session_id": mock_session_id, "url": "http://169.254.169.254/latest/meta-data/"}
    kwargs.update(input_kwargs)

    # Build input model from the tool's annotations.
    input_name = tool.fn.__annotations__["input"]
    input_cls = eval(input_name, tool.fn.__globals__)
    result = await tool.fn(input_cls(**kwargs))
    data = json.loads(result)
    assert "error" in data, f"{tool_name} should reject cloud metadata URL"


@pytest.mark.unit
async def test_capture_scrape_rejects_internal_url(
    session_manager_with_mock: SessionManager,
) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.capture import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_scrape")
    assert tool is not None
    result = await tool.fn(
        ScrapeInput(
            urls=["http://169.254.169.254/latest/meta-data/"],
            expression="document.title",
        )
    )
    data = json.loads(result)
    assert "error" in data


@pytest.mark.unit
async def test_a11y_snapshot_rejects_internal_url(
    session_manager_with_mock: SessionManager,
) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.a11y import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_a11y_snapshot")
    assert tool is not None
    result = await tool.fn(
        A11ySnapshotInput(url="http://169.254.169.254/latest/meta-data/")
    )
    data = json.loads(result)
    assert "error" in data


@pytest.mark.unit
async def test_websocket_intercept_rejects_internal_url(
    session_manager_with_mock: SessionManager,
) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.data import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_websocket_intercept")
    assert tool is not None
    result = await tool.fn(
        WebsocketInterceptInput(url="http://169.254.169.254/latest/meta-data/")
    )
    data = json.loads(result)
    assert "error" in data


@pytest.mark.unit
async def test_raw_cdp_blocks_unsafe_method(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.workflows import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_raw_cdp")
    assert tool is not None
    result = await tool.fn(
        RawCDPInput(session_id=mock_session_id, method="Runtime.evaluate")
    )
    data = json.loads(result)
    assert "error" in data


@pytest.mark.unit
async def test_raw_bidi_blocks_unsafe_method(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.workflows import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_raw_bidi")
    assert tool is not None
    result = await tool.fn(
        RawBiDiInput(session_id=mock_session_id, method="script.evaluate")
    )
    data = json.loads(result)
    assert "error" in data


@pytest.mark.unit
async def test_session_open_sandboxes_user_data_dir(
    session_manager_with_mock: SessionManager,
) -> None:
    """user_data_dir outside WAVEXIS_MCP_OUTPUT_DIR must be rejected."""
    with pytest.raises(ValueError):
        await session_manager_with_mock.open(user_data_dir="/tmp/outside-profile")
