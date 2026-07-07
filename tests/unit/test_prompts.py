"""Unit tests for MCP prompts (M3)."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest


class TestPrompts:
    """Tests for MCP prompt templates."""

    @pytest.mark.unit
    def test_scrape_page_prompt(self) -> None:
        from wavexis_mcp.prompts import register

        mcp = MagicMock()
        registered: dict[str, object] = {}

        def capture_prompt():
            def decorator(func):
                registered[func.__name__] = func
                return func
            return decorator

        mcp.prompt = capture_prompt
        register(mcp)

        assert "scrape_page" in registered
        result = registered["scrape_page"]("https://example.com", "article")
        assert "https://example.com" in result
        assert "article" in result
        assert "wavexis_session_open" in result
        assert "wavexis_scrape" in result

    @pytest.mark.unit
    def test_audit_page_prompt(self) -> None:
        from wavexis_mcp.prompts import register

        mcp = MagicMock()
        registered: dict[str, object] = {}

        def capture_prompt():
            def decorator(func):
                registered[func.__name__] = func
                return func
            return decorator

        mcp.prompt = capture_prompt
        register(mcp)

        assert "audit_page" in registered
        result = registered["audit_page"]("https://example.com")
        assert "https://example.com" in result
        assert "wavexis_axe_audit" in result
        assert "wavexis_perf_metrics" in result

    @pytest.mark.unit
    def test_fill_form_prompt(self) -> None:
        from wavexis_mcp.prompts import register

        mcp = MagicMock()
        registered: dict[str, object] = {}

        def capture_prompt():
            def decorator(func):
                registered[func.__name__] = func
                return func
            return decorator

        mcp.prompt = capture_prompt
        register(mcp)

        assert "fill_form" in registered
        result = registered["fill_form"](
            "https://example.com/form", "name=John, email=john@test.com"
        )
        assert "https://example.com/form" in result
        assert "name=John" in result
        assert "wavexis_fill_form" in result or "fill" in result.lower()

    @pytest.mark.unit
    def test_debug_page_prompt(self) -> None:
        from wavexis_mcp.prompts import register

        mcp = MagicMock()
        registered: dict[str, object] = {}

        def capture_prompt():
            def decorator(func):
                registered[func.__name__] = func
                return func
            return decorator

        mcp.prompt = capture_prompt
        register(mcp)

        assert "debug_page" in registered
        result = registered["debug_page"]("https://example.com")
        assert "https://example.com" in result
        assert "wavexis_console_messages" in result
        assert "wavexis_perf_metrics" in result

    @pytest.mark.unit
    def test_all_four_prompts_registered(self) -> None:
        from wavexis_mcp.prompts import register

        mcp = MagicMock()
        registered: dict[str, object] = {}

        def capture_prompt():
            def decorator(func):
                registered[func.__name__] = func
                return func
            return decorator

        mcp.prompt = capture_prompt
        register(mcp)

        assert len(registered) == 4
        assert set(registered.keys()) == {"scrape_page", "audit_page", "fill_form", "debug_page"}
