"""Unit tests for SessionManager."""

from __future__ import annotations

import asyncio
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


@pytest.mark.unit
async def test_close_waits_for_pending_acquire_release(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    backend, sid = await session_manager_with_mock.acquire_backend(
        session_id=mock_session_id,
    )
    assert sid == mock_session_id
    assert session_manager_with_mock._sessions[mock_session_id].ref_count == 1

    async def _close_after_release() -> None:
        await session_manager_with_mock.release_backend(backend, sid)

    task = asyncio.create_task(_close_after_release())
    await session_manager_with_mock.close(mock_session_id)
    await task

    assert mock_session_id not in session_manager_with_mock._sessions


@pytest.mark.unit
async def test_connect_existing_launches_chrome(mock_backend: AsyncMock) -> None:
    """connect_existing=True launches Chrome and connects via CDP."""
    from unittest.mock import MagicMock

    mgr = SessionManager()
    with (
        patch.object(mgr._backend_manager, "select", return_value=mock_backend),
        patch(
            "wavexis_mcp.session._find_chrome_binary",
            return_value="/usr/bin/google-chrome",
        ),
        patch(
            "wavexis_mcp.session._launch_chrome_with_debug_port", new_callable=AsyncMock
        ) as mock_launch,
    ):
        mock_proc = MagicMock()
        mock_proc.pid = 12345
        mock_proc.terminate = MagicMock()
        mock_proc.wait = AsyncMock(return_value=0)
        mock_launch.return_value = mock_proc

        sid = await mgr.open(backend="cdp", headless=True, connect_existing=True)

    session = mgr._sessions[sid]
    assert session.chrome_proc is mock_proc
    # Verify launch was called with a port and no user_data_dir
    mock_launch.assert_called_once()
    args = mock_launch.call_args
    assert args.args[0] == 9223  # _CONNECT_EXISTING_PORT
    # Cleanup
    await mgr.close(sid)


@pytest.mark.unit
async def test_connect_existing_without_chrome_raises(mock_backend: AsyncMock) -> None:
    """connect_existing=True raises RuntimeError when Chrome is not found."""
    mgr = SessionManager()
    with (
        patch.object(mgr._backend_manager, "select", return_value=mock_backend),
        patch("wavexis_mcp.session._find_chrome_binary", return_value=None),
        pytest.raises(RuntimeError, match="Could not find Chrome"),
    ):
        await mgr.open(backend="cdp", headless=True, connect_existing=True)


@pytest.mark.unit
async def test_connect_existing_ignores_browser_url(mock_backend: AsyncMock) -> None:
    """connect_existing is ignored when browser_url is already set."""
    mgr = SessionManager()
    with (
        patch.object(mgr._backend_manager, "select", return_value=mock_backend),
        patch(
            "wavexis_mcp.session._launch_chrome_with_debug_port", new_callable=AsyncMock
        ) as mock_launch,
        patch("wavexis_mcp.session.validate_websocket_url", return_value=None),
    ):
        sid = await mgr.open(
            backend="cdp",
            headless=True,
            connect_existing=True,
            connect_endpoint="ws://example.com:9999",
        )

    # Should NOT have launched Chrome since browser_url was provided
    mock_launch.assert_not_called()
    session = mgr._sessions[sid]
    assert session.chrome_proc is None
    await mgr.close(sid)


@pytest.mark.unit
async def test_close_terminates_chrome_subprocess(mock_backend: AsyncMock) -> None:
    """close() terminates the Chrome subprocess launched by connect_existing."""
    from unittest.mock import MagicMock

    mgr = SessionManager()
    mock_proc = MagicMock()
    mock_proc.pid = 12345
    mock_proc.terminate = MagicMock()
    mock_proc.wait = AsyncMock(return_value=0)

    with (
        patch.object(mgr._backend_manager, "select", return_value=mock_backend),
        patch(
            "wavexis_mcp.session._find_chrome_binary",
            return_value="/usr/bin/google-chrome",
        ),
        patch(
            "wavexis_mcp.session._launch_chrome_with_debug_port", new_callable=AsyncMock
        ) as mock_launch,
    ):
        mock_launch.return_value = mock_proc
        sid = await mgr.open(backend="cdp", headless=True, connect_existing=True)

    await mgr.close(sid)
    mock_proc.terminate.assert_called_once()


@pytest.mark.unit
def test_find_chrome_binary_returns_none_when_not_found() -> None:
    """_find_chrome_binary returns None when no browser is in PATH."""
    with (
        patch("wavexis_mcp.session.shutil.which", return_value=None),
        patch("wavexis_mcp.session.platform.system", return_value="Linux"),
    ):
        from wavexis_mcp.session import _find_chrome_binary

        result = _find_chrome_binary()
    assert result is None


@pytest.mark.unit
def test_session_open_input_has_connect_existing() -> None:
    """SessionOpenInput has the connect_existing field."""
    from wavexis_mcp.models import SessionOpenInput

    field_info = SessionOpenInput.model_fields.get("connect_existing")
    assert field_info is not None
    assert field_info.default is False
