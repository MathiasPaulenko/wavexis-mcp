"""Emulation tools for WaveXisMCP.

Provides tools for emulating device characteristics: viewport,
geolocation, timezone, dark mode, locale, CPU throttling,
touch events, and sensor values.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from wavexis.config import SensorParams

from wavexis_mcp.formatter import format_error, format_json_response
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

_SENSOR_TYPE_MAP: dict[str, str] = {
    "orientation": "device-orientation",
    "motion": "device-orientation",
    "light": "ambient-light",
    "proximity": "ambient-light",
}


def register(mcp: FastMCP, session_manager: SessionManager) -> None:
    """Register all emulation tools on the FastMCP server.

    Args:
        mcp: The FastMCP server instance.
        session_manager: The shared session manager.
    """

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ))
    async def wavexis_emulate_device(input: EmulateDeviceInput) -> str:
        """Emulate a specific device (iphone-15, pixel-8, etc.).

        Args:
            input: Device emulation parameters.

        Returns:
            JSON string with status ``"ok"`` and ``device``.
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.emulate_device(input.device)
            return format_json_response({"status": "ok", "device": input.device})
        except Exception as e:
            return format_error("wavexis_emulate_device", e)

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ))
    async def wavexis_set_viewport(input: SetViewportInput) -> str:
        """Set a custom viewport size and scale factor.

        Args:
            input: Viewport parameters (width, height, scale factor).

        Returns:
            JSON string with status ``"ok"`` and viewport dimensions.
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.set_viewport(
                input.width, input.height, input.device_scale_factor
            )
            return format_json_response({
                "status": "ok",
                "width": input.width,
                "height": input.height,
                "device_scale_factor": input.device_scale_factor,
            })
        except Exception as e:
            return format_error("wavexis_set_viewport", e)

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ))
    async def wavexis_set_geolocation(input: SetGeolocationInput) -> str:
        """Override the browser geolocation.

        Args:
            input: Geolocation parameters (latitude, longitude, accuracy).

        Returns:
            JSON string with status ``"ok"`` and coordinates.
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.set_geolocation(
                input.latitude, input.longitude, input.accuracy
            )
            return format_json_response({
                "status": "ok",
                "latitude": input.latitude,
                "longitude": input.longitude,
            })
        except Exception as e:
            return format_error("wavexis_set_geolocation", e)

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ))
    async def wavexis_set_timezone(input: SetTimezoneInput) -> str:
        """Override the browser timezone.

        Args:
            input: Timezone parameters.

        Returns:
            JSON string with status ``"ok"`` and ``timezone``.
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.set_timezone(input.timezone)
            return format_json_response({"status": "ok", "timezone": input.timezone})
        except Exception as e:
            return format_error("wavexis_set_timezone", e)

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ))
    async def wavexis_set_dark_mode(input: SetDarkModeInput) -> str:
        """Enable or disable dark mode emulation.

        Args:
            input: Dark mode parameters.

        Returns:
            JSON string with status ``"ok"`` and ``dark_mode``.
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.set_dark_mode(input.enabled)
            return format_json_response({"status": "ok", "dark_mode": input.enabled})
        except Exception as e:
            return format_error("wavexis_set_dark_mode", e)

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ))
    async def wavexis_set_locale(input: SetLocaleInput) -> str:
        """Override the browser locale.

        Args:
            input: Locale parameters.

        Returns:
            JSON string with status ``"ok"`` and ``locale``.
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.set_locale(input.locale)
            return format_json_response({"status": "ok", "locale": input.locale})
        except Exception as e:
            return format_error("wavexis_set_locale", e)

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ))
    async def wavexis_set_cpu_throttle(input: SetCPUThrottleInput) -> str:
        """Enable CPU throttling at a given multiplier.

        Args:
            input: CPU throttle parameters (rate).

        Returns:
            JSON string with status ``"ok"`` and ``rate``.
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.set_cpu_throttle(input.rate)
            return format_json_response({"status": "ok", "rate": input.rate})
        except Exception as e:
            return format_error("wavexis_set_cpu_throttle", e)

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ))
    async def wavexis_set_touch_emulation(input: SetTouchEmulationInput) -> str:
        """Enable or disable touch event emulation.

        Args:
            input: Touch emulation parameters.

        Returns:
            JSON string with status ``"ok"`` and ``touch_emulation``.
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.set_touch_emulation(input.enabled)
            return format_json_response({"status": "ok", "touch_emulation": input.enabled})
        except Exception as e:
            return format_error("wavexis_set_touch_emulation", e)

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ))
    async def wavexis_set_sensors(input: SetSensorsInput) -> str:
        """Override sensor values (orientation, motion, light, proximity).

        Args:
            input: Sensor parameters (sensor_type, values).

        Returns:
            JSON string with status ``"ok"``, ``sensor_type``, and ``values``.
        """
        try:
            session = session_manager.get(input.session_id)
            sensor_type = _SENSOR_TYPE_MAP.get(
                input.sensor_type, input.sensor_type
            )
            params = SensorParams(type=sensor_type, values=input.values)
            await session.backend.set_sensors(params)
            return format_json_response({
                "status": "ok",
                "sensor_type": input.sensor_type,
                "values": input.values,
            })
        except Exception as e:
            return format_error("wavexis_set_sensors", e)
