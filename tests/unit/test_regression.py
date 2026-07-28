"""Regression tests for bugs identified during the stabilization audit."""

from __future__ import annotations

import asyncio
import base64
import json
from typing import Any
from unittest.mock import AsyncMock

import pytest
from mcp.server.fastmcp import FastMCP
from pydantic import ValidationError

from wavexis_mcp.session import SessionManager
from wavexis_mcp.streaming import StreamingHandler


@pytest.mark.unit
async def test_streaming_start_is_idempotent(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    """Calling start_stream twice for the same session must not create duplicate tasks."""
    handler = StreamingHandler(session_manager_with_mock)
    stream_id = await handler.start_stream(mock_session_id)
    assert stream_id == f"stream-{mock_session_id}"
    again = await handler.start_stream(mock_session_id)
    assert again == stream_id
    assert len(handler._streams) == 1


@pytest.mark.unit
async def test_release_backend_close_error_does_not_raise(
    session_manager_with_mock: SessionManager,
) -> None:
    """release_backend must swallow close() failures instead of raising."""
    backend = AsyncMock()
    backend.close = AsyncMock(side_effect=RuntimeError("close failed"))
    await session_manager_with_mock.release_backend(backend, None)
    backend.close.assert_awaited_once()


@pytest.mark.unit
async def test_crawl_respects_url_pattern(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    """CrawlInput.url_pattern must filter discovered links."""
    from wavexis_mcp.models import CrawlInput
    from wavexis_mcp.tools import data

    session = session_manager_with_mock.get(mock_session_id)
    session.backend.eval = AsyncMock(
        side_effect=[
            "",
            ["https://example.com/api/users", "https://example.com/about"],
            "",
            [],
        ]
    )

    mcp = FastMCP("test")
    data.register(mcp, session_manager_with_mock)
    tool = mcp._tool_manager.get_tool("wavexis_crawl")
    result = await tool.fn(
        CrawlInput(
            session_id=mock_session_id,
            start_url="https://example.com",
            max_depth=1,
            max_pages=3,
            url_pattern="/api/",
        )
    )
    payload = json.loads(result)
    assert payload["pages_crawled"] == 2
    urls = {p["url"] for p in payload["pages"]}
    assert "https://example.com/api/users" in urls
    assert "https://example.com/about" not in urls


@pytest.mark.unit
def test_route_input_status_range() -> None:
    """RouteInput.status must reject invalid HTTP status codes."""
    from wavexis_mcp.models import RouteInput

    with pytest.raises(ValidationError):
        RouteInput(
            session_id="sid",
            pattern="**/api/*",
            status=99,
        )


@pytest.mark.unit
async def test_invoke_release_error_does_not_hide_result(
    session_manager_with_mock: SessionManager,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """wavexis_invoke must return a successful result even if release_backend fails."""
    from wavexis_mcp.models import InvokeInput
    from wavexis_mcp.tools import utility

    monkeypatch.setattr(
        session_manager_with_mock,
        "release_backend",
        AsyncMock(side_effect=RuntimeError("release failed")),
    )
    monkeypatch.setattr(
        session_manager_with_mock,
        "acquire_backend",
        AsyncMock(return_value=(AsyncMock(browser_version=AsyncMock(return_value="1.0")), None)),
    )

    mcp = FastMCP("test")
    utility.register(mcp, session_manager_with_mock)
    tool = mcp._tool_manager.get_tool("wavexis_invoke")
    result = await tool.fn(InvokeInput(method="browser_version", session_id=None, backend="cdp"))
    payload = json.loads(result)
    assert payload["status"] == "ok"
    assert payload["result"] == "1.0"


@pytest.mark.unit
async def test_find_handles_cyclic_a11y_tree(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    """wavexis_find must not recurse infinitely on a cyclic accessibility tree."""
    from wavexis_mcp.tools.playwright_parity import FindInput
    from wavexis_mcp.tools.playwright_parity import register as register_parity

    session = session_manager_with_mock.get(mock_session_id)
    session.backend.a11y_tree = AsyncMock(
        return_value={
            "nodes": [
                {"nodeId": "1", "role": "WebArea", "name": "page", "childIds": ["2"]},
                {"nodeId": "2", "role": "button", "name": "Submit", "childIds": ["1"]},
            ]
        }
    )

    mcp = FastMCP("test")
    register_parity(mcp, session_manager_with_mock)
    tool = mcp._tool_manager.get_tool("wavexis_find")
    result = await tool.fn(FindInput(text="Submit", session_id=mock_session_id))
    payload = json.loads(result)
    assert payload["count"] == 1


@pytest.mark.unit
@pytest.mark.parametrize(
    "cls, kwargs",
    [
        ("KeyDownInput", {"key": "", "session_id": "sid"}),
        ("PressKeysInput", {"text": "", "session_id": "sid"}),
        ("FindInput", {"text": "", "session_id": "sid"}),
        ("CookieGetInput", {"name": "", "session_id": "sid"}),
    ],
)
def test_playwright_parity_inputs_reject_empty_strings(cls: str, kwargs: dict[str, Any]) -> None:
    """Playwright parity input models must reject empty required strings."""
    from wavexis_mcp.tools import playwright_parity

    model_cls = getattr(playwright_parity, cls)
    with pytest.raises(ValidationError):
        model_cls(**kwargs)


@pytest.mark.unit
def test_base_input_rejects_empty_session_id() -> None:
    """Every model with a session_id field must reject empty or whitespace IDs."""
    from wavexis_mcp.models import SessionCloseInput, SessionInfoInput

    with pytest.raises(ValidationError):
        SessionCloseInput(session_id="")
    with pytest.raises(ValidationError):
        SessionInfoInput(session_id="   ")


@pytest.mark.unit
def test_base_input_strips_session_id_whitespace() -> None:
    """Padded session_ids are stripped so lookups do not fail on whitespace."""
    from wavexis_mcp.models import SessionInfoInput

    input_obj = SessionInfoInput(session_id="  abc-123  ")
    assert input_obj.session_id == "abc-123"


@pytest.mark.unit
def test_base_input_rejects_oversized_nested_payload(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Payloads that split fields across many small nested containers must still fail."""
    from wavexis_mcp.models import SetHeadersInput

    monkeypatch.setattr("wavexis_mcp.models._MAX_TOTAL_FIELDS", 2)
    with pytest.raises(ValueError):
        SetHeadersInput(
            session_id="sid",
            headers={"outer": {"a": "b", "c": "d"}},
        )


@pytest.mark.unit
async def test_session_open_respects_limit_concurrently(
    session_manager_with_mock: SessionManager,
    mock_backend: AsyncMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Concurrent open() calls must not exceed _MAX_SESSIONS."""
    from wavexis_mcp import session as session_module

    monkeypatch.setattr(session_module, "_MAX_SESSIONS", 2)

    async def slow_launch(*args: Any, **kwargs: Any) -> None:
        await asyncio.sleep(0.05)

    mock_backend.launch = AsyncMock(side_effect=slow_launch)

    results = await asyncio.gather(
        session_manager_with_mock.open(),
        session_manager_with_mock.open(),
        return_exceptions=True,
    )
    successes = [r for r in results if isinstance(r, str)]
    failures = [r for r in results if isinstance(r, RuntimeError)]
    assert len(successes) == 1
    assert len(failures) == 1


@pytest.mark.unit
async def test_execute_act_times_out_and_retries(monkeypatch: pytest.MonkeyPatch) -> None:
    """execute_act must wrap backend actions with a timeout and retry."""
    import wavexis_mcp.act as act_module
    from wavexis_mcp.act import execute_act

    async def slow_click(*args: Any, **kwargs: Any) -> None:
        await asyncio.sleep(5)

    async def js_fallback_fails(*args: Any, **kwargs: Any) -> None:
        raise RuntimeError("JS fallback also failed")

    backend = AsyncMock()
    backend.click = AsyncMock(side_effect=slow_click)
    monkeypatch.setattr(act_module, "_ACT_ACTION_TIMEOUT", 0.05)
    monkeypatch.setattr(act_module, "_execute_action_via_js", js_fallback_fails)

    tree = [{"ref": "1", "role": "button", "name": "Submit", "children": []}]
    result = await execute_act(backend, "click submit", tree, max_retries=2)

    assert result["status"] == "error"
    assert result["action"] == "click"
    assert result["attempts"] == 2
    assert backend.click.call_count == 2


@pytest.mark.unit
def test_get_config_input_inherits_base_input() -> None:
    """GetConfigInput must inherit BaseInput so shared validators run."""
    from wavexis_mcp.models import BaseInput
    from wavexis_mcp.tools.playwright_parity import GetConfigInput

    assert issubclass(GetConfigInput, BaseInput)


@pytest.mark.unit
async def test_extension_install_rejects_invalid_path(
    session_manager_with_mock: SessionManager, mock_session_id: str, tmp_path: Any
) -> None:
    """wavexis_extension_install must reject non-.crx / non-directory paths."""
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.models import ExtensionInstallInput
    from wavexis_mcp.tools import experimental

    bad = tmp_path / "foo.txt"
    bad.write_text("not an extension")

    mcp = FastMCP("test")
    experimental.register(mcp, session_manager_with_mock)
    tool = mcp._tool_manager.get_tool("wavexis_extension_install")
    result = await tool.fn(ExtensionInstallInput(session_id=mock_session_id, path=str(bad)))
    payload = json.loads(result)
    assert payload["tool"] == "wavexis_extension_install"
    assert payload["type"] == "ValueError"
    assert "Extension path" in payload["message"]


@pytest.mark.unit
async def test_video_frame_handler_tracks_total_frames() -> None:
    """_make_frame_handler must update a shared frame counter."""
    import asyncio

    from wavexis_mcp.tools.video import _make_frame_handler

    recording: dict[str, Any] = {"frames": [], "_stopped": False}
    total_ref: list[int] = [0]
    handler = _make_frame_handler(recording, total_ref)
    payload = base64.b64encode(b"frame-data").decode()
    handler({"data": payload})
    await asyncio.sleep(0.1)
    assert len(recording["frames"]) == 1
    assert total_ref[0] == 1


@pytest.mark.unit
def test_network_log_map_stays_bounded(
    session_manager_with_mock: SessionManager, mock_session_id: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """_on_network_event must cap the request map at _NETWORK_LOG_MAX."""
    from wavexis_mcp.tools import network as network_module

    monkeypatch.setattr(network_module, "_NETWORK_LOG_MAX", 3)

    session = session_manager_with_mock.get(mock_session_id)
    backend = session.backend

    for i in range(5):
        network_module._on_network_event(
            session,
            {
                "type": "network_request",
                "data": {"requestId": f"req-{i}", "request": {"url": f"https://x/{i}"}},
            },
        )

    assert len(backend._network_log_map) == 3
