"""Unit tests for emulation tools."""

from __future__ import annotations

import json

import pytest

from wavexis_mcp.models import (
    EmulateDeviceInput,
    SetCPUThrottleInput,
    SetDarkModeInput,
    SetGeolocationInput,
    SetLocaleInput,
    SetSensorsInput,
    SetTimezoneInput,
    SetTouchEmulationInput,
    SetViewportInput,
)
from wavexis_mcp.session import SessionManager


@pytest.mark.unit
async def test_emulate_device(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.emulation import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_emulate_device")
    result = await tool.fn(
        EmulateDeviceInput(device="iphone-15", session_id=mock_session_id)
    )
    data = json.loads(result)
    assert data["status"] == "ok"
    assert data["device"] == "iphone-15"


@pytest.mark.unit
async def test_set_viewport(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.emulation import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_set_viewport")
    result = await tool.fn(
        SetViewportInput(
            width=1920, height=1080, device_scale_factor=2.0, session_id=mock_session_id
        )
    )
    data = json.loads(result)
    assert data["status"] == "ok"
    assert data["width"] == 1920
    assert data["height"] == 1080


@pytest.mark.unit
async def test_set_geolocation(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.emulation import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_set_geolocation")
    result = await tool.fn(
        SetGeolocationInput(
            latitude=37.7749, longitude=-122.4194, session_id=mock_session_id
        )
    )
    data = json.loads(result)
    assert data["status"] == "ok"
    assert data["latitude"] == 37.7749


@pytest.mark.unit
async def test_set_timezone(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.emulation import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_set_timezone")
    result = await tool.fn(
        SetTimezoneInput(timezone="America/New_York", session_id=mock_session_id)
    )
    data = json.loads(result)
    assert data["status"] == "ok"
    assert data["timezone"] == "America/New_York"


@pytest.mark.unit
async def test_set_dark_mode(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.emulation import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_set_dark_mode")
    result = await tool.fn(
        SetDarkModeInput(enabled=True, session_id=mock_session_id)
    )
    data = json.loads(result)
    assert data["status"] == "ok"
    assert data["dark_mode"] is True


@pytest.mark.unit
async def test_set_locale(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.emulation import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_set_locale")
    result = await tool.fn(
        SetLocaleInput(locale="fr-FR", session_id=mock_session_id)
    )
    data = json.loads(result)
    assert data["status"] == "ok"
    assert data["locale"] == "fr-FR"


@pytest.mark.unit
async def test_set_cpu_throttle(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.emulation import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_set_cpu_throttle")
    result = await tool.fn(
        SetCPUThrottleInput(rate=4.0, session_id=mock_session_id)
    )
    data = json.loads(result)
    assert data["status"] == "ok"
    assert data["rate"] == 4.0


@pytest.mark.unit
async def test_set_touch_emulation(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.emulation import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_set_touch_emulation")
    result = await tool.fn(
        SetTouchEmulationInput(enabled=True, session_id=mock_session_id)
    )
    data = json.loads(result)
    assert data["status"] == "ok"
    assert data["touch_emulation"] is True


@pytest.mark.unit
async def test_set_sensors(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.emulation import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_set_sensors")
    result = await tool.fn(
        SetSensorsInput(
            sensor_type="orientation",
            values={"alpha": 0, "beta": 90, "gamma": 0},
            session_id=mock_session_id,
        )
    )
    data = json.loads(result)
    assert data["status"] == "ok"
    assert data["sensor_type"] == "orientation"
