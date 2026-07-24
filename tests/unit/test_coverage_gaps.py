"""Targeted coverage tests for branches missed by the generic smoke tests."""

from __future__ import annotations

import json
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from wavexis_mcp import errors
from wavexis_mcp import server as server_module
from wavexis_mcp.rate_limiter import RateLimiter
from wavexis_mcp.session import SessionManager


@pytest.fixture
def coverage_mcp(session_manager_with_mock: SessionManager, mock_session_id: str) -> Any:
    """Build a FastMCP server with all tools registered to the mock session."""
    with patch("wavexis.backend.manager.BackendManager") as mock_mgr_cls:
        mock_mgr = MagicMock()
        mock_mgr.list_available = MagicMock(return_value=["cdp"])
        mock_mgr.install_check = MagicMock(return_value={"cdp": "1.0.0"})
        mock_mgr.select = MagicMock(
            return_value=session_manager_with_mock._backend_manager.select()
        )
        mock_mgr_cls.return_value = mock_mgr

        original_session_manager = server_module._session_manager
        server_module._session_manager = session_manager_with_mock
        try:
            mcp = server_module.create_server(caps="all")
            yield mcp
        finally:
            server_module._session_manager = original_session_manager


@pytest.mark.unit
async def test_error_classes_and_suggestion() -> None:
    assert str(errors.SessionExpiredError("sid")) == "Session 'sid' has expired or been closed."
    assert str(errors.TimeoutError(5000)) == "Operation timed out after 5000ms."
    assert errors.get_suggestion(Exception("x")) == "Check the error message and verify inputs."


@pytest.mark.unit
async def test_rate_limiter_update_existing_buckets() -> None:
    rl = RateLimiter(rate=1, burst=2)
    # Create two buckets implicitly by acquiring tokens.
    await rl.acquire("s1")
    await rl.acquire("s2")
    rl.configure(10, 20)
    assert rl.default_rate == 10.0
    assert rl.default_burst == 20
    for bucket in rl._buckets.values():
        assert bucket.rate == 10.0
        assert bucket.burst == 20


@pytest.mark.unit
async def test_session_tools_error_branches(
    coverage_mcp: Any, session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    session_manager_with_mock.open = AsyncMock(side_effect=RuntimeError("open fail"))
    session_manager_with_mock.close = AsyncMock(side_effect=RuntimeError("close fail"))
    session_manager_with_mock.info = MagicMock(side_effect=RuntimeError("info fail"))

    from wavexis_mcp.models import SessionInfoInput, SessionOpenInput

    tool = coverage_mcp._tool_manager.get_tool("wavexis_session_open")
    result = await tool.fn(SessionOpenInput())
    assert "error" in json.loads(result)

    tool = coverage_mcp._tool_manager.get_tool("wavexis_session_close")
    result = await tool.fn(SessionInfoInput(session_id=mock_session_id))
    assert "error" in json.loads(result)

    tool = coverage_mcp._tool_manager.get_tool("wavexis_session_info")
    result = await tool.fn(SessionInfoInput(session_id=mock_session_id))
    assert "error" in json.loads(result)


@pytest.mark.unit
async def test_act_partial_name_scoring() -> None:
    from wavexis_mcp.act import _score_element

    # "sub" is a substring of "submit" but not a separate word in name_words.
    score = _score_element({"role": "button", "name": "submit button"}, ["sub"], {"button"})
    assert score >= 15


@pytest.mark.unit
async def test_dom_query_with_url_branch(
    coverage_mcp: Any, session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from wavexis_mcp.models import DOMQueryInput

    tool = coverage_mcp._tool_manager.get_tool("wavexis_dom_query")
    inp = DOMQueryInput(
        session_id=mock_session_id,
        selector="button",
        url="https://example.com",
        all=True,
    )
    result = await tool.fn(inp)
    data = json.loads(result)
    assert data["count"] == 1
    session_manager_with_mock.get(mock_session_id).backend.navigate.assert_awaited()


@pytest.mark.unit
async def test_webaudio_single_context(
    coverage_mcp: Any, session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from wavexis_mcp.models import WebAudioCaptureInput

    session_manager_with_mock.get(mock_session_id).backend.webaudio_get_context = AsyncMock(
        return_value={"id": "ctx-1"}
    )
    tool = coverage_mcp._tool_manager.get_tool("wavexis_webaudio_capture")
    result = await tool.fn(WebAudioCaptureInput(session_id=mock_session_id, context_id="ctx-1"))
    data = json.loads(result)
    assert data["contexts"][0]["id"] == "ctx-1"


@pytest.mark.unit
async def test_fill_form_navigate_branch(
    coverage_mcp: Any, session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from wavexis_mcp.models import FillFormInput, FormField

    tool = coverage_mcp._tool_manager.get_tool("wavexis_fill_form")
    result = await tool.fn(
        FillFormInput(
            session_id=mock_session_id,
            url="https://example.com",
            fields=[FormField(selector="#name", value="alice")],
        )
    )
    data = json.loads(result)
    assert data["fields_filled"] == 1
    session_manager_with_mock.get(mock_session_id).backend.navigate.assert_awaited()


@pytest.mark.unit
async def test_drop_missing_element(
    coverage_mcp: Any, session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from wavexis_mcp.models import DropInput

    session_manager_with_mock.get(mock_session_id).backend.eval = AsyncMock(return_value=None)

    tool = coverage_mcp._tool_manager.get_tool("wavexis_drop")
    result = await tool.fn(
        DropInput(
            session_id=mock_session_id,
            selector="#target",
            data={"text/plain": "hello"},
        )
    )
    assert "error" in json.loads(result)


@pytest.mark.unit
async def test_storage_restore_invalid_state(
    tmp_path, coverage_mcp: Any, mock_session_id: str
) -> None:
    from wavexis_mcp.models import StorageStateRestoreInput

    path = tmp_path / "state.json"
    path.write_text(json.dumps([]))

    tool = coverage_mcp._tool_manager.get_tool("wavexis_storage_state_restore")
    result = await tool.fn(
        StorageStateRestoreInput(session_id=mock_session_id, input_path=str(path))
    )
    assert "error" in json.loads(result)


@pytest.mark.unit
async def test_storage_restore_exception(tmp_path, coverage_mcp: Any, mock_session_id: str) -> None:
    from wavexis_mcp.models import StorageStateRestoreInput

    path = tmp_path / "missing.json"

    tool = coverage_mcp._tool_manager.get_tool("wavexis_storage_state_restore")
    result = await tool.fn(
        StorageStateRestoreInput(session_id=mock_session_id, input_path=str(path))
    )
    assert "error" in json.loads(result)
