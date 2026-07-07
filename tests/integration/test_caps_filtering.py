"""Integration test: verify --caps correctly filters tools."""

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


async def _create_with_caps(caps: str) -> FastMCP:
    """Create a server with the given caps and return it."""
    cm = CapsManager(caps)
    mcp = FastMCP("test")
    sm = SessionManager()

    session.register(mcp, sm)
    navigation.register(mcp, sm)
    capture.register(mcp, sm)
    javascript.register(mcp, sm)
    dom.register(mcp, sm)
    input.register(mcp, sm)
    cookies.register(mcp, sm)
    tabs.register(mcp, sm)
    utility.register(mcp, sm)

    if cm.is_enabled("network"):
        network.register(mcp, sm)
    if cm.is_enabled("storage"):
        storage.register(mcp, sm)
    if cm.is_enabled("emulation"):
        emulation.register(mcp, sm)
    if cm.is_enabled("a11y"):
        a11y.register(mcp, sm)
    if cm.is_enabled("interactions"):
        interactions.register(mcp, sm)
    if cm.is_enabled("devtools"):
        devtools.register(mcp, sm)
    if cm.is_enabled("vision"):
        vision.register(mcp, sm)
    if cm.is_enabled("video"):
        video.register(mcp, sm)
    if cm.is_enabled("testing"):
        testing.register(mcp, sm)
    if cm.is_enabled("workflows"):
        workflows.register(mcp, sm)
    if cm.is_enabled("data"):
        data.register(mcp, sm)
    if cm.is_enabled("experimental"):
        experimental.register(mcp, sm)

    return mcp


@pytest.mark.integration
async def test_core_only() -> None:
    """Core caps should only register core tools."""
    mcp = await _create_with_caps("core")
    tools = await mcp.list_tools()
    tool_names = {t.name for t in tools}

    assert "wavexis_screenshot" in tool_names
    assert "wavexis_set_headers" not in tool_names
    assert "wavexis_a11y_snapshot" not in tool_names
    assert "wavexis_perf_metrics" not in tool_names


@pytest.mark.integration
async def test_core_plus_network() -> None:
    """core,network should register core + network tools."""
    mcp = await _create_with_caps("core,network")
    tools = await mcp.list_tools()
    tool_names = {t.name for t in tools}

    assert "wavexis_screenshot" in tool_names
    assert "wavexis_set_headers" in tool_names
    assert "wavexis_a11y_snapshot" not in tool_names


@pytest.mark.integration
async def test_all_caps() -> None:
    """all should register every tier."""
    mcp = await _create_with_caps("all")
    tools = await mcp.list_tools()
    tool_names = {t.name for t in tools}

    assert "wavexis_screenshot" in tool_names
    assert "wavexis_set_headers" in tool_names
    assert "wavexis_a11y_snapshot" in tool_names
    assert "wavexis_perf_metrics" in tool_names
    assert "wavexis_service_worker_list" in tool_names


@pytest.mark.integration
async def test_invalid_tier_warned() -> None:
    """Invalid tier names should be warned and skipped."""
    cm = CapsManager("core,faketier,anotherfake")
    assert "faketier" not in cm.enabled_tiers()
    assert "anotherfake" not in cm.enabled_tiers()
    assert "core" in cm.enabled_tiers()
