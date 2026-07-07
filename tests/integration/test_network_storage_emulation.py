"""Integration test for Network + Storage + Emulation tiers.

Requires Chrome and cdpwave installed. Run with:
    pytest tests/integration/test_network_storage_emulation.py -v -m integration
"""

from __future__ import annotations

import json

import pytest

from wavexis_mcp.models import (
    CaptureHARInput,
    LocalStorageGetInput,
    LocalStorageSetInput,
    NavigateInput,
    SessionCloseInput,
    SessionOpenInput,
    SetHeadersInput,
)
from wavexis_mcp.session import SessionManager


@pytest.mark.integration
@pytest.mark.chrome
async def test_network_storage_emulation_workflow() -> None:
    """Full workflow: session → set headers → capture HAR → localStorage → emulate → close."""
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.emulation import register as register_emulation
    from wavexis_mcp.tools.navigation import register as register_nav
    from wavexis_mcp.tools.network import register as register_network
    from wavexis_mcp.tools.session import register as register_session
    from wavexis_mcp.tools.storage import register as register_storage

    mcp = FastMCP("test-integration")
    mgr = SessionManager()
    register_session(mcp, mgr)
    register_nav(mcp, mgr)
    register_network(mcp, mgr)
    register_storage(mcp, mgr)
    register_emulation(mcp, mgr)

    open_tool = mcp._tool_manager.get_tool("wavexis_session_open")
    result = await open_tool.fn(SessionOpenInput(backend="cdp", headless=True))
    data = json.loads(result)
    assert data["status"] == "ok"
    session_id = data["session_id"]

    try:
        from wavexis_mcp.models import EmulateDeviceInput

        headers_tool = mcp._tool_manager.get_tool("wavexis_set_headers")
        result = await headers_tool.fn(
            SetHeadersInput(
                headers={"X-Test": "wavexis-mcp"},
                session_id=session_id,
            )
        )
        data = json.loads(result)
        assert data["status"] == "ok"

        nav_tool = mcp._tool_manager.get_tool("wavexis_navigate")
        result = await nav_tool.fn(NavigateInput(url="https://example.com", session_id=session_id))
        data = json.loads(result)
        assert data["status"] == "ok"

        har_tool = mcp._tool_manager.get_tool("wavexis_capture_har")
        result = await har_tool.fn(
            CaptureHARInput(url="https://example.com", session_id=session_id)
        )
        data = json.loads(result)
        assert "har" in data

        ls_set_tool = mcp._tool_manager.get_tool("wavexis_localstorage_set")
        result = await ls_set_tool.fn(
            LocalStorageSetInput(key="test_key", value="test_value", session_id=session_id)
        )
        data = json.loads(result)
        assert data["status"] == "ok"

        ls_get_tool = mcp._tool_manager.get_tool("wavexis_localstorage_get")
        result = await ls_get_tool.fn(LocalStorageGetInput(key="test_key", session_id=session_id))
        data = json.loads(result)
        assert data["value"] == "test_value"

        device_tool = mcp._tool_manager.get_tool("wavexis_emulate_device")
        result = await device_tool.fn(EmulateDeviceInput(device="iphone-15", session_id=session_id))
        data = json.loads(result)
        assert data["status"] == "ok"
    finally:
        close_tool = mcp._tool_manager.get_tool("wavexis_session_close")
        result = await close_tool.fn(SessionCloseInput(session_id=session_id))
        data = json.loads(result)
        assert data["status"] == "ok"
