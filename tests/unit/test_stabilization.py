"""Stabilization tests covering error handling, concurrency, and edge cases.

These tests close gaps identified during the stabilization audit (Sprint 2,
items T-4 through T-7 in ref/fixes.md).
"""

from __future__ import annotations

import asyncio
import json
from unittest.mock import AsyncMock

import pytest
from mcp.server.fastmcp import FastMCP
from pydantic import ValidationError
from wavexis.exceptions import ActionError

from wavexis_mcp.errors import SessionNotFoundError
from wavexis_mcp.models import (
    EvalInput,
    FillFormInput,
    NavigateInput,
)
from wavexis_mcp.session import SessionManager

# ── T-4: Error handling gaps ──────────────────────────────────────


@pytest.mark.unit
async def test_session_expired_after_close(
    session_manager_with_mock: SessionManager,
    mock_session_id: str,
) -> None:
    """Using a session ID after close raises SessionNotFoundError."""
    await session_manager_with_mock.close(mock_session_id)
    with pytest.raises(SessionNotFoundError):
        session_manager_with_mock.get(mock_session_id)


@pytest.mark.unit
async def test_acquire_backend_ephemeral_launch_failure(
    session_manager_with_mock: SessionManager,
    mock_backend: AsyncMock,
) -> None:
    """Ephemeral backend launch failure propagates and cleans up."""
    mock_backend.launch = AsyncMock(side_effect=RuntimeError("launch failed"))
    with pytest.raises(RuntimeError, match="launch failed"):
        await session_manager_with_mock.acquire_backend(None)
    mock_backend.close.assert_awaited()


@pytest.mark.unit
async def test_navigate_tool_handles_backend_error(
    session_manager_with_mock: SessionManager,
    mock_session_id: str,
    mock_backend: AsyncMock,
) -> None:
    """Navigate tool returns error JSON when backend.navigate raises."""
    from wavexis_mcp.tools.navigation import register

    mock_backend.navigate = AsyncMock(side_effect=RuntimeError("network error"))
    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)
    tool = mcp._tool_manager.get_tool("wavexis_navigate")
    result = await tool.fn(NavigateInput(session_id=mock_session_id, url="https://example.com"))
    data = json.loads(result)
    assert "error" in data
    assert "network error" in data["error"]


@pytest.mark.unit
async def test_eval_tool_handles_backend_crash(
    session_manager_with_mock: SessionManager,
    mock_session_id: str,
    mock_backend: AsyncMock,
) -> None:
    """Eval tool returns error JSON when backend.eval raises."""
    from wavexis_mcp.tools.javascript import register

    mock_backend.eval = AsyncMock(side_effect=ConnectionError("WebSocket closed"))
    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)
    tool = mcp._tool_manager.get_tool("wavexis_eval")
    result = await tool.fn(EvalInput(session_id=mock_session_id, expression="1+1"))
    data = json.loads(result)
    assert "error" in data
    assert "WebSocket closed" in data["error"]


# ── T-6: Concurrency gaps ─────────────────────────────────────────


@pytest.mark.unit
async def test_concurrent_acquire_release_same_session(
    session_manager_with_mock: SessionManager,
    mock_session_id: str,
) -> None:
    """Multiple concurrent acquire/release cycles on the same session are safe."""

    async def acquire_release() -> None:
        backend, sid = await session_manager_with_mock.acquire_backend(session_id=mock_session_id)
        await asyncio.sleep(0.01)
        await session_manager_with_mock.release_backend(backend, sid)

    await asyncio.gather(*(acquire_release() for _ in range(10)))
    session = session_manager_with_mock._sessions[mock_session_id]
    assert session.ref_count == 0


@pytest.mark.unit
async def test_concurrent_close_different_sessions(
    session_manager_with_mock: SessionManager,
    mock_backend: AsyncMock,
) -> None:
    """Closing multiple sessions concurrently does not deadlock."""
    import time
    import uuid

    from wavexis_mcp.session import BrowserSession

    sids: list[str] = []
    for _ in range(5):
        sid = str(uuid.uuid4())
        session_manager_with_mock._sessions[sid] = BrowserSession(
            session_id=sid,
            backend=mock_backend,
            backend_name="cdp",
            created_at=time.time(),
            last_used=time.time(),
        )
        sids.append(sid)

    await asyncio.gather(*(session_manager_with_mock.close(sid) for sid in sids))
    for sid in sids:
        assert sid not in session_manager_with_mock._sessions


# ── T-7: Edge case gaps ───────────────────────────────────────────


@pytest.mark.unit
async def test_eval_with_unicode_expression(
    session_manager_with_mock: SessionManager,
    mock_session_id: str,
    mock_backend: AsyncMock,
) -> None:
    """Eval tool handles unicode (emoji, RTL) in expressions."""
    from wavexis_mcp.tools.javascript import register

    mock_backend.eval = AsyncMock(return_value="🎉")
    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)
    tool = mcp._tool_manager.get_tool("wavexis_eval")
    result = await tool.fn(
        EvalInput(
            session_id=mock_session_id,
            expression="document.title = 'مرحبا 🎉'",
        )
    )
    data = json.loads(result)
    assert data["status"] == "ok"


@pytest.mark.unit
async def test_fill_form_empty_fields_list(
    session_manager_with_mock: SessionManager,
    mock_session_id: str,
) -> None:
    """Fill form with zero fields is rejected by Pydantic validation."""
    with pytest.raises(ValidationError):
        FillFormInput(fields=[], session_id=mock_session_id)


@pytest.mark.unit
async def test_navigate_with_empty_url(
    session_manager_with_mock: SessionManager,
    mock_session_id: str,
) -> None:
    """Navigate with empty URL should not crash."""
    from wavexis_mcp.tools.navigation import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)
    tool = mcp._tool_manager.get_tool("wavexis_navigate")
    result = await tool.fn(NavigateInput(session_id=mock_session_id, url=""))
    data = json.loads(result)
    # Empty URL is either rejected or handled — must not crash.
    assert isinstance(data, dict)


@pytest.mark.unit
async def test_session_open_with_extreme_viewport(
    session_manager_with_mock: SessionManager,
    mock_backend: AsyncMock,
) -> None:
    """Session open with very large viewport values is rejected by wavexis."""
    with pytest.raises(ActionError):
        await session_manager_with_mock.open(width=99999, height=99999)


@pytest.mark.unit
async def test_session_open_with_zero_viewport(
    session_manager_with_mock: SessionManager,
    mock_backend: AsyncMock,
) -> None:
    """Session open with zero viewport is rejected by wavexis."""
    with pytest.raises(ActionError):
        await session_manager_with_mock.open(width=0, height=0)


@pytest.mark.unit
async def test_navigate_with_extremely_long_url(
    session_manager_with_mock: SessionManager,
    mock_session_id: str,
) -> None:
    """Navigate with a very long URL is handled gracefully."""
    from wavexis_mcp.tools.navigation import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)
    tool = mcp._tool_manager.get_tool("wavexis_navigate")
    long_url = "https://example.com/" + "a" * 5000
    result = await tool.fn(NavigateInput(session_id=mock_session_id, url=long_url))
    data = json.loads(result)
    assert isinstance(data, dict)
