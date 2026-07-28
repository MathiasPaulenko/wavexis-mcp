"""Tests for Sprint 4 features: CLI flags, stale retry, auto web vitals."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock

import pytest

from wavexis_mcp.session import SessionManager
from wavexis_mcp.tools.input import _is_stale_error, _with_retry

# ── F-7: Blocked origins ──────────────────────────────────────────


@pytest.mark.unit
async def test_blocked_origins_applied_on_open(
    session_manager_with_mock: SessionManager,
    mock_backend: AsyncMock,
) -> None:
    """blocked_origins are applied to every new session."""
    session_manager_with_mock.blocked_origins = ["*ads*", "*tracker*"]
    sid = await session_manager_with_mock.open()
    mock_backend.block_requests.assert_awaited_once_with(["*ads*", "*tracker*"])
    await session_manager_with_mock.close(sid)


@pytest.mark.unit
async def test_blocked_origins_not_applied_when_empty(
    session_manager_with_mock: SessionManager,
    mock_backend: AsyncMock,
) -> None:
    """No block_requests call when blocked_origins is empty."""
    sid = await session_manager_with_mock.open()
    mock_backend.block_requests.assert_not_awaited()
    await session_manager_with_mock.close(sid)


# ── F-8: Storage state restore ────────────────────────────────────


@pytest.mark.unit
async def test_storage_state_restore_on_open(
    session_manager_with_mock: SessionManager,
    mock_backend: AsyncMock,
    tmp_path,
) -> None:
    """storage_state_path is restored on every new session."""
    state_file = tmp_path / "state.json"
    state_file.write_text(
        json.dumps(
            {
                "cookies": [{"name": "session", "value": "abc"}],
                "localStorage": {"theme": "dark"},
                "sessionStorage": {"temp": "123"},
            }
        )
    )
    session_manager_with_mock.storage_state_path = str(state_file)
    sid = await session_manager_with_mock.open()
    mock_backend.set_cookies.assert_awaited_once()
    assert mock_backend.eval.await_count >= 2  # localStorage + sessionStorage
    await session_manager_with_mock.close(sid)


@pytest.mark.unit
async def test_storage_state_missing_file_does_not_crash(
    session_manager_with_mock: SessionManager,
    mock_backend: AsyncMock,
) -> None:
    """Missing storage state file should not crash session open."""
    session_manager_with_mock.storage_state_path = "/nonexistent/path.json"
    sid = await session_manager_with_mock.open()
    await session_manager_with_mock.close(sid)


# ── F-9: Stale element retry ──────────────────────────────────────


@pytest.mark.unit
def test_is_stale_error_detects_stale_keywords() -> None:
    """_is_stale_error detects common stale element error messages."""
    assert _is_stale_error(RuntimeError("element is stale"))
    assert _is_stale_error(RuntimeError("Node not found in the document"))
    assert _is_stale_error(RuntimeError("element not attached to the DOM"))
    assert _is_stale_error(RuntimeError("element has been detached"))


@pytest.mark.unit
def test_is_stale_error_rejects_non_stale() -> None:
    """_is_stale_error returns False for non-stale errors."""
    assert not _is_stale_error(RuntimeError("network error"))
    assert not _is_stale_error(ValueError("invalid selector"))
    assert not _is_stale_error(ConnectionError("WebSocket closed"))


@pytest.mark.unit
async def test_with_retry_succeeds_on_second_attempt() -> None:
    """_with_retry retries on stale errors and succeeds."""
    call_count = 0

    async def coro_factory():
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise RuntimeError("element is stale")
        return "ok"

    result = await _with_retry(coro_factory)
    assert result == "ok"
    assert call_count == 2


@pytest.mark.unit
async def test_with_retry_does_not_retry_non_stale() -> None:
    """_with_retry does not retry on non-stale errors."""
    call_count = 0

    async def coro_factory():
        nonlocal call_count
        call_count += 1
        raise RuntimeError("network error")

    with pytest.raises(RuntimeError, match="network error"):
        await _with_retry(coro_factory)
    assert call_count == 1


@pytest.mark.unit
async def test_with_retry_exhausts_retries() -> None:
    """_with_retry exhausts retries on persistent stale errors."""
    call_count = 0

    async def coro_factory():
        nonlocal call_count
        call_count += 1
        raise RuntimeError("element is stale")

    with pytest.raises(RuntimeError, match="stale"):
        await _with_retry(coro_factory, retries=2)
    assert call_count == 3  # initial + 2 retries


# ── F-10: Auto web vitals ─────────────────────────────────────────


@pytest.mark.unit
async def test_auto_web_vitals_injects_script(
    session_manager_with_mock: SessionManager,
    mock_backend: AsyncMock,
) -> None:
    """auto_web_vitals injects collection script after navigation."""
    session_manager_with_mock.auto_web_vitals = True

    # Replace the mock navigate with a real coroutine so _wrap_backend wraps it.
    original_navigate = AsyncMock()

    async def _real_navigate(url, wait=None):
        await original_navigate(url, wait)

    mock_backend.navigate = _real_navigate
    session_manager_with_mock._wrap_backend(mock_backend)

    sid = await session_manager_with_mock.open()
    # Navigate to trigger vitals injection.
    nav_coro = mock_backend.navigate
    await nav_coro("https://example.com")
    # eval should have been called for vitals injection.
    mock_backend.eval.assert_awaited()
    await session_manager_with_mock.close(sid)


@pytest.mark.unit
async def test_auto_web_vitals_disabled_by_default(
    session_manager_with_mock: SessionManager,
) -> None:
    """auto_web_vitals is False by default."""
    assert session_manager_with_mock.auto_web_vitals is False
