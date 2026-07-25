"""Security regression tests for WaveXisMCP."""

from __future__ import annotations

import json
from typing import Any

import pytest

from wavexis_mcp.models import (
    A11ySnapshotInput,
    EvalInput,
    NewTabInput,
    RawBiDiInput,
    RawCDPInput,
    ScrapeInput,
    ServiceWorkerEmulateInput,
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
    result = await tool.fn(A11ySnapshotInput(url="http://169.254.169.254/latest/meta-data/"))
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
    result = await tool.fn(WebsocketInterceptInput(url="http://169.254.169.254/latest/meta-data/"))
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
    result = await tool.fn(RawCDPInput(session_id=mock_session_id, method="Runtime.evaluate"))
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
    result = await tool.fn(RawBiDiInput(session_id=mock_session_id, method="script.evaluate"))
    data = json.loads(result)
    assert "error" in data


@pytest.mark.unit
async def test_session_open_sandboxes_user_data_dir(
    session_manager_with_mock: SessionManager,
) -> None:
    """user_data_dir outside WAVEXIS_MCP_OUTPUT_DIR must be rejected."""
    with pytest.raises(ValueError):
        await session_manager_with_mock.open(user_data_dir="/tmp/outside-profile")


@pytest.mark.unit
async def test_session_open_rejects_crlf_in_user_agent(
    session_manager_with_mock: SessionManager,
) -> None:
    """User-Agent values containing CRLF must be rejected."""
    with pytest.raises(ValueError):
        await session_manager_with_mock.open(user_agent="Evil\r\nX-Inject: true")


@pytest.mark.unit
async def test_session_open_rejects_crlf_in_extra_headers(
    session_manager_with_mock: SessionManager,
) -> None:
    """Extra header values containing CRLF or null bytes must be rejected."""
    with pytest.raises(ValueError):
        await session_manager_with_mock.open(extra_headers={"X-Test": "evil\r\nvalue"})


@pytest.mark.unit
async def test_service_worker_emulate_rejects_internal_url(
    session_manager_with_mock: SessionManager,
    mock_session_id: str,
) -> None:
    """Service worker script URLs must pass URL validation."""
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.experimental import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_service_worker_emulate")
    result = await tool.fn(
        ServiceWorkerEmulateInput(
            session_id=mock_session_id,
            registration_id="sw-1",
            script_url="http://169.254.169.254/latest/meta-data/",
        )
    )
    data = json.loads(result)
    assert "error" in data


@pytest.mark.unit
def test_base_input_rejects_oversized_string() -> None:
    """Inputs with strings longer than the limit should fail Pydantic validation."""
    with pytest.raises(ValueError):
        EvalInput(expression="x" * 60_000)


@pytest.mark.unit
def test_base_input_rejects_oversized_container() -> None:
    """Inputs with dicts/lists larger than the limit should fail validation."""
    from wavexis_mcp.models import SetHeadersInput

    with pytest.raises(ValueError):
        SetHeadersInput(headers={f"header-{i}": "value" for i in range(1_001)})


@pytest.mark.unit
async def test_new_tab_rejects_internal_url(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    """New tabs must run submitted URLs through the same SSRF filter as navigate."""
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.tabs import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_new_tab")
    assert tool is not None
    result = await tool.fn(
        NewTabInput(session_id=mock_session_id, url="http://169.254.169.254/latest/meta-data/")
    )
    data = json.loads(result)
    assert "error" in data


@pytest.mark.unit
async def test_set_files_rejects_oversized_file(
    session_manager_with_mock: SessionManager, mock_session_id: str, tmp_path: Any
) -> None:
    """File uploads must reject files that exceed the configured size limit."""
    from unittest.mock import patch

    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.models import SetFilesInput
    from wavexis_mcp.tools.input import _MAX_FILE_SIZE, _validate_files, register

    large = tmp_path / "large.bin"
    large.write_bytes(b"x" * (_MAX_FILE_SIZE + 1))

    # Keep the test fast by validating the helper directly.
    with pytest.raises(ValueError):
        _validate_files([str(large)])

    # Also exercise the tool end-to-end with the size patched down.
    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)
    tool = mcp._tool_manager.get_tool("wavexis_set_files")
    assert tool is not None

    small = tmp_path / "small.bin"
    small.write_bytes(b"x")
    with patch(
        "wavexis_mcp.tools.input._MAX_FILE_SIZE",
        len(small.read_bytes()) - 1,
    ):
        result = await tool.fn(
            SetFilesInput(session_id=mock_session_id, selector="#file", files=[str(small)])
        )
    data = json.loads(result)
    assert "error" in data
