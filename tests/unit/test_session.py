"""Unit tests for SessionManager."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from wavexis_mcp.errors import SessionNotFoundError
from wavexis_mcp.session import SessionManager


@pytest.mark.unit
async def test_open_returns_session_id(mock_backend: AsyncMock) -> None:
    mgr = SessionManager()
    with patch.object(mgr._backend_manager, "select", return_value=mock_backend):
        sid = await mgr.open(backend="cdp", headless=True)
    assert isinstance(sid, str)
    assert sid in mgr._sessions
    mock_backend.launch.assert_called_once()


@pytest.mark.unit
async def test_get_returns_session(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    session = session_manager_with_mock.get(mock_session_id)
    assert session.session_id == mock_session_id


@pytest.mark.unit
async def test_get_raises_not_found(session_manager_with_mock: SessionManager) -> None:
    with pytest.raises(SessionNotFoundError):
        session_manager_with_mock.get("nonexistent-id")


@pytest.mark.unit
async def test_close_removes_session(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    await session_manager_with_mock.close(mock_session_id)
    assert mock_session_id not in session_manager_with_mock._sessions


@pytest.mark.unit
async def test_close_raises_not_found(session_manager_with_mock: SessionManager) -> None:
    with pytest.raises(SessionNotFoundError):
        await session_manager_with_mock.close("nonexistent-id")


@pytest.mark.unit
async def test_cleanup_all_closes_all(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    await session_manager_with_mock.cleanup_all()
    assert len(session_manager_with_mock._sessions) == 0


@pytest.mark.unit
async def test_info_returns_metadata(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    info = session_manager_with_mock.info(mock_session_id)
    assert info["session_id"] == mock_session_id
    assert info["backend"] == "cdp"
    assert "created_at" in info
