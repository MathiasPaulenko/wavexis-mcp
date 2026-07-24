"""Extended unit tests for wavexis_mcp.tools.network.

These focus on the Playwright-parity additions (network event log,
single-request detail, route management) that the generic smoke tests
do not exercise deeply.
"""

from __future__ import annotations

import json
import re
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from wavexis_mcp.models import (
    GetRequestBodyInput,
    GetResponseBodyInput,
    ModifyRequestInput,
    ModifyResponseInput,
    NetworkClearInput,
    NetworkRequestInput,
    NetworkRequestsInput,
    ReplayHARInput,
    RouteInput,
    RouteListInput,
    UnrouteInput,
)
from wavexis_mcp.session import SessionManager
from wavexis_mcp.tools.network import (
    _build_route_handler,
    _ensure_network_log,
    _init_network_log,
    _init_routes,
    _is_fetch,
    _is_success,
    _matches_pattern,
    _on_network_event,
    _parse_header_list,
    _refresh_routes,
    _render_network_line,
    _RouteEntry,
    register,
)


@pytest.mark.unit
async def test_glob_to_regex_matches(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    assert _matches_pattern("**/*.js", "https://example.com/app.js") is True
    assert _matches_pattern("**/*.js", "https://example.com/app.css") is False
    assert _matches_pattern("*api*", "https://example.com/api/v1") is True


@pytest.mark.unit
async def test_parse_header_list() -> None:
    assert _parse_header_list(["X-Test: 1", "Authorization: Bearer token"]) == {
        "X-Test": "1",
        "Authorization": "Bearer token",
    }
    assert _parse_header_list([]) == {}
    assert _parse_header_list(["no-colon"]) == {}


@pytest.mark.unit
async def test_render_network_line() -> None:
    assert "=> [200]" in _render_network_line(
        {"method": "GET", "url": "https://x.com", "status": 200}
    )
    assert _render_network_line({"method": "POST", "url": "https://x.com"}).endswith(
        "https://x.com"
    )


@pytest.mark.unit
async def test_is_fetch_and_success() -> None:
    assert _is_fetch({"type": "fetch"}) is True
    assert _is_fetch({"type": "script"}) is False
    assert _is_success({"status": 200}) is True
    assert _is_success({"status": 404}) is False
    assert _is_success({"status": None}) is False


@pytest.mark.unit
async def test_network_event_log_flow(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    session = session_manager_with_mock.get(mock_session_id)
    _init_network_log(session)

    _on_network_event(
        session,
        {
            "type": "network_request",
            "data": {
                "requestId": "r1",
                "request": {
                    "url": "https://example.com/api",
                    "method": "GET",
                    "headers": {"X": "1"},
                },
                "resourceType": "fetch",
            },
        },
    )

    _on_network_event(
        session,
        {
            "type": "network_response",
            "data": {
                "requestId": "r1",
                "response": {"status": 200, "headers": {"Content-Type": "application/json"}},
            },
        },
    )

    entry = session.backend._network_log_map["r1"]
    assert entry["status"] == 200
    assert entry["response_headers"]["Content-Type"] == "application/json"
    assert entry["request_headers"]["X"] == "1"

    # _on_network_event with missing requestId is ignored.
    _on_network_event(session, {"type": "network_request", "data": {}})
    assert len(session.backend._network_log) == 1


@pytest.mark.unit
async def test_ensure_network_log_subscribes(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    session = session_manager_with_mock.get(mock_session_id)
    session.backend.subscribe_events = AsyncMock(return_value="sub-1")

    log = await _ensure_network_log(session)
    assert log == session.backend._network_log
    assert session.backend._network_log_sub_id == "sub-1"
    session.backend.subscribe_events.assert_awaited_once()

    # Second call is idempotent.
    log2 = await _ensure_network_log(session)
    assert log2 is log
    assert session.backend.subscribe_events.await_count == 1


@pytest.mark.unit
async def test_network_requests_event_mode(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    session = session_manager_with_mock.get(mock_session_id)
    session.backend.subscribe_events = AsyncMock(return_value="sub-1")

    # Seed the network log manually.
    _init_network_log(session)
    session.backend._network_log.append(
        {
            "requestId": "r1",
            "url": "https://example.com/api.js",
            "method": "GET",
            "type": "script",
            "status": 200,
            "request_headers": {},
            "response_headers": {},
            "request_post_data": None,
            "timestamp": None,
            "response": None,
        }
    )

    tool = mcp._tool_manager.get_tool("wavexis_network_requests")
    result = await tool.fn(NetworkRequestsInput(session_id=mock_session_id, mode="events"))
    data = json.loads(result)
    assert data["total"] == 1
    assert data["requests"][0]["url"] == "https://example.com/api.js"

    # Filter by resource type.
    result = await tool.fn(
        NetworkRequestsInput(session_id=mock_session_id, mode="events", resource_type="script")
    )
    data = json.loads(result)
    assert data["total"] == 1

    result = await tool.fn(
        NetworkRequestsInput(session_id=mock_session_id, mode="events", resource_type="fetch")
    )
    data = json.loads(result)
    assert data["total"] == 0


@pytest.mark.unit
async def test_network_request_detail_and_clear(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    session = session_manager_with_mock.get(mock_session_id)
    session.backend.subscribe_events = AsyncMock(return_value="sub-1")
    session.backend.network_get_request_post_data = AsyncMock(return_value="body")
    session.backend.get_response_body = AsyncMock(return_value="response")

    _init_network_log(session)
    session.backend._network_log.append(
        {
            "requestId": "r1",
            "url": "https://example.com/api",
            "method": "POST",
            "type": "fetch",
            "status": 200,
            "request_headers": {"X": "1"},
            "response_headers": {"Y": "2"},
            "request_post_data": None,
            "timestamp": None,
            "response": None,
        }
    )

    tool = mcp._tool_manager.get_tool("wavexis_network_request")
    result = await tool.fn(NetworkRequestInput(session_id=mock_session_id, index=1))
    data = json.loads(result)
    assert data["url"] == "https://example.com/api"
    assert data["request_body"] == "body"
    assert data["response_body"] == "response"
    assert data["request_headers"] == {"X": "1"}
    assert data["response_headers"] == {"Y": "2"}

    # Out-of-range index.
    result = await tool.fn(NetworkRequestInput(session_id=mock_session_id, index=99))
    data = json.loads(result)
    assert "error" in data

    # Specific parts.
    result = await tool.fn(
        NetworkRequestInput(session_id=mock_session_id, index=1, part="request-headers")
    )
    data = json.loads(result)
    assert "request_headers" in data
    assert "response_headers" not in data

    clear_tool = mcp._tool_manager.get_tool("wavexis_network_clear")
    result = await clear_tool.fn(NetworkClearInput(session_id=mock_session_id))
    data = json.loads(result)
    assert data["status"] == "ok"
    assert session.backend._network_log == []


@pytest.mark.unit
async def test_route_mock_flow(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    session = session_manager_with_mock.get(mock_session_id)
    cdp_session = MagicMock()
    session.backend._require_session = MagicMock(return_value=cdp_session)
    session.backend.raw = AsyncMock()

    tool = mcp._tool_manager.get_tool("wavexis_route")
    result = await tool.fn(
        RouteInput(
            session_id=mock_session_id,
            pattern="**/*.json",
            status=200,
            body='{"ok": true}',
            content_type="application/json",
        )
    )
    data = json.loads(result)
    assert data["status"] == "ok"

    # Trigger the route handler for a matching request.
    handler = session.backend._route_handler
    assert handler is not None
    await handler({"requestId": "req-1", "request": {"url": "https://example.com/data.json"}})

    session.backend.raw.assert_awaited()
    assert session.backend.raw.await_args_list[-1].args[0] == "Fetch.fulfillRequest"

    # List routes.
    list_tool = mcp._tool_manager.get_tool("wavexis_route_list")
    result = await list_tool.fn(RouteListInput(session_id=mock_session_id))
    data = json.loads(result)
    assert data["count"] == 1
    assert data["routes"][0]["pattern"] == "**/*.json"


@pytest.mark.unit
async def test_route_header_modification(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    session = session_manager_with_mock.get(mock_session_id)
    cdp_session = MagicMock()
    session.backend._require_session = MagicMock(return_value=cdp_session)
    session.backend.raw = AsyncMock()

    tool = mcp._tool_manager.get_tool("wavexis_route")
    await tool.fn(
        RouteInput(
            session_id=mock_session_id,
            pattern="**/*.js",
            headers=["X-Added: yes"],
            remove_headers="x-deprecated",
        )
    )

    handler = session.backend._route_handler
    assert handler is not None
    await handler(
        {
            "requestId": "req-2",
            "request": {"url": "https://example.com/app.js", "headers": {"X-Deprecated": "old"}},
        }
    )

    call_args = session.backend.raw.await_args_list[-1]
    assert call_args.args[0] == "Fetch.continueRequest"
    headers = call_args.args[1]["headers"]
    header_names = {h["name"] for h in headers}
    assert "X-Added" in header_names
    assert "X-Deprecated" not in header_names


@pytest.mark.unit
async def test_unroute(session_manager_with_mock: SessionManager, mock_session_id: str) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    session = session_manager_with_mock.get(mock_session_id)
    cdp_session = MagicMock()
    session.backend._require_session = MagicMock(return_value=cdp_session)
    session.backend.raw = AsyncMock()

    # Add two routes.
    tool = mcp._tool_manager.get_tool("wavexis_route")
    await tool.fn(RouteInput(session_id=mock_session_id, pattern="**/*.js"))
    await tool.fn(RouteInput(session_id=mock_session_id, pattern="**/*.css"))

    list_tool = mcp._tool_manager.get_tool("wavexis_route_list")

    unroute_tool = mcp._tool_manager.get_tool("wavexis_unroute")
    result = await unroute_tool.fn(UnrouteInput(session_id=mock_session_id, pattern="**/*.js"))
    data = json.loads(result)
    assert data["removed"] == 1

    result = await list_tool.fn(RouteListInput(session_id=mock_session_id))
    data = json.loads(result)
    assert data["count"] == 1

    # Unroute all.
    result = await unroute_tool.fn(UnrouteInput(session_id=mock_session_id, pattern=None))
    data = json.loads(result)
    assert data["removed"] == 1

    result = await list_tool.fn(RouteListInput(session_id=mock_session_id))
    data = json.loads(result)
    assert data["count"] == 0


@pytest.mark.unit
async def test_refresh_routes_with_empty_list_disables_fetch(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    session = session_manager_with_mock.get(mock_session_id)
    cdp_session = MagicMock()
    session.backend._require_session = MagicMock(return_value=cdp_session)
    session.backend.raw = AsyncMock()

    _init_routes(session)
    await _refresh_routes(session)

    call_names = [c.args[0] for c in session.backend.raw.await_args_list if c.args]
    assert "Fetch.disable" in call_names


@pytest.mark.unit
async def test_matches_pattern_regex_error_fallback() -> None:
    with patch("wavexis_mcp.tools.network._glob_to_regex", side_effect=re.error("bad")):
        assert _matches_pattern("*.js", "https://example.com/app.js") is True


@pytest.mark.unit
async def test_route_handler_body_dict_and_exceptions(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    session = session_manager_with_mock.get(mock_session_id)
    _init_routes(session)
    session.backend.raw = AsyncMock()

    route = _RouteEntry(
        pattern="**/*.json",
        status=201,
        body={"ok": True},
        content_type="application/json",
        add_headers={},
        remove_headers=[],
    )
    session.backend._route_entries.append(route)

    handler = _build_route_handler(session)
    session.backend._route_handler = handler
    await handler({"requestId": "r1", "request": {"url": "https://example.com/x.json"}})

    last_call = session.backend.raw.await_args_list[-1]
    assert last_call.args[0] == "Fetch.fulfillRequest"
    assert last_call.args[1]["responseCode"] == 201

    # Force raw() to raise so the except/pass branches are covered.
    session.backend.raw.side_effect = RuntimeError("fail")
    await handler({"requestId": "r2", "request": {"url": "https://example.com/y.json"}})

    # No-match continueRequest with exception branch.
    session.backend._route_entries.clear()
    await handler({"requestId": "r3", "request": {"url": "https://other.com/z.css"}})


@pytest.mark.unit
async def test_route_handler_no_match_and_header_mods(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    session = session_manager_with_mock.get(mock_session_id)
    _init_routes(session)
    session.backend.raw = AsyncMock()

    no_match = _RouteEntry(
        pattern="*.css",
        status=None,
        body=None,
        content_type=None,
        add_headers={"X-Trace": "yes"},
        remove_headers=["Cookie"],
    )
    session.backend._route_entries.append(no_match)
    handler = _build_route_handler(session)

    # No match: continue unchanged
    await handler({"requestId": "r4", "request": {"url": "https://example.com/app.js"}})
    call_names = [c.args[0] for c in session.backend.raw.await_args_list if c.args]
    assert "Fetch.continueRequest" in call_names

    # Header-modification branch with exception
    session.backend._route_entries.clear()
    session.backend._route_entries.append(no_match)
    session.backend.raw = AsyncMock(side_effect=RuntimeError("fail"))
    await handler(
        {
            "requestId": "r5",
            "request": {"url": "https://example.com/style.css", "headers": {"Cookie": "x=1"}},
        }
    )


@pytest.mark.unit
async def test_network_requests_events_filter(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    session = session_manager_with_mock.get(mock_session_id)
    session.backend.subscribe_events = AsyncMock(return_value="sub-1")
    _init_network_log(session)
    session.backend._network_log.append(
        {
            "requestId": "r1",
            "url": "https://example.com/api",
            "method": "GET",
            "type": "fetch",
            "status": 200,
            "request_headers": {},
            "response_headers": {},
            "request_post_data": None,
            "timestamp": None,
            "response": None,
        }
    )

    tool = mcp._tool_manager.get_tool("wavexis_network_requests")
    result = await tool.fn(
        NetworkRequestsInput(session_id=mock_session_id, mode="events", filter="[")
    )
    data = json.loads(result)
    assert data["total"] == 0


@pytest.mark.unit
async def test_network_requests_filters(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    session = session_manager_with_mock.get(mock_session_id)
    session.backend.subscribe_events = AsyncMock(return_value="sub-1")
    _init_network_log(session)
    session.backend._network_log.append(
        {
            "requestId": "r1",
            "url": "https://example.com/api",
            "method": "GET",
            "type": "fetch",
            "status": 200,
            "request_headers": {},
            "response_headers": {},
            "request_post_data": None,
            "timestamp": None,
            "response": None,
        }
    )

    tool = mcp._tool_manager.get_tool("wavexis_network_requests")

    # Events mode with a valid regex filter and resource_type.
    result = await tool.fn(
        NetworkRequestsInput(
            session_id=mock_session_id, mode="events", filter="example", resource_type="fetch"
        )
    )
    data = json.loads(result)
    assert data["total"] == 1

    # Legacy mode with filter and resource_type.
    session.backend.eval = AsyncMock(
        return_value=json.dumps([{"url": "https://x.com/script.js", "type": "script"}])
    )
    result = await tool.fn(
        NetworkRequestsInput(session_id=mock_session_id, filter="x.com", resource_type="script")
    )
    data = json.loads(result)
    assert data["total"] == 1


@pytest.mark.unit
async def test_network_request_body_exceptions(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    session = session_manager_with_mock.get(mock_session_id)
    session.backend.subscribe_events = AsyncMock(return_value="sub-1")
    session.backend.network_get_request_post_data = AsyncMock(side_effect=RuntimeError("fail"))
    session.backend.get_response_body = AsyncMock(side_effect=RuntimeError("fail"))

    _init_network_log(session)
    session.backend._network_log.append(
        {
            "requestId": "r1",
            "url": "https://example.com/api",
            "method": "POST",
            "type": "fetch",
            "status": 200,
            "request_headers": {},
            "response_headers": {},
            "request_post_data": None,
            "timestamp": None,
            "response": None,
        }
    )

    tool = mcp._tool_manager.get_tool("wavexis_network_request")
    result = await tool.fn(NetworkRequestInput(session_id=mock_session_id, index=1))
    data = json.loads(result)
    assert data["request_body"] is None
    assert data["response_body"] is None


@pytest.mark.unit
async def test_network_tools_exception_branches(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    # Use a bogus session_id to force session_manager.get() to raise.
    tool = mcp._tool_manager.get_tool("wavexis_network_clear")
    result = await tool.fn(NetworkClearInput(session_id="not-a-session"))
    assert "error" in json.loads(result)

    tool = mcp._tool_manager.get_tool("wavexis_route")
    result = await tool.fn(RouteInput(session_id="not-a-session", pattern="**/*.js"))
    assert "error" in json.loads(result)

    tool = mcp._tool_manager.get_tool("wavexis_route_list")
    result = await tool.fn(RouteListInput(session_id="not-a-session"))
    assert "error" in json.loads(result)

    tool = mcp._tool_manager.get_tool("wavexis_unroute")
    result = await tool.fn(UnrouteInput(session_id="not-a-session"))
    assert "error" in json.loads(result)

    tool = mcp._tool_manager.get_tool("wavexis_modify_request")
    result = await tool.fn(
        ModifyRequestInput(session_id="not-a-session", pattern={}, modifications={})
    )
    assert "error" in json.loads(result)

    tool = mcp._tool_manager.get_tool("wavexis_modify_response")
    result = await tool.fn(
        ModifyResponseInput(session_id="not-a-session", pattern={}, modifications={})
    )
    assert "error" in json.loads(result)

    tool = mcp._tool_manager.get_tool("wavexis_replay_har")
    result = await tool.fn(ReplayHARInput(session_id="not-a-session", har_path="/tmp/test.har"))
    assert "error" in json.loads(result)

    tool = mcp._tool_manager.get_tool("wavexis_get_request_body")
    result = await tool.fn(GetRequestBodyInput(session_id="not-a-session", request_id="r1"))
    assert "error" in json.loads(result)

    tool = mcp._tool_manager.get_tool("wavexis_get_response_body")
    result = await tool.fn(GetResponseBodyInput(session_id="not-a-session", request_id="r1"))
    assert "error" in json.loads(result)
