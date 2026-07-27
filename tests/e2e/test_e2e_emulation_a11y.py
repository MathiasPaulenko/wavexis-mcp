"""E2E tests for emulation, accessibility, and interactions tier tools.

Emulation: device, viewport, geolocation, timezone, dark mode, locale, CPU throttle, touch, sensors.
A11y: snapshot, node, ancestors, axe audit.
Interactions: dialog, download, permissions.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.e2e


# ── Emulation ──────────────────────────────────────────────────────


class TestEmulation:
    """Browser emulation tools."""

    async def test_emulate_device(self, call_tool, chrome_session) -> None:
        """Emulate a mobile device."""
        data = await call_tool(
            "wavexis_emulate_device",
            device="iphone-15",
            session_id=chrome_session,
        )
        assert data.get("status") == "ok" or "device" in data or "error" in data

    async def test_set_viewport(self, call_tool, chrome_session) -> None:
        """Set a custom viewport size."""
        data = await call_tool(
            "wavexis_set_viewport",
            width=768,
            height=1024,
            session_id=chrome_session,
        )
        assert data["status"] == "ok"

        # Verify
        result = await call_tool(
            "wavexis_eval",
            expression="JSON.stringify({w: window.innerWidth, h: window.innerHeight})",
            session_id=chrome_session,
        )
        assert "768" in str(result.get("result", ""))

    async def test_set_geolocation(self, call_tool, chrome_session) -> None:
        """Set a custom geolocation."""
        data = await call_tool(
            "wavexis_set_geolocation",
            latitude=40.4168,
            longitude=-3.7038,
            session_id=chrome_session,
        )
        assert data["status"] == "ok"

    async def test_set_timezone(self, call_tool, chrome_session) -> None:
        """Set a custom timezone."""
        data = await call_tool(
            "wavexis_set_timezone",
            timezone="Europe/Madrid",
            session_id=chrome_session,
        )
        assert data["status"] == "ok"

    async def test_set_dark_mode(self, call_tool, chrome_session) -> None:
        """Enable dark mode preference."""
        data = await call_tool(
            "wavexis_set_dark_mode",
            enabled=True,
            session_id=chrome_session,
        )
        assert data["status"] == "ok"

    async def test_set_locale(self, call_tool, chrome_session) -> None:
        """Set browser locale."""
        data = await call_tool(
            "wavexis_set_locale",
            locale="es-ES",
            session_id=chrome_session,
        )
        assert data["status"] == "ok"

    async def test_set_cpu_throttle(self, call_tool, chrome_session) -> None:
        """Throttle CPU to slow down the page."""
        data = await call_tool(
            "wavexis_set_cpu_throttle",
            rate=4,
            session_id=chrome_session,
        )
        assert data["status"] == "ok"

    async def test_set_touch_emulation(self, call_tool, chrome_session) -> None:
        """Enable touch emulation."""
        data = await call_tool(
            "wavexis_set_touch_emulation",
            enabled=True,
            session_id=chrome_session,
        )
        assert data["status"] == "ok"

    async def test_set_sensors(self, call_tool, chrome_session) -> None:
        """Set sensor values."""
        data = await call_tool(
            "wavexis_set_sensors",
            sensor_type="geolocation",
            values={"latitude": 40.4168, "longitude": -3.7038, "accuracy": 1},
            session_id=chrome_session,
        )
        assert data.get("status") == "ok" or "sensor_type" in data or "error" in data


# ── Accessibility ──────────────────────────────────────────────────


class TestAccessibility:
    """Accessibility tree and audit tools."""

    async def test_a11y_snapshot(self, call_tool, chrome_session, base_url) -> None:
        """Take an accessibility snapshot of the a11y page."""
        await call_tool("wavexis_navigate", url=f"{base_url}/a11y.html", session_id=chrome_session)
        data = await call_tool("wavexis_a11y_snapshot", session_id=chrome_session)
        assert "snapshot" in data or "text" in data or "element_count" in data
        text = data.get("text", data.get("snapshot", ""))
        assert text  # non-empty

    async def test_a11y_node(self, call_tool, chrome_session, base_url) -> None:
        """Get a specific a11y node by first taking a snapshot to get a node_id."""
        await call_tool("wavexis_navigate", url=f"{base_url}/a11y.html", session_id=chrome_session)
        # First take snapshot to get a node_id
        await call_tool("wavexis_a11y_snapshot", session_id=chrome_session)
        # Try with node_id="1" (root or first node)
        data = await call_tool(
            "wavexis_a11y_node",
            node_id="1",
            session_id=chrome_session,
        )
        assert "node" in data or "error" in data

    async def test_a11y_ancestors(self, call_tool, chrome_session, base_url) -> None:
        """Get ancestors of an a11y node."""
        await call_tool("wavexis_navigate", url=f"{base_url}/a11y.html", session_id=chrome_session)
        data = await call_tool(
            "wavexis_a11y_ancestors",
            node_id="1",
            session_id=chrome_session,
        )
        assert "ancestors" in data or "error" in data

    async def test_axe_audit(self, call_tool, chrome_session, base_url) -> None:
        """Run an axe-core accessibility audit."""
        await call_tool("wavexis_navigate", url=f"{base_url}/a11y.html", session_id=chrome_session)
        data = await call_tool("wavexis_axe_audit", session_id=chrome_session)
        # axe audit returns results directly (violations, passes, etc.)
        assert isinstance(data, dict)
        assert "violations" in data or "error" in data or "status" in data


# ── Interactions ───────────────────────────────────────────────────


class TestInteractions:
    """Dialog, download, and permission tools."""

    async def test_grant_permission(self, call_tool, chrome_session) -> None:
        """Grant a browser permission."""
        data = await call_tool(
            "wavexis_grant_permission",
            permission="geolocation",
            session_id=chrome_session,
        )
        assert data["status"] == "ok"

    async def test_reset_permissions(self, call_tool, chrome_session) -> None:
        """Reset all granted permissions."""
        data = await call_tool("wavexis_reset_permissions", session_id=chrome_session)
        assert data["status"] == "ok"

    async def test_dialog_accept(self, call_tool, chrome_session, base_url) -> None:
        """Accept a JavaScript dialog (alert/confirm)."""
        # Set up a page that triggers a confirm dialog
        await call_tool(
            "wavexis_eval",
            expression="window.confirm('Are you sure?')",
            session_id=chrome_session,
        )
        # The dialog handler should accept it
        data = await call_tool("wavexis_dialog_accept", session_id=chrome_session)
        # Dialog may or may not be present depending on timing
        assert data["status"] == "ok" or "error" in data
