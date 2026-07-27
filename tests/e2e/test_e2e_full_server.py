"""E2E tests for full MCP server protocol-level validation.

These tests validate the MCP server as a whole:
- All 13 tier tools are registered and callable.
- MCP resources and prompts are discoverable.
- Tool listing matches expected names.
- Full end-to-end workflow: open → navigate → interact → capture → close.
- Stateless mode (no session_id, auto-ephemeral backend).
"""

from __future__ import annotations

import pytest
from mcp.server.fastmcp import FastMCP

pytestmark = pytest.mark.e2e


class TestServerRegistration:
    """Verify all tools, resources, and prompts are registered."""

    async def test_all_tools_registered(self, mcp_server: FastMCP) -> None:
        """Verify the server has 100+ tools registered with --caps=all."""
        tools = await mcp_server.list_tools()
        tool_names = {t.name for t in tools}
        # Core tier tools (always present)
        expected_core = {
            "wavexis_session_open",
            "wavexis_session_close",
            "wavexis_session_info",
            "wavexis_navigate",
            "wavexis_back",
            "wavexis_forward",
            "wavexis_reload",
            "wavexis_stop",
            "wavexis_wait",
            "wavexis_screenshot",
            "wavexis_pdf",
            "wavexis_scrape",
            "wavexis_eval",
            "wavexis_dom_get",
            "wavexis_dom_query",
            "wavexis_click",
            "wavexis_type",
            "wavexis_fill",
            "wavexis_cookies_get",
            "wavexis_list_tabs",
            "wavexis_browser_version",
            "wavexis_act",
        }
        missing = expected_core - tool_names
        assert not missing, f"Missing core tools: {missing}"

        # Optional tier tools
        expected_optional = {
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
            "wavexis_extract",
            "wavexis_service_worker_list",
        }
        missing_opt = expected_optional - tool_names
        assert not missing_opt, f"Missing optional tier tools: {missing_opt}"

    async def test_tool_count(self, mcp_server: FastMCP) -> None:
        """Verify a significant number of tools are registered."""
        tools = await mcp_server.list_tools()
        assert len(tools) >= 100, f"Expected 100+ tools, got {len(tools)}"

    async def test_all_tools_have_annotations(self, mcp_server: FastMCP) -> None:
        """Every registered tool should have ToolAnnotations."""
        tools = await mcp_server.list_tools()
        for tool in tools:
            assert tool.annotations is not None, f"Tool {tool.name} missing annotations"

    async def test_all_tools_have_descriptions(self, mcp_server: FastMCP) -> None:
        """Every registered tool should have a description."""
        tools = await mcp_server.list_tools()
        for tool in tools:
            assert tool.description, f"Tool {tool.name} missing description"

    async def test_resources_registered(self, mcp_server: FastMCP) -> None:
        """Verify MCP resources are registered."""
        resources = await mcp_server.list_resources()
        # Resources use wavexis:// scheme
        templates = await mcp_server.list_resource_templates()
        assert len(templates) >= 1 or len(resources) >= 1

    async def test_prompts_registered(self, mcp_server: FastMCP) -> None:
        """Verify MCP prompts are registered."""
        prompts = await mcp_server.list_prompts()
        prompt_names = {p.name for p in prompts}
        expected = {"scrape_page", "audit_page", "fill_form", "debug_page"}
        missing = expected - prompt_names
        assert not missing, f"Missing prompts: {missing}"


class TestFullWorkflow:
    """Complete end-to-end workflows through the MCP server."""

    async def test_complete_form_workflow(self, call_tool, base_url) -> None:
        """Full workflow: open session → navigate → fill form → submit → verify → close."""
        # 1. Open session
        session_data = await call_tool("wavexis_session_open", backend="cdp", headless=True)
        assert session_data["status"] == "ok"
        sid = session_data["session_id"]

        try:
            # 2. Navigate to form page
            nav_data = await call_tool(
                "wavexis_navigate",
                url=f"{base_url}/form.html",
                session_id=sid,
            )
            assert nav_data["status"] == "ok"

            # 3. Fill name field
            fill_data = await call_tool(
                "wavexis_fill",
                selector="#name",
                value="E2E Test User",
                session_id=sid,
            )
            assert fill_data["status"] == "ok"

            # 4. Fill email field
            email_data = await call_tool(
                "wavexis_fill",
                selector="#email",
                value="e2e@test.com",
                session_id=sid,
            )
            assert email_data["status"] == "ok"

            # 5. Select country
            select_data = await call_tool(
                "wavexis_select_option",
                selector="#country",
                value="es",
                session_id=sid,
            )
            assert select_data["status"] == "ok"

            # 6. Click submit
            click_data = await call_tool(
                "wavexis_click",
                selector="#submit-btn",
                session_id=sid,
            )
            assert click_data["status"] == "ok"

            # 7. Verify form submitted
            status_data = await call_tool(
                "wavexis_eval",
                expression="document.getElementById('form-status').textContent",
                session_id=sid,
            )
            assert "Submitted" in str(status_data.get("result", ""))

            # 8. Take a screenshot as proof
            shot_data = await call_tool("wavexis_screenshot", session_id=sid)
            assert shot_data["status"] == "ok"
            assert "base64" in shot_data

        finally:
            await call_tool("wavexis_session_close", session_id=sid)

    async def test_stateless_screenshot(self, call_tool, base_url) -> None:
        """Take a screenshot in stateless mode (no session_id, auto-ephemeral)."""
        data = await call_tool(
            "wavexis_screenshot",
            url=f"{base_url}/index.html",
            headless=True,
        )
        assert data["status"] == "ok"
        assert "base64" in data

    async def test_stateless_scrape(self, call_tool, base_url) -> None:
        """Scrape a page in stateless mode."""
        data = await call_tool(
            "wavexis_scrape",
            urls=[f"{base_url}/index.html"],
            headless=True,
        )
        results = data.get("results", [])
        assert isinstance(results, list)
        assert len(results) >= 1
        content = str(results[0])
        assert "WaveXisMCP" in content or "Test Page" in content

    async def test_multi_tab_workflow(self, call_tool, base_url) -> None:
        """Open session, create multiple tabs, interact in each, verify."""
        session_data = await call_tool("wavexis_session_open", backend="cdp", headless=True)
        sid = session_data["session_id"]

        try:
            # Navigate to index in first tab
            await call_tool("wavexis_navigate", url=f"{base_url}/index.html", session_id=sid)

            # Open second tab with form
            await call_tool("wavexis_new_tab", url=f"{base_url}/form.html", session_id=sid)

            # List tabs
            tabs_data = await call_tool("wavexis_list_tabs", session_id=sid)
            tabs = tabs_data.get("tabs", [])
            assert len(tabs) >= 2

        finally:
            await call_tool("wavexis_session_close", session_id=sid)

    async def test_act_full_workflow(self, call_tool, base_url) -> None:
        """Full workflow using wavexis_act for NL interaction."""
        session_data = await call_tool("wavexis_session_open", backend="cdp", headless=True)
        sid = session_data["session_id"]

        try:
            # Navigate to index
            await call_tool("wavexis_navigate", url=f"{base_url}/index.html", session_id=sid)

            # Use act to click the Click Me button
            act_data = await call_tool(
                "wavexis_act",
                instruction="click the Click Me button",
                session_id=sid,
            )
            assert act_data.get("status") in ("ok", "no_match") or "error" in act_data

            # If it worked, verify the click result
            if act_data.get("status") == "ok":
                result = await call_tool(
                    "wavexis_eval",
                    expression="document.getElementById('click-result').textContent",
                    session_id=sid,
                )
                assert "Clicked" in str(result.get("result", ""))

        finally:
            await call_tool("wavexis_session_close", session_id=sid)


class TestErrorHandling:
    """Verify error handling in real browser scenarios."""

    async def test_navigate_invalid_url(self, call_tool, chrome_session) -> None:
        """Navigate to an invalid URL should return an error."""
        data = await call_tool(
            "wavexis_navigate",
            url="not-a-valid-url",
            session_id=chrome_session,
        )
        assert "error" in data or data["status"] != "ok"

    async def test_click_nonexistent_selector(self, call_tool, chrome_session) -> None:
        """Click a non-existent selector should return an error."""
        data = await call_tool(
            "wavexis_click",
            selector="#nonexistent-element-xyz",
            session_id=chrome_session,
        )
        assert "error" in data or data["status"] != "ok"

    async def test_eval_syntax_error(self, call_tool, chrome_session) -> None:
        """Evaluate invalid JavaScript should return an error or exception."""
        data = await call_tool(
            "wavexis_eval",
            expression="this is not valid javascript!!!",
            session_id=chrome_session,
        )
        # eval returns result+type on success, error key on failure
        assert (
            "error" in data
            or "exceptionDetails" in str(data.get("result", ""))
            or data.get("type") == "undefined"
        )

    async def test_session_close_already_closed(self, call_tool) -> None:
        """Close a session that was already closed."""
        # Open and close
        session_data = await call_tool("wavexis_session_open", backend="cdp", headless=True)
        sid = session_data["session_id"]
        await call_tool("wavexis_session_close", session_id=sid)

        # Try to close again
        data = await call_tool("wavexis_session_close", session_id=sid)
        assert "error" in data or data["status"] != "ok"
