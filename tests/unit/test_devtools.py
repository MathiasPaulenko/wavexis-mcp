"""Unit tests for DevTools tools."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock

import pytest

from wavexis_mcp.models import (
    BrowserLogsInput,
    ConsoleMessagesInput,
    CSSGetComputedInput,
    CSSGetRulesInput,
    CSSGetStylesheetsInput,
    CSSGetStylesInput,
    DebugGetListenersInput,
    DebugPauseInput,
    DebugRemoveBreakpointInput,
    DebugSetBreakpointFunctionInput,
    DebugSetBreakpointInput,
    DebugStepInput,
    GetSecurityStateInput,
    GetWindowBoundsInput,
    IgnoreCertErrorsInput,
    OverlayClearInput,
    OverlayHighlightInput,
    PerfCoverageInput,
    PerfCSSCoverageInput,
    PerfHeapSnapshotInput,
    PerfMetricsInput,
    PerfProfileInput,
    PerfTraceInput,
    SetWindowBoundsInput,
)
from wavexis_mcp.session import SessionManager

SID = "test-session-id"


def _register(mcp, mgr):
    from wavexis_mcp.tools.devtools import register

    register(mcp, mgr)


# ── Performance (6) ──


@pytest.mark.unit
async def test_perf_metrics(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_perf_metrics")
    result = await tool.fn(PerfMetricsInput(session_id=mock_session_id))
    data = json.loads(result)
    assert "metrics" in data
    assert data["metrics"]["LCP"] == 1234


@pytest.mark.unit
async def test_perf_trace(session_manager_with_mock: SessionManager, mock_session_id: str) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_perf_trace")
    result = await tool.fn(PerfTraceInput(session_id=mock_session_id, duration_ms=1000))
    data = json.loads(result)
    assert "trace" in data


@pytest.mark.unit
async def test_perf_trace_file(
    session_manager_with_mock: SessionManager, mock_session_id: str, tmp_path
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    out = tmp_path / "trace.json"
    tool = mcp._tool_manager.get_tool("wavexis_perf_trace")
    result = await tool.fn(PerfTraceInput(session_id=mock_session_id, output_path=str(out)))
    data = json.loads(result)
    assert data["path"] == str(out)
    assert out.exists()


@pytest.mark.unit
async def test_perf_profile(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_perf_profile")
    result = await tool.fn(PerfProfileInput(session_id=mock_session_id))
    data = json.loads(result)
    assert "profile" in data


@pytest.mark.unit
async def test_perf_heap_snapshot(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_perf_heap_snapshot")
    result = await tool.fn(PerfHeapSnapshotInput(session_id=mock_session_id))
    data = json.loads(result)
    assert "snapshot" in data


@pytest.mark.unit
async def test_perf_coverage(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_perf_coverage")
    result = await tool.fn(PerfCoverageInput(session_id=mock_session_id))
    data = json.loads(result)
    assert "coverage" in data
    assert data["scripts"] == 1


@pytest.mark.unit
async def test_perf_css_coverage(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_perf_css_coverage")
    result = await tool.fn(PerfCSSCoverageInput(session_id=mock_session_id))
    data = json.loads(result)
    assert "coverage" in data


# ── CSS (4) ──


@pytest.mark.unit
async def test_css_get_styles(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_css_get_styles")
    result = await tool.fn(CSSGetStylesInput(selector="h1", session_id=mock_session_id))
    data = json.loads(result)
    assert "styles" in data


@pytest.mark.unit
async def test_css_get_stylesheets(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_css_get_stylesheets")
    result = await tool.fn(CSSGetStylesheetsInput(session_id=mock_session_id))
    data = json.loads(result)
    assert data["count"] == 1


@pytest.mark.unit
async def test_css_get_rules(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_css_get_rules")
    result = await tool.fn(CSSGetRulesInput(stylesheet_id="s1", session_id=mock_session_id))
    data = json.loads(result)
    assert data["count"] == 1


@pytest.mark.unit
async def test_css_get_computed(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_css_get_computed")
    result = await tool.fn(CSSGetComputedInput(selector="h1", session_id=mock_session_id))
    data = json.loads(result)
    assert data["computed"]["display"] == "block"


# ── Debugging (9) ──


@pytest.mark.unit
async def test_debug_set_breakpoint(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_debug_set_breakpoint")
    result = await tool.fn(
        DebugSetBreakpointInput(
            url="https://example.com/script.js", line=10, session_id=mock_session_id
        )
    )
    data = json.loads(result)
    assert data["breakpoint_id"] == "bp-1"


@pytest.mark.unit
async def test_debug_set_breakpoint_function(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_debug_set_breakpoint_function")
    result = await tool.fn(
        DebugSetBreakpointFunctionInput(function_name="myFunc", session_id=mock_session_id)
    )
    data = json.loads(result)
    assert data["breakpoint_id"] == "bp-2"


@pytest.mark.unit
async def test_debug_remove_breakpoint(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_debug_remove_breakpoint")
    result = await tool.fn(
        DebugRemoveBreakpointInput(breakpoint_id="bp-1", session_id=mock_session_id)
    )
    data = json.loads(result)
    assert data["status"] == "ok"


@pytest.mark.unit
async def test_debug_step_over(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_debug_step_over")
    result = await tool.fn(DebugStepInput(session_id=mock_session_id))
    data = json.loads(result)
    assert data["status"] == "ok"


@pytest.mark.unit
async def test_debug_step_into(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_debug_step_into")
    result = await tool.fn(DebugStepInput(session_id=mock_session_id))
    data = json.loads(result)
    assert data["status"] == "ok"


@pytest.mark.unit
async def test_debug_step_out(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_debug_step_out")
    result = await tool.fn(DebugStepInput(session_id=mock_session_id))
    data = json.loads(result)
    assert data["status"] == "ok"


@pytest.mark.unit
async def test_debug_pause(session_manager_with_mock: SessionManager, mock_session_id: str) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_debug_pause")
    result = await tool.fn(DebugPauseInput(session_id=mock_session_id))
    data = json.loads(result)
    assert data["status"] == "ok"


@pytest.mark.unit
async def test_debug_resume(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_debug_resume")
    result = await tool.fn(DebugPauseInput(session_id=mock_session_id))
    data = json.loads(result)
    assert data["status"] == "ok"


@pytest.mark.unit
async def test_debug_get_listeners(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_debug_get_listeners")
    result = await tool.fn(DebugGetListenersInput(selector="button", session_id=mock_session_id))
    data = json.loads(result)
    assert data["count"] == 1
    assert data["listeners"][0]["type"] == "click"


# ── Overlay (2) ──


@pytest.mark.unit
async def test_overlay_highlight(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_overlay_highlight")
    result = await tool.fn(OverlayHighlightInput(selector="h1", session_id=mock_session_id))
    data = json.loads(result)
    assert data["status"] == "ok"


@pytest.mark.unit
async def test_overlay_clear(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_overlay_clear")
    result = await tool.fn(OverlayClearInput(session_id=mock_session_id))
    data = json.loads(result)
    assert data["status"] == "ok"


# ── Console & Logs (2) ──


@pytest.mark.unit
async def test_console_messages_pagination(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    messages = [{"level": "error", "text": f"err {i}", "url": "", "line": i} for i in range(10)]
    session_manager_with_mock.get(mock_session_id).backend.capture_console = AsyncMock(
        return_value=messages
    )

    tool = mcp._tool_manager.get_tool("wavexis_console_messages")
    result = await tool.fn(
        ConsoleMessagesInput(session_id=mock_session_id, limit=3, offset=2, all=True)
    )
    data = json.loads(result)
    assert data["count"] == 3
    assert data["total"] == 10


@pytest.mark.unit
async def test_browser_logs(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_browser_logs")
    result = await tool.fn(BrowserLogsInput(session_id=mock_session_id))
    data = json.loads(result)
    assert data["count"] == 1


# ── Security (2) ──


@pytest.mark.unit
async def test_get_security_state(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_get_security_state")
    result = await tool.fn(GetSecurityStateInput(session_id=mock_session_id))
    data = json.loads(result)
    assert data["state"]["state"] == "secure"


@pytest.mark.unit
async def test_ignore_cert_errors(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_ignore_cert_errors")
    result = await tool.fn(IgnoreCertErrorsInput(ignore=True, session_id=mock_session_id))
    data = json.loads(result)
    assert data["status"] == "ok"
    assert data["ignore"] is True


# ── Window (2) ──


@pytest.mark.unit
async def test_get_window_bounds(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_get_window_bounds")
    result = await tool.fn(GetWindowBoundsInput(session_id=mock_session_id))
    data = json.loads(result)
    assert data["width"] == 1280
    assert data["height"] == 800


@pytest.mark.unit
async def test_set_window_bounds(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_set_window_bounds")
    result = await tool.fn(
        SetWindowBoundsInput(width=1920, height=1080, x=100, y=50, session_id=mock_session_id)
    )
    data = json.loads(result)
    assert data["status"] == "ok"
    assert data["width"] == 1920
