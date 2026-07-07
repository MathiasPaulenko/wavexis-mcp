"""Unit tests for MCP resources (M3)."""

from __future__ import annotations

import json

import pytest

from wavexis_mcp.session import SessionManager


class TestResources:
    """Tests for MCP resource handlers."""

    @pytest.mark.unit
    async def test_get_session_url(
        self,
        session_manager_with_mock: SessionManager,
        mock_session_id: str,
    ) -> None:
        from unittest.mock import MagicMock

        from wavexis_mcp.resources import register

        mcp = MagicMock()
        registered: dict[str, object] = {}

        def capture_resource(uri: str):
            def decorator(func):
                registered[uri] = func
                return func
            return decorator

        mcp.resource = capture_resource
        register(mcp, session_manager_with_mock)

        url_func = registered["wavexis://session/{session_id}/url"]
        result = await url_func(mock_session_id)
        assert result == "result"  # mock_backend.eval returns "result"

    @pytest.mark.unit
    async def test_get_session_cookies(
        self,
        session_manager_with_mock: SessionManager,
        mock_session_id: str,
    ) -> None:
        from unittest.mock import MagicMock

        mcp = MagicMock()
        registered: dict[str, object] = {}

        def capture_resource(uri: str):
            def decorator(func):
                registered[uri] = func
                return func
            return decorator

        mcp.resource = capture_resource

        from wavexis_mcp.resources import register

        register(mcp, session_manager_with_mock)

        cookies_func = registered["wavexis://session/{session_id}/cookies"]
        result = await cookies_func(mock_session_id)
        cookies = json.loads(result)
        assert isinstance(cookies, list)
        assert cookies[0]["name"] == "session"

    @pytest.mark.unit
    async def test_get_session_console(
        self,
        session_manager_with_mock: SessionManager,
        mock_session_id: str,
    ) -> None:
        from unittest.mock import MagicMock

        mcp = MagicMock()
        registered: dict[str, object] = {}

        def capture_resource(uri: str):
            def decorator(func):
                registered[uri] = func
                return func
            return decorator

        mcp.resource = capture_resource

        from wavexis_mcp.resources import register

        register(mcp, session_manager_with_mock)

        console_func = registered["wavexis://session/{session_id}/console"]
        result = await console_func(mock_session_id)
        messages = json.loads(result)
        assert isinstance(messages, list)
        assert messages[0]["level"] == "error"

    @pytest.mark.unit
    async def test_get_session_tabs(
        self,
        session_manager_with_mock: SessionManager,
        mock_session_id: str,
    ) -> None:
        from unittest.mock import MagicMock

        mcp = MagicMock()
        registered: dict[str, object] = {}

        def capture_resource(uri: str):
            def decorator(func):
                registered[uri] = func
                return func
            return decorator

        mcp.resource = capture_resource

        from wavexis_mcp.resources import register

        register(mcp, session_manager_with_mock)

        tabs_func = registered["wavexis://session/{session_id}/tabs"]
        result = await tabs_func(mock_session_id)
        tabs = json.loads(result)
        assert isinstance(tabs, list)
        assert tabs[0]["id"] == "1"

    @pytest.mark.unit
    async def test_resource_error_handling(self) -> None:
        from unittest.mock import MagicMock

        mcp = MagicMock()
        registered: dict[str, object] = {}

        def capture_resource(uri: str):
            def decorator(func):
                registered[uri] = func
                return func
            return decorator

        mcp.resource = capture_resource

        from wavexis_mcp.resources import register

        register(mcp, SessionManager())

        url_func = registered["wavexis://session/{session_id}/url"]
        result = await url_func("nonexistent-session")
        data = json.loads(result)
        assert "error" in data

    @pytest.mark.unit
    async def test_resource_cookies_error(self) -> None:
        from unittest.mock import MagicMock

        mcp = MagicMock()
        registered: dict[str, object] = {}

        def capture_resource(uri: str):
            def decorator(func):
                registered[uri] = func
                return func
            return decorator

        mcp.resource = capture_resource

        from wavexis_mcp.resources import register

        register(mcp, SessionManager())

        cookies_func = registered["wavexis://session/{session_id}/cookies"]
        result = await cookies_func("nonexistent-session")
        data = json.loads(result)
        assert "error" in data

    @pytest.mark.unit
    async def test_resource_console_error(self) -> None:
        from unittest.mock import MagicMock

        mcp = MagicMock()
        registered: dict[str, object] = {}

        def capture_resource(uri: str):
            def decorator(func):
                registered[uri] = func
                return func
            return decorator

        mcp.resource = capture_resource

        from wavexis_mcp.resources import register

        register(mcp, SessionManager())

        console_func = registered["wavexis://session/{session_id}/console"]
        result = await console_func("nonexistent-session")
        data = json.loads(result)
        assert "error" in data

    @pytest.mark.unit
    async def test_resource_tabs_error(self) -> None:
        from unittest.mock import MagicMock

        mcp = MagicMock()
        registered: dict[str, object] = {}

        def capture_resource(uri: str):
            def decorator(func):
                registered[uri] = func
                return func
            return decorator

        mcp.resource = capture_resource

        from wavexis_mcp.resources import register

        register(mcp, SessionManager())

        tabs_func = registered["wavexis://session/{session_id}/tabs"]
        result = await tabs_func("nonexistent-session")
        data = json.loads(result)
        assert "error" in data

    @pytest.mark.unit
    async def test_resource_url_empty(
        self,
        session_manager_with_mock: SessionManager,
        mock_session_id: str,
    ) -> None:
        from unittest.mock import AsyncMock, MagicMock

        mcp = MagicMock()
        registered: dict[str, object] = {}

        def capture_resource(uri: str):
            def decorator(func):
                registered[uri] = func
                return func
            return decorator

        mcp.resource = capture_resource

        from wavexis_mcp.resources import register

        register(mcp, session_manager_with_mock)
        session_manager_with_mock.get(mock_session_id).backend.eval = AsyncMock(return_value=None)

        url_func = registered["wavexis://session/{session_id}/url"]
        result = await url_func(mock_session_id)
        assert result == ""
