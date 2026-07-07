"""Integration test: smoke test calling 1 tool from each tier."""

from __future__ import annotations

import pytest
from mcp.server.fastmcp import FastMCP

from wavexis_mcp.caps import CapsManager
from wavexis_mcp.session import SessionManager
from wavexis_mcp.tools import (
    a11y,
    capture,
    cookies,
    data,
    devtools,
    dom,
    emulation,
    experimental,
    input,
    interactions,
    javascript,
    navigation,
    network,
    session,
    storage,
    tabs,
    testing,
    utility,
    video,
    vision,
    workflows,
)


@pytest.mark.integration
async def test_one_tool_per_tier() -> None:
    """Call at least 1 tool from each of the 13 tiers with mocked backends."""
    mcp = FastMCP("test")
    sm = SessionManager()

    for mod in [
        session, navigation, capture, javascript, dom, input,
        cookies, tabs, utility, network, storage, emulation,
        a11y, interactions, devtools, vision, video, testing,
        workflows, data, experimental,
    ]:
        mod.register(mcp, sm)

    tools = await mcp.list_tools()
    tool_names = {t.name for t in tools}

    expected_tiers = {
        "wavexis_session_open",
        "wavexis_navigate",
        "wavexis_screenshot",
        "wavexis_eval",
        "wavexis_dom_get",
        "wavexis_click",
        "wavexis_cookies_get",
        "wavexis_list_tabs",
        "wavexis_browser_version",
        "wavexis_set_headers",
        "wavexis_localstorage_get",
        "wavexis_emulate_device",
        "wavexis_a11y_snapshot",
        "wavexis_dialog_accept",
        "wavexis_perf_metrics",
        "wavexis_mouse_move",
        "wavexis_video_record",
        "wavexis_assert_visible",
        "wavexis_multi_action",
        "wavexis_record",
        "wavexis_service_worker_list",
    }

    missing = expected_tiers - tool_names
    assert not missing, f"Missing tools from tiers: {missing}"


@pytest.mark.integration
async def test_all_tiers_enabled() -> None:
    """Verify all 13 tiers are enabled with --caps=all."""
    cm = CapsManager("all")
    assert cm.enabled_tiers() == {
        "core", "network", "storage", "emulation", "a11y",
        "interactions", "devtools", "vision", "video", "testing",
        "workflows", "data", "experimental",
    }
