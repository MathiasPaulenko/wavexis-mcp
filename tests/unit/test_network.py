"""Unit tests for network tools."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from wavexis_mcp.models import (
    BlockRequestsInput,
    CaptureHARInput,
    InterceptRequestsInput,
    MockResponseInput,
    ModifyResponseInput,
    NetworkRequestsInput,
    SetCacheDisabledInput,
    SetHeadersInput,
    SetUserAgentInput,
    ThrottleNetworkInput,
)
from wavexis_mcp.session import SessionManager


@pytest.mark.unit
async def test_set_headers(session_manager_with_mock: SessionManager, mock_session_id: str) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.network import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_set_headers")
    result = await tool.fn(SetHeadersInput(headers={"X-Test": "true"}, session_id=mock_session_id))
    data = json.loads(result)
    assert data["status"] == "ok"


@pytest.mark.unit
async def test_set_user_agent(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.network import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_set_user_agent")
    result = await tool.fn(SetUserAgentInput(user_agent="TestBot/1.0", session_id=mock_session_id))
    data = json.loads(result)
    assert data["status"] == "ok"


@pytest.mark.unit
async def test_block_requests(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.network import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_block_requests")
    result = await tool.fn(
        BlockRequestsInput(patterns=["*.css", "*.png"], session_id=mock_session_id)
    )
    data = json.loads(result)
    assert data["status"] == "ok"


@pytest.mark.unit
async def test_throttle_network_preset(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.network import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_throttle_network")
    result = await tool.fn(ThrottleNetworkInput(session_id=mock_session_id, preset="3g"))
    data = json.loads(result)
    assert data["status"] == "ok"


@pytest.mark.unit
async def test_throttle_network_custom(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.network import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_throttle_network")
    result = await tool.fn(
        ThrottleNetworkInput(
            session_id=mock_session_id,
            latency_ms=200,
            download_bps=100000,
            upload_bps=50000,
        )
    )
    data = json.loads(result)
    assert data["status"] == "ok"


@pytest.mark.unit
async def test_set_cache_disabled(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.network import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_set_cache_disabled")
    result = await tool.fn(SetCacheDisabledInput(session_id=mock_session_id, disabled=True))
    data = json.loads(result)
    assert data["status"] == "ok"
    assert data["cache_disabled"] is True


@pytest.mark.unit
async def test_capture_har(mock_backend: AsyncMock) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.network import register

    mcp = FastMCP("test")
    mgr = SessionManager()
    mgr._backend_manager.select = MagicMock(return_value=mock_backend)
    register(mcp, mgr)

    tool = mcp._tool_manager.get_tool("wavexis_capture_har")
    result = await tool.fn(CaptureHARInput(url="https://example.com"))
    data = json.loads(result)
    assert "har" in data
    assert "entries" in data


@pytest.mark.unit
async def test_intercept_requests(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.network import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_intercept_requests")
    result = await tool.fn(
        InterceptRequestsInput(
            pattern={"urlPattern": "*.js", "resourceType": "script"},
            session_id=mock_session_id,
        )
    )
    data = json.loads(result)
    assert data["status"] == "ok"


@pytest.mark.unit
async def test_mock_response(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.network import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_mock_response")
    result = await tool.fn(
        MockResponseInput(
            url="https://api.example.com/data",
            status=200,
            body='{"ok": true}',
            session_id=mock_session_id,
        )
    )
    data = json.loads(result)
    assert data["status"] == "ok"


@pytest.mark.unit
async def test_network_requests_pagination(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.network import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    requests = [
        {"url": f"https://example.com/r{i}", "method": "GET", "type": "xmlhttprequest"}
        for i in range(10)
    ]
    session_manager_with_mock.get(mock_session_id).backend.eval = AsyncMock(
        return_value=json.dumps(requests)
    )

    tool = mcp._tool_manager.get_tool("wavexis_network_requests")
    result = await tool.fn(NetworkRequestsInput(session_id=mock_session_id, limit=3, offset=2))
    data = json.loads(result)
    assert data["count"] == 3
    assert data["total"] == 10


@pytest.mark.unit
async def test_get_request_body_found(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.models import GetRequestBodyInput
    from wavexis_mcp.tools.network import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    session_manager_with_mock.get(mock_session_id).backend.get_request_body = AsyncMock(
        return_value='{"key": "value"}'
    )

    tool = mcp._tool_manager.get_tool("wavexis_get_request_body")
    result = await tool.fn(GetRequestBodyInput(session_id=mock_session_id, request_id="req-123"))
    data = json.loads(result)
    assert data["found"] is True
    assert data["body"] == '{"key": "value"}'


@pytest.mark.unit
async def test_get_request_body_not_found(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.models import GetRequestBodyInput
    from wavexis_mcp.tools.network import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    session_manager_with_mock.get(mock_session_id).backend.get_request_body = AsyncMock(
        return_value=None
    )

    tool = mcp._tool_manager.get_tool("wavexis_get_request_body")
    result = await tool.fn(GetRequestBodyInput(session_id=mock_session_id, request_id="req-999"))
    data = json.loads(result)
    assert data["found"] is False
    assert data["body"] is None


@pytest.mark.unit
async def test_get_response_body_found(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.models import GetResponseBodyInput
    from wavexis_mcp.tools.network import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    session_manager_with_mock.get(mock_session_id).backend.get_response_body = AsyncMock(
        return_value="<html>OK</html>"
    )

    tool = mcp._tool_manager.get_tool("wavexis_get_response_body")
    result = await tool.fn(GetResponseBodyInput(session_id=mock_session_id, request_id="resp-123"))
    data = json.loads(result)
    assert data["found"] is True
    assert data["body"] == "<html>OK</html>"


@pytest.mark.unit
async def test_get_response_body_not_found(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.models import GetResponseBodyInput
    from wavexis_mcp.tools.network import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    session_manager_with_mock.get(mock_session_id).backend.get_response_body = AsyncMock(
        return_value=None
    )

    tool = mcp._tool_manager.get_tool("wavexis_get_response_body")
    result = await tool.fn(GetResponseBodyInput(session_id=mock_session_id, request_id="resp-999"))
    data = json.loads(result)
    assert data["found"] is False


@pytest.mark.unit
async def test_modify_request(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.models import ModifyRequestInput
    from wavexis_mcp.tools.network import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    session_manager_with_mock.get(mock_session_id).backend.modify_request = AsyncMock()

    tool = mcp._tool_manager.get_tool("wavexis_modify_request")
    result = await tool.fn(
        ModifyRequestInput(
            session_id=mock_session_id,
            pattern={"url": "*api*"},
            modifications={"headers": {"X-Custom": "val"}},
        )
    )
    data = json.loads(result)
    assert data["status"] == "ok"
    assert data["pattern"] == {"url": "*api*"}


@pytest.mark.unit
async def test_modify_request_error(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.models import ModifyRequestInput
    from wavexis_mcp.tools.network import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    session_manager_with_mock.get(mock_session_id).backend.modify_request = AsyncMock(
        side_effect=RuntimeError("not supported")
    )

    tool = mcp._tool_manager.get_tool("wavexis_modify_request")
    result = await tool.fn(
        ModifyRequestInput(
            session_id=mock_session_id,
            pattern={"url": "*"},
            modifications={},
        )
    )
    data = json.loads(result)
    assert "error" in data
    assert data["tool"] == "wavexis_modify_request"


@pytest.mark.unit
async def test_replay_har(session_manager_with_mock: SessionManager, mock_session_id: str) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.models import ReplayHARInput
    from wavexis_mcp.tools.network import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    session_manager_with_mock.get(mock_session_id).backend.replay_har = AsyncMock()

    tool = mcp._tool_manager.get_tool("wavexis_replay_har")
    result = await tool.fn(
        ReplayHARInput(
            har_path="/tmp/test.har",
            session_id=mock_session_id,
        )
    )
    data = json.loads(result)
    assert data["status"] == "ok"
    assert data["har_path"] == "/tmp/test.har"


@pytest.mark.unit
async def test_replay_har_with_url(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.models import ReplayHARInput
    from wavexis_mcp.tools.network import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    session_manager_with_mock.get(mock_session_id).backend.replay_har = AsyncMock()

    tool = mcp._tool_manager.get_tool("wavexis_replay_har")
    result = await tool.fn(
        ReplayHARInput(
            har_path="/tmp/test.har",
            url="https://example.com",
            session_id=mock_session_id,
        )
    )
    data = json.loads(result)
    assert data["status"] == "ok"
    session_manager_with_mock.get(mock_session_id).backend.navigate.assert_awaited()


@pytest.mark.unit
async def test_replay_har_error(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.models import ReplayHARInput
    from wavexis_mcp.tools.network import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    session_manager_with_mock.get(mock_session_id).backend.replay_har = AsyncMock(
        side_effect=FileNotFoundError("har not found")
    )

    tool = mcp._tool_manager.get_tool("wavexis_replay_har")
    result = await tool.fn(
        ReplayHARInput(
            har_path="/nonexistent.har",
            session_id=mock_session_id,
        )
    )
    data = json.loads(result)
    assert "error" in data
    assert data["tool"] == "wavexis_replay_har"


@pytest.mark.unit
async def test_modify_response(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.network import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_modify_response")
    result = await tool.fn(
        ModifyResponseInput(
            session_id=mock_session_id,
            pattern={"urlPattern": "*://api.example.com/*"},
            modifications={"status": 200, "body": '{"ok": true}'},
        )
    )
    data = json.loads(result)
    assert data["status"] == "ok"
    assert data["pattern"] == {"urlPattern": "*://api.example.com/*"}
