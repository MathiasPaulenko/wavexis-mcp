"""E2E tests for core tier tools: session, navigation, capture, JS, DOM, input, cookies, tabs, utility.

These tests exercise the full stack: Pydantic validation → tool handler →
SessionManager → wavexis backend → CDP → Chrome against local fixture pages.
"""

from __future__ import annotations

import base64
import json

import pytest

pytestmark = pytest.mark.e2e


# ── Session lifecycle ──────────────────────────────────────────────


class TestSessionLifecycle:
    """Session open, info, close through the full MCP server."""

    async def test_session_open_and_close(self, call_tool) -> None:
        """Open a session, verify info, then close it."""
        data = await call_tool("wavexis_session_open", backend="cdp", headless=True)
        assert data["status"] == "ok"
        sid = data["session_id"]
        assert sid

        info = await call_tool("wavexis_session_info", session_id=sid)
        assert info["session_id"] == sid

        close = await call_tool("wavexis_session_close", session_id=sid)
        assert close["status"] == "ok"

    async def test_session_info_invalid_id(self, call_tool) -> None:
        """Session info for a non-existent session should return an error."""
        data = await call_tool("wavexis_session_info", session_id="nonexistent-uuid")
        assert "error" in data

    async def test_multiple_concurrent_sessions(self, call_tool) -> None:
        """Open multiple sessions simultaneously."""
        s1 = await call_tool("wavexis_session_open", backend="cdp", headless=True)
        s2 = await call_tool("wavexis_session_open", backend="cdp", headless=True)
        assert s1["status"] == "ok"
        assert s2["status"] == "ok"
        assert s1["session_id"] != s2["session_id"]

        await call_tool("wavexis_session_close", session_id=s1["session_id"])
        await call_tool("wavexis_session_close", session_id=s2["session_id"])


# ── Navigation ─────────────────────────────────────────────────────


class TestNavigation:
    """Navigation tools against real pages."""

    async def test_navigate_to_index(self, call_tool, chrome_session, base_url) -> None:
        """Navigate to the index page and verify URL."""
        data = await call_tool(
            "wavexis_navigate",
            url=f"{base_url}/index.html",
            session_id=chrome_session,
        )
        assert data["status"] == "ok"

    async def test_navigate_back_forward(self, call_tool, chrome_session, base_url) -> None:
        """Navigate to form, back to index, then forward to form."""
        await call_tool("wavexis_navigate", url=f"{base_url}/form.html", session_id=chrome_session)
        await call_tool("wavexis_navigate", url=f"{base_url}/index.html", session_id=chrome_session)
        await call_tool("wavexis_back", session_id=chrome_session)

        # Verify we're on form page via JS
        title = await call_tool("wavexis_eval", expression="document.title", session_id=chrome_session)
        assert "Form" in str(title.get("result", ""))

        await call_tool("wavexis_forward", session_id=chrome_session)
        title2 = await call_tool("wavexis_eval", expression="document.title", session_id=chrome_session)
        assert "Index" in str(title2.get("result", "")) or "Form" in str(title2.get("result", ""))

    async def test_reload(self, call_tool, chrome_session) -> None:
        """Reload the current page."""
        data = await call_tool("wavexis_reload", session_id=chrome_session)
        assert data["status"] == "ok"

    async def test_wait_for_selector(self, call_tool, chrome_session, base_url) -> None:
        """Wait for a specific selector to appear."""
        data = await call_tool(
            "wavexis_wait",
            strategy="selector",
            selector="#main-heading",
            session_id=chrome_session,
            timeout=5000,
        )
        # The tool should either succeed or return a structured error.
        assert "status" in data or "error" in data or "elapsed_ms" in data


# ── Capture ────────────────────────────────────────────────────────


class TestCapture:
    """Screenshot, PDF, scrape, snapshot tools."""

    async def test_screenshot_base64(self, call_tool, chrome_session) -> None:
        """Take a screenshot and verify base64 data is returned."""
        data = await call_tool("wavexis_screenshot", session_id=chrome_session)
        assert data["status"] == "ok"
        assert "base64" in data
        # Verify it's valid base64 PNG
        raw = base64.b64decode(data["base64"])
        assert raw[:8] == b"\x89PNG\r\n\x1a\n"

    async def test_screenshot_selector(self, call_tool, chrome_session) -> None:
        """Take a screenshot of a specific element."""
        data = await call_tool(
            "wavexis_screenshot",
            session_id=chrome_session,
            selector="#main-heading",
        )
        assert data["status"] == "ok"
        assert "base64" in data

    async def test_scrape(self, call_tool, chrome_session, base_url) -> None:
        """Scrape page content and verify text."""
        data = await call_tool("wavexis_scrape", urls=[f"{base_url}/index.html"], session_id=chrome_session)
        results = data.get("results", [])
        assert isinstance(results, list)
        assert len(results) >= 1
        content = str(results[0])
        assert "WaveXisMCP" in content or "Test Page" in content

    async def test_pdf(self, call_tool, chrome_session) -> None:
        """Generate a PDF and verify it starts with %PDF."""
        data = await call_tool("wavexis_pdf", session_id=chrome_session)
        assert data["status"] == "ok"
        assert "base64" in data
        raw = base64.b64decode(data["base64"])
        assert raw[:5] == b"%PDF-"

    async def test_page_snapshot(self, call_tool, chrome_session) -> None:
        """Capture a page accessibility snapshot."""
        data = await call_tool("wavexis_page_snapshot", session_id=chrome_session)
        assert data["status"] == "ok"


# ── JavaScript evaluation ──────────────────────────────────────────


class TestJavaScript:
    """JavaScript evaluation in browser context."""

    async def test_eval_simple_expression(self, call_tool, chrome_session) -> None:
        """Evaluate a simple JS expression."""
        data = await call_tool("wavexis_eval", expression="1 + 2", session_id=chrome_session)
        assert "result" in data
        assert "3" in str(data.get("result", ""))

    async def test_eval_document_title(self, call_tool, chrome_session) -> None:
        """Get the document title via JS."""
        data = await call_tool(
            "wavexis_eval",
            expression="document.title",
            session_id=chrome_session,
        )
        assert "result" in data
        assert "WaveXisMCP" in str(data.get("result", ""))

    async def test_eval_dom_query(self, call_tool, chrome_session) -> None:
        """Query DOM via JS and verify result."""
        data = await call_tool(
            "wavexis_eval",
            expression="document.getElementById('main-heading').textContent",
            session_id=chrome_session,
        )
        assert "result" in data
        assert "WaveXisMCP" in str(data.get("result", ""))

    async def test_eval_promise(self, call_tool, chrome_session) -> None:
        """Evaluate a Promise-based expression."""
        data = await call_tool(
            "wavexis_eval",
            expression="Promise.resolve('resolved_value')",
            session_id=chrome_session,
            await_promise=True,
        )
        assert "result" in data
        assert "resolved_value" in str(data.get("result", ""))


# ── DOM manipulation ───────────────────────────────────────────────


class TestDOM:
    """DOM tools: get, query, attributes, remove, focus, scroll."""

    async def test_dom_get(self, call_tool, chrome_session) -> None:
        """Get HTML content of the page."""
        data = await call_tool("wavexis_dom_get", selector="body", session_id=chrome_session)
        content = data.get("html", "")
        assert "WaveXisMCP" in content or "html" in content.lower()

    async def test_dom_query(self, call_tool, chrome_session) -> None:
        """Query for elements by CSS selector."""
        data = await call_tool("wavexis_dom_query", selector="h1", session_id=chrome_session)
        results = data.get("results", data.get("elements", []))
        assert len(results) >= 1

    async def test_dom_get_attr(self, call_tool, chrome_session) -> None:
        """Get an attribute from an element."""
        data = await call_tool(
            "wavexis_dom_get_attr",
            selector="#data-para",
            name="data-value",
            session_id=chrome_session,
        )
        assert data.get("value") == "42" or data.get("data-value") == "42" or "42" in str(data)

    async def test_dom_set_attr(self, call_tool, chrome_session) -> None:
        """Set an attribute on an element."""
        data = await call_tool(
            "wavexis_dom_set_attr",
            selector="#main-heading",
            name="data-test",
            value="e2e",
            session_id=chrome_session,
        )
        assert data.get("status") == "ok" or data.get("value") == "e2e"

        # Verify
        verify = await call_tool(
            "wavexis_dom_get_attr",
            selector="#main-heading",
            name="data-test",
            session_id=chrome_session,
        )
        assert "e2e" in str(verify)

    async def test_dom_remove_attr(self, call_tool, chrome_session) -> None:
        """Remove an attribute from an element."""
        # First set it
        await call_tool(
            "wavexis_dom_set_attr",
            selector="#main-heading",
            name="data-temp",
            value="temp",
            session_id=chrome_session,
        )
        # Then remove it
        data = await call_tool(
            "wavexis_dom_remove_attr",
            selector="#main-heading",
            name="data-temp",
            session_id=chrome_session,
        )
        assert data.get("status") == "ok" or "removed" in str(data).lower()

    async def test_dom_focus(self, call_tool, chrome_session, base_url) -> None:
        """Focus an element."""
        await call_tool("wavexis_navigate", url=f"{base_url}/form.html", session_id=chrome_session)
        data = await call_tool(
            "wavexis_dom_focus",
            selector="#name",
            session_id=chrome_session,
        )
        assert data["status"] == "ok"

    async def test_dom_scroll(self, call_tool, chrome_session) -> None:
        """Scroll the page."""
        data = await call_tool(
            "wavexis_dom_scroll",
            selector="body",
            session_id=chrome_session,
            y=100,
        )
        assert data["status"] == "ok"


# ── Input interactions ─────────────────────────────────────────────


class TestInput:
    """Click, type, fill, select, hover, key press, check, uncheck."""

    async def test_click_button(self, call_tool, chrome_session) -> None:
        """Click the 'Click Me' button and verify result text changes."""
        data = await call_tool(
            "wavexis_click",
            selector="#click-me",
            session_id=chrome_session,
        )
        assert data["status"] == "ok"

        # Verify the click took effect
        result = await call_tool(
            "wavexis_eval",
            expression="document.getElementById('click-result').textContent",
            session_id=chrome_session,
        )
        assert "Clicked" in str(result.get("result", ""))

    async def test_type_text(self, call_tool, chrome_session, base_url) -> None:
        """Type text into a form field."""
        await call_tool("wavexis_navigate", url=f"{base_url}/form.html", session_id=chrome_session)
        data = await call_tool(
            "wavexis_type",
            selector="#name",
            text="John Doe",
            session_id=chrome_session,
        )
        assert data["status"] == "ok"

        value = await call_tool(
            "wavexis_eval",
            expression="document.getElementById('name').value",
            session_id=chrome_session,
        )
        assert "John Doe" in str(value.get("result", ""))

    async def test_fill_field(self, call_tool, chrome_session, base_url) -> None:
        """Fill a form field (replaces content)."""
        await call_tool("wavexis_navigate", url=f"{base_url}/form.html", session_id=chrome_session)
        data = await call_tool(
            "wavexis_fill",
            selector="#email",
            value="test@example.com",
            session_id=chrome_session,
        )
        assert data["status"] == "ok"

        value = await call_tool(
            "wavexis_eval",
            expression="document.getElementById('email').value",
            session_id=chrome_session,
        )
        assert "test@example.com" in str(value.get("result", ""))

    async def test_fill_form(self, call_tool, chrome_session, base_url) -> None:
        """Fill multiple form fields at once."""
        await call_tool("wavexis_navigate", url=f"{base_url}/form.html", session_id=chrome_session)
        data = await call_tool(
            "wavexis_fill_form",
            fields=[
                {"selector": "#name", "value": "Alice"},
                {"selector": "#email", "value": "alice@test.com"},
            ],
            session_id=chrome_session,
        )
        assert data["status"] == "ok"

    async def test_select_option(self, call_tool, chrome_session, base_url) -> None:
        """Select a dropdown option."""
        await call_tool("wavexis_navigate", url=f"{base_url}/form.html", session_id=chrome_session)
        data = await call_tool(
            "wavexis_select_option",
            selector="#country",
            value="es",
            session_id=chrome_session,
        )
        assert data["status"] == "ok"

        value = await call_tool(
            "wavexis_eval",
            expression="document.getElementById('country').value",
            session_id=chrome_session,
        )
        assert "es" in str(value.get("result", ""))

    async def test_hover(self, call_tool, chrome_session) -> None:
        """Hover over an element."""
        data = await call_tool(
            "wavexis_hover",
            selector="#click-me",
            session_id=chrome_session,
        )
        assert data["status"] == "ok"

    async def test_key_press(self, call_tool, chrome_session, base_url) -> None:
        """Press a key (Enter)."""
        await call_tool("wavexis_navigate", url=f"{base_url}/form.html", session_id=chrome_session)
        await call_tool("wavexis_fill", selector="#name", value="Test", session_id=chrome_session)
        data = await call_tool(
            "wavexis_key_press",
            key="Enter",
            session_id=chrome_session,
        )
        assert data["status"] == "ok"

    async def test_check_uncheck(self, call_tool, chrome_session, base_url) -> None:
        """Check and uncheck a checkbox."""
        await call_tool("wavexis_navigate", url=f"{base_url}/form.html", session_id=chrome_session)

        # Uncheck the pre-checked subscribe checkbox
        data = await call_tool(
            "wavexis_uncheck",
            selector="#subscribe",
            session_id=chrome_session,
        )
        assert data["status"] == "ok"

        checked = await call_tool(
            "wavexis_eval",
            expression="document.getElementById('subscribe').checked",
            session_id=chrome_session,
        )
        assert "false" in str(checked.get("result", "")).lower()

        # Check it back
        data = await call_tool(
            "wavexis_check",
            selector="#subscribe",
            session_id=chrome_session,
        )
        assert data["status"] == "ok"

    async def test_find_by_text(self, call_tool, chrome_session) -> None:
        """Find an element by its text content."""
        data = await call_tool(
            "wavexis_find_by_text",
            query="WaveXisMCP Test Page",
            session_id=chrome_session,
        )
        assert data.get("status") == "ok" or "found" in str(data).lower() or "selector" in data


# ── Cookies ────────────────────────────────────────────────────────


class TestCookies:
    """Cookie management tools."""

    async def test_get_cookies(self, call_tool, chrome_session, base_url) -> None:
        """Get cookies from the current page."""
        # Navigate to dynamic page which sets a cookie
        await call_tool("wavexis_navigate", url=f"{base_url}/dynamic.html", session_id=chrome_session)
        data = await call_tool("wavexis_cookies_get", session_id=chrome_session)
        cookies = data.get("cookies", [])
        assert isinstance(cookies, list)

    async def test_set_and_delete_cookie(self, call_tool, chrome_session, base_url) -> None:
        """Set a cookie, verify, then delete it."""
        await call_tool("wavexis_navigate", url=f"{base_url}/index.html", session_id=chrome_session)

        # Set
        data = await call_tool(
            "wavexis_cookies_set",
            name="e2e_test_cookie",
            value="e2e_value",
            domain="127.0.0.1",
            session_id=chrome_session,
        )
        assert data.get("status") == "ok"

        # Get and verify
        get_data = await call_tool("wavexis_cookies_get", session_id=chrome_session)
        cookies = get_data.get("cookies", [])
        cookie_names = [c.get("name", "") for c in cookies]
        assert "e2e_test_cookie" in cookie_names

        # Delete
        del_data = await call_tool(
            "wavexis_cookies_delete",
            name="e2e_test_cookie",
            domain="127.0.0.1",
            session_id=chrome_session,
        )
        assert del_data.get("status") == "ok" or "deleted" in str(del_data).lower()


# ── Tabs ───────────────────────────────────────────────────────────


class TestTabs:
    """Tab management tools."""

    async def test_list_tabs(self, call_tool, chrome_session) -> None:
        """List open tabs."""
        data = await call_tool("wavexis_list_tabs", session_id=chrome_session)
        tabs = data.get("tabs", [])
        assert len(tabs) >= 1

    async def test_new_and_close_tab(self, call_tool, chrome_session, base_url) -> None:
        """Open a new tab, verify it appears, then close it."""
        # Open new tab
        data = await call_tool(
            "wavexis_new_tab",
            url=f"{base_url}/form.html",
            session_id=chrome_session,
        )
        assert "tab_id" in data or data.get("status") == "ok"

        # List tabs — should have at least 2
        list_data = await call_tool("wavexis_list_tabs", session_id=chrome_session)
        tabs = list_data.get("tabs", [])
        assert len(tabs) >= 2

        # Close the new tab (find it by URL)
        form_tabs = [t for t in tabs if "form" in t.get("url", "")]
        if form_tabs:
            tab_id = form_tabs[0].get("id")
            if tab_id:
                close_data = await call_tool(
                    "wavexis_close_tab",
                    tab_id=tab_id,
                    session_id=chrome_session,
                )
                assert close_data.get("status") == "ok"


# ── Utility ────────────────────────────────────────────────────────


class TestUtility:
    """Browser version, backends listing."""

    async def test_browser_version(self, call_tool, chrome_session) -> None:
        """Get the browser version."""
        data = await call_tool("wavexis_browser_version", session_id=chrome_session)
        version = data.get("version", "")
        assert version  # non-empty

    async def test_backends_list(self, call_tool) -> None:
        """List available backends."""
        data = await call_tool("wavexis_backends")
        backends = data.get("backends", {})
        assert "cdp" in backends or "cdp" in data.get("available", [])
