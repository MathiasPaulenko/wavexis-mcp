"""Regression tests for bugs identified during the stabilization audit."""

from __future__ import annotations

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
