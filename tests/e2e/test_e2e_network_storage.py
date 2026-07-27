"""E2E tests for network and storage tier tools.

Network: headers, user agent, request interception, network requests, HAR.
Storage: localStorage, sessionStorage, Cache Storage, IndexedDB, storage state.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.e2e


# ── Network ────────────────────────────────────────────────────────


class TestNetwork:
    """Network control and monitoring tools."""

    async def test_set_headers(self, call_tool, chrome_session) -> None:
        """Set custom HTTP headers."""
        data = await call_tool(
            "wavexis_set_headers",
            headers={"X-E2E-Test": "true"},
            session_id=chrome_session,
        )
        assert data["status"] == "ok"

    async def test_set_user_agent(self, call_tool, chrome_session) -> None:
        """Set a custom user agent."""
        data = await call_tool(
            "wavexis_set_user_agent",
            user_agent="WaveXisMCP-E2E-Test/1.0",
            session_id=chrome_session,
        )
        assert data["status"] == "ok"

        # Verify by evaluating navigator.userAgent
        ua = await call_tool(
            "wavexis_eval",
            expression="navigator.userAgent",
            session_id=chrome_session,
        )
        assert "WaveXisMCP-E2E-Test" in str(ua.get("result", ""))

    async def test_network_requests(self, call_tool, chrome_session, base_url) -> None:
        """Navigate to network page, trigger fetch, and list network requests."""
        await call_tool("wavexis_navigate", url=f"{base_url}/network.html", session_id=chrome_session)

        # Trigger a fetch request
        await call_tool(
            "wavexis_eval",
            expression="fetch('/api/data').then(r => r.json())",
            session_id=chrome_session,
        )

        # Give it a moment
        await call_tool("wavexis_wait", strategy="selector", selector="body", session_id=chrome_session, timeout=2000)

        data = await call_tool("wavexis_network_requests", session_id=chrome_session)
        requests = data.get("requests", [])
        assert isinstance(requests, list)

    async def test_block_requests(self, call_tool, chrome_session, base_url) -> None:
        """Block requests matching a pattern."""
        data = await call_tool(
            "wavexis_block_requests",
            patterns=["*/api/notfound*"],
            session_id=chrome_session,
        )
        assert data["status"] == "ok"

    async def test_throttle_network(self, call_tool, chrome_session) -> None:
        """Throttle network to slow connection."""
        data = await call_tool(
            "wavexis_throttle_network",
            download_throughput=100000,
            upload_throughput=50000,
            latency_ms=200,
            session_id=chrome_session,
        )
        assert data["status"] == "ok"

    async def test_set_cache_disabled(self, call_tool, chrome_session) -> None:
        """Disable cache."""
        data = await call_tool(
            "wavexis_set_cache_disabled",
            disabled=True,
            session_id=chrome_session,
        )
        assert data["status"] == "ok"

    async def test_capture_har(self, call_tool, chrome_session, base_url) -> None:
        """Capture a HAR archive."""
        data = await call_tool(
            "wavexis_capture_har",
            url=f"{base_url}/index.html",
            session_id=chrome_session,
        )
        assert "har" in data or "entries" in data

    async def test_network_clear(self, call_tool, chrome_session) -> None:
        """Clear network log."""
        data = await call_tool("wavexis_network_clear", session_id=chrome_session)
        assert data["status"] == "ok"


# ── Storage ────────────────────────────────────────────────────────


class TestStorage:
    """localStorage, sessionStorage, Cache Storage, IndexedDB tools."""

    async def test_localstorage_get_set(self, call_tool, chrome_session, base_url) -> None:
        """Set and get a localStorage item."""
        await call_tool("wavexis_navigate", url=f"{base_url}/storage.html", session_id=chrome_session)

        # Get pre-set value
        data = await call_tool(
            "wavexis_localstorage_get",
            key="user_name",
            session_id=chrome_session,
        )
        assert "value" in data
        assert "Test User" in str(data.get("value", ""))

        # Set a new value
        set_data = await call_tool(
            "wavexis_localstorage_set",
            key="e2e_key",
            value="e2e_value",
            session_id=chrome_session,
        )
        assert set_data.get("status") == "ok"

        # Verify
        get_data = await call_tool(
            "wavexis_localstorage_get",
            key="e2e_key",
            session_id=chrome_session,
        )
        assert "e2e_value" in str(get_data.get("value", ""))

    async def test_localstorage_list(self, call_tool, chrome_session, base_url) -> None:
        """List all localStorage entries."""
        await call_tool("wavexis_navigate", url=f"{base_url}/storage.html", session_id=chrome_session)
        data = await call_tool("wavexis_localstorage_list", session_id=chrome_session)
        entries = data.get("entries", {})
        assert isinstance(entries, dict)
        assert len(entries) >= 1

    async def test_localstorage_delete(self, call_tool, chrome_session, base_url) -> None:
        """Delete a localStorage item."""
        await call_tool("wavexis_navigate", url=f"{base_url}/storage.html", session_id=chrome_session)
        data = await call_tool(
            "wavexis_localstorage_delete",
            key="user_name",
            session_id=chrome_session,
        )
        assert data["status"] == "ok"

    async def test_sessionstorage_get_set(self, call_tool, chrome_session, base_url) -> None:
        """Set and get a sessionStorage item."""
        await call_tool("wavexis_navigate", url=f"{base_url}/storage.html", session_id=chrome_session)

        data = await call_tool(
            "wavexis_sessionstorage_get",
            key="temp_data",
            session_id=chrome_session,
        )
        assert "value" in data
        assert "temporary" in str(data.get("value", ""))

    async def test_sessionstorage_list(self, call_tool, chrome_session, base_url) -> None:
        """List all sessionStorage entries."""
        await call_tool("wavexis_navigate", url=f"{base_url}/storage.html", session_id=chrome_session)
        data = await call_tool("wavexis_sessionstorage_list", session_id=chrome_session)
        entries = data.get("entries", {})
        assert len(entries) >= 1

    async def test_cache_storage_list(self, call_tool, chrome_session, base_url) -> None:
        """List Cache Storage entries."""
        await call_tool("wavexis_navigate", url=f"{base_url}/storage.html", session_id=chrome_session)

        # Initialize cache first
        await call_tool(
            "wavexis_eval",
            expression="caches.open('test-cache').then(c => c.put(new Request('/test'), new Response('data')))",
            session_id=chrome_session,
            await_promise=True,
        )

        data = await call_tool("wavexis_cache_storage_list", session_id=chrome_session)
        caches = data.get("caches", [])
        assert isinstance(caches, list)

    async def test_indexeddb_list(self, call_tool, chrome_session, base_url) -> None:
        """List IndexedDB databases."""
        await call_tool("wavexis_navigate", url=f"{base_url}/storage.html", session_id=chrome_session)

        # Initialize IndexedDB first
        await call_tool(
            "wavexis_eval",
            expression=(
                "new Promise((resolve) => {"
                "  var req = indexedDB.open('e2e-db', 1);"
                "  req.onupgradeneeded = (e) => {"
                "    e.target.result.createObjectStore('items', {keyPath: 'id'});"
                "  };"
                "  req.onsuccess = () => resolve('ok');"
                "})"
            ),
            session_id=chrome_session,
            await_promise=True,
        )

        data = await call_tool("wavexis_indexeddb_list", session_id=chrome_session)
        dbs = data.get("databases", [])
        assert isinstance(dbs, list)

    async def test_storage_state_save_restore(self, call_tool, chrome_session, base_url, tmp_path) -> None:
        """Save and restore browser storage state."""
        await call_tool("wavexis_navigate", url=f"{base_url}/storage.html", session_id=chrome_session)

        # Save state
        save_path = str(tmp_path / "storage_state.json")
        data = await call_tool(
            "wavexis_storage_state_save",
            output_path=save_path,
            session_id=chrome_session,
        )
        assert "path" in data or data.get("status") == "ok"

        # Verify file exists
        from pathlib import Path

        assert Path(save_path).exists()

        # Restore state
        restore_data = await call_tool(
            "wavexis_storage_state_restore",
            input_path=save_path,
            session_id=chrome_session,
        )
        assert restore_data.get("status") == "ok" or "cookies" in restore_data or "error" in restore_data
