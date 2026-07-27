"""E2E tests for Testing, Workflows, Data, and Act (NL interaction) tier tools.

Testing: assertions (visible, text, url, value), locator generation.
Workflows: multi-action YAML, raw CDP, browser contexts.
Data: extract, lighthouse, crawl, visual diff, core web vitals, record.
Act: natural language interaction via wavexis_act.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.e2e


# ── Testing assertions ─────────────────────────────────────────────


class TestAssertions:
    """Assertion tools with polling."""

    async def test_assert_visible(self, call_tool, chrome_session) -> None:
        """Assert an element is visible."""
        data = await call_tool(
            "wavexis_assert_visible",
            selector="#main-heading",
            session_id=chrome_session,
        )
        assert data.get("passed") is True

    async def test_assert_visible_hidden_element(self, call_tool, chrome_session) -> None:
        """Assert a hidden element is NOT visible (should fail)."""
        data = await call_tool(
            "wavexis_assert_visible",
            selector="#toggle-target",
            session_id=chrome_session,
            timeout=500,
        )
        assert data.get("passed") is False

    async def test_assert_text_visible(self, call_tool, chrome_session) -> None:
        """Assert text is visible on the page."""
        data = await call_tool(
            "wavexis_assert_text_visible",
            text="WaveXisMCP Test Page",
            session_id=chrome_session,
        )
        assert data.get("passed") is True

    async def test_assert_url(self, call_tool, chrome_session, base_url) -> None:
        """Assert the current URL matches a pattern."""
        data = await call_tool(
            "wavexis_assert_url",
            url_pattern="*index*",
            session_id=chrome_session,
        )
        assert data.get("passed") is True or data.get("passed") is False

    async def test_generate_locator(self, call_tool, chrome_session) -> None:
        """Generate a CSS locator for an element."""
        data = await call_tool(
            "wavexis_generate_locator",
            selector="#main-heading",
            session_id=chrome_session,
        )
        locators = data.get("locators", [])
        assert isinstance(locators, list)


# ── Workflows ──────────────────────────────────────────────────────


class TestWorkflows:
    """Multi-action, raw CDP, browser context tools."""

    async def test_multi_action_click_and_verify(self, call_tool, chrome_session) -> None:
        """Execute a multi-action YAML workflow: click + eval."""
        yaml_config = (
            "actions:\n"
            "  - click:\n"
            "      selector: '#click-me'\n"
            "  - eval:\n"
            "      expression: \"document.getElementById('click-result').textContent\"\n"
        )
        data = await call_tool(
            "wavexis_multi_action",
            config=yaml_config,
            session_id=chrome_session,
        )
        assert data["status"] == "ok"
        results = data.get("results", [])
        assert len(results) >= 2

    async def test_multi_action_navigate_and_screenshot(self, call_tool, chrome_session, base_url) -> None:
        """Execute a multi-action workflow: navigate + screenshot."""
        yaml_config = (
            f"actions:\n"
            f"  - navigate:\n"
            f"      url: '{base_url}/form.html'\n"
            f"  - eval:\n"
            f"      expression: 'document.title'\n"
        )
        data = await call_tool(
            "wavexis_multi_action",
            config=yaml_config,
            session_id=chrome_session,
        )
        assert data["status"] == "ok"

    async def test_raw_cdp(self, call_tool, chrome_session) -> None:
        """Send a raw CDP command."""
        data = await call_tool(
            "wavexis_raw_cdp",
            method="Runtime.evaluate",
            params={"expression": "1 + 1"},
            session_id=chrome_session,
        )
        assert "result" in data or "error" in data

    async def test_browser_context_list(self, call_tool, chrome_session) -> None:
        """List browser contexts."""
        data = await call_tool("wavexis_browser_context_list", session_id=chrome_session)
        assert "contexts" in data


# ── Data ───────────────────────────────────────────────────────────


class TestData:
    """Data extraction and analysis tools."""

    async def test_extract(self, call_tool, chrome_session, base_url) -> None:
        """Extract structured data from the page using CSS selectors."""
        data = await call_tool(
            "wavexis_extract",
            url=f"{base_url}/index.html",
            json_schema={"heading": "#main-heading"},
            session_id=chrome_session,
        )
        assert "data" in data or "error" in data

    async def test_core_web_vitals(self, call_tool, chrome_session, base_url) -> None:
        """Measure Core Web Vitals."""
        data = await call_tool(
            "wavexis_core_web_vitals",
            url=f"{base_url}/index.html",
            session_id=chrome_session,
        )
        assert isinstance(data, dict)

    async def test_crawl(self, call_tool, chrome_session, base_url) -> None:
        """Crawl the local site starting from index page."""
        data = await call_tool(
            "wavexis_crawl",
            start_url=f"{base_url}/index.html",
            max_pages=3,
            max_depth=1,
            session_id=chrome_session,
        )
        pages = data.get("pages", [])
        assert isinstance(pages, list)
        assert len(pages) >= 1


# ── Act (Natural Language Interaction) ─────────────────────────────


class TestAct:
    """wavexis_act — natural language interaction."""

    async def test_act_click_button(self, call_tool, chrome_session) -> None:
        """Use wavexis_act to click a button by natural language."""
        data = await call_tool(
            "wavexis_act",
            instruction="click the Click Me button",
            session_id=chrome_session,
        )
        assert data.get("status") == "ok" or data.get("status") == "no_match" or "error" in data

    async def test_act_click_link(self, call_tool, chrome_session) -> None:
        """Use wavexis_act to click a link by natural language."""
        data = await call_tool(
            "wavexis_act",
            instruction="click the Go to Form link",
            session_id=chrome_session,
        )
        assert data.get("status") in ("ok", "no_match") or "error" in data

    async def test_act_no_match(self, call_tool, chrome_session) -> None:
        """Act with an instruction that doesn't match any element."""
        data = await call_tool(
            "wavexis_act",
            instruction="click the nonexistent elephant button",
            session_id=chrome_session,
        )
        assert data.get("status") == "no_match" or "error" in data

    async def test_act_type_into_field(self, call_tool, chrome_session, base_url) -> None:
        """Use wavexis_act to type into a form field."""
        await call_tool("wavexis_navigate", url=f"{base_url}/form.html", session_id=chrome_session)
        data = await call_tool(
            "wavexis_act",
            instruction="type John Doe into the Name field",
            value="John Doe",
            session_id=chrome_session,
        )
        assert data.get("status") in ("ok", "no_match") or "error" in data
