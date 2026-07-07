"""Integration test for workflows + data + experimental tools.

Requires Chrome and cdpwave installed. Run with:
    pytest tests/integration/test_workflows_data_experimental.py -v -m integration
"""

from __future__ import annotations

import json

import pytest

from wavexis_mcp.models import (
    ExtractInput,
    LighthouseInput,
    MultiActionInput,
    RawCDPInput,
    ServiceWorkerListInput,
    SessionCloseInput,
    SessionOpenInput,
)
from wavexis_mcp.session import SessionManager


@pytest.mark.integration
@pytest.mark.chrome
async def test_workflows_data_experimental_workflow() -> None:
    """Full workflow: session → multi-action → raw CDP → lighthouse → extract → SW list → close."""
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.capture import register as register_capture
    from wavexis_mcp.tools.data import register as register_data
    from wavexis_mcp.tools.experimental import register as register_experimental
    from wavexis_mcp.tools.navigation import register as register_nav
    from wavexis_mcp.tools.session import register as register_session
    from wavexis_mcp.tools.workflows import register as register_workflows

    mcp = FastMCP("test-integration")
    mgr = SessionManager()
    register_session(mcp, mgr)
    register_nav(mcp, mgr)
    register_capture(mcp, mgr)
    register_workflows(mcp, mgr)
    register_data(mcp, mgr)
    register_experimental(mcp, mgr)

    open_tool = mcp._tool_manager.get_tool("wavexis_session_open")
    result = await open_tool.fn(SessionOpenInput(backend="cdp", headless=True))
    data = json.loads(result)
    assert data["status"] == "ok"
    session_id = data["session_id"]

    try:
        # 1. Multi-action: navigate → eval
        yaml_config = (
            "actions:\n"
            "  - navigate:\n"
            "      url: https://example.com\n"
            "  - eval:\n"
            "      expression: document.title\n"
        )
        multi_tool = mcp._tool_manager.get_tool("wavexis_multi_action")
        result = await multi_tool.fn(
            MultiActionInput(config=yaml_config, session_id=session_id)
        )
        data = json.loads(result)
        assert data["status"] == "ok"
        assert data["actions"] == 2

        # 2. Raw CDP: Page.getResourceTree
        raw_tool = mcp._tool_manager.get_tool("wavexis_raw_cdp")
        result = await raw_tool.fn(
            RawCDPInput(session_id=session_id, method="Page.getResourceTree")
        )
        data = json.loads(result)
        assert "result" in data

        # 3. Lighthouse audit
        lighthouse_tool = mcp._tool_manager.get_tool("wavexis_lighthouse")
        result = await lighthouse_tool.fn(
            LighthouseInput(
                url="https://example.com",
                session_id=session_id,
                categories=["performance"],
            )
        )
        data = json.loads(result)
        assert "categories" in data
        assert "performance" in data["categories"]

        # 4. Extract structured data
        extract_tool = mcp._tool_manager.get_tool("wavexis_extract")
        result = await extract_tool.fn(
            ExtractInput(
                url="https://example.com",
                schema={"title": "h1"},
                session_id=session_id,
            )
        )
        data = json.loads(result)
        assert "data" in data
        assert data["rows"] >= 1

        # 5. Service worker list
        sw_tool = mcp._tool_manager.get_tool("wavexis_service_worker_list")
        result = await sw_tool.fn(
            ServiceWorkerListInput(session_id=session_id)
        )
        data = json.loads(result)
        assert "workers" in data

    finally:
        close_tool = mcp._tool_manager.get_tool("wavexis_session_close")
        result = await close_tool.fn(SessionCloseInput(session_id=session_id))
        data = json.loads(result)
        assert data["status"] == "ok"
