"""Unit tests for server CLI, help, and wavexis_act integration."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from wavexis_mcp.session import SessionManager


# ── _parse_args ──────────────────────────────────────────


@pytest.mark.unit
def test_parse_args_defaults() -> None:
    from wavexis_mcp.server import _parse_args

    args = _parse_args([])
    assert args.caps == "core"
    assert args.transport == "stdio"
    assert args.host == "127.0.0.1"
    assert args.port == 8765
    assert args.allow_remote is False
    assert args.rate_limit == 60
    assert args.rate_burst == 10


@pytest.mark.unit
def test_parse_args_http_transport() -> None:
    from wavexis_mcp.server import _parse_args

    args = _parse_args(["--transport", "http", "--port", "9999", "--host", "0.0.0.0"])
    assert args.transport == "http"
    assert args.port == 9999
    assert args.host == "0.0.0.0"


@pytest.mark.unit
def test_parse_args_allow_remote() -> None:
    from wavexis_mcp.server import _parse_args

    args = _parse_args(["--allow-remote"])
    assert args.allow_remote is True


@pytest.mark.unit
def test_parse_args_rate_limit() -> None:
    from wavexis_mcp.server import _parse_args

    args = _parse_args(["--rate-limit", "120", "--rate-burst", "20"])
    assert args.rate_limit == 120
    assert args.rate_burst == 20


@pytest.mark.unit
def test_parse_args_caps() -> None:
    from wavexis_mcp.server import _parse_args

    args = _parse_args(["--caps", "core,network,storage"])
    assert args.caps == "core,network,storage"


# ── _print_help ──────────────────────────────────────────


@pytest.mark.unit
def test_print_help_core(capsys) -> None:
    from wavexis_mcp.server import _print_help

    _print_help("core")
    captured = capsys.readouterr()
    assert "WaveXisMCP" in captured.out
    assert "--caps" in captured.out
    assert "--transport" in captured.out
    assert "core" in captured.out


@pytest.mark.unit
def test_print_help_all(capsys) -> None:
    from wavexis_mcp.server import _print_help

    _print_help("all")
    captured = capsys.readouterr()
    assert "[enabled]" in captured.out


# ── create_server ────────────────────────────────────────


@pytest.mark.unit
def test_create_server_default() -> None:
    from wavexis_mcp.server import create_server

    mcp = create_server("core")
    tools = list(mcp._tool_manager._tools.keys())
    assert "wavexis_screenshot" in tools
    assert "wavexis_navigate" in tools


@pytest.mark.unit
def test_create_server_all_caps() -> None:
    from wavexis_mcp.server import create_server

    mcp = create_server("all")
    tools = list(mcp._tool_manager._tools.keys())
    assert "wavexis_screenshot" in tools
    assert "wavexis_set_headers" in tools
    assert "wavexis_a11y_snapshot" in tools


@pytest.mark.unit
def test_create_server_with_rate_limit() -> None:
    from wavexis_mcp.server import create_server

    mcp = create_server("core", rate_limit=100, rate_burst=15)
    assert mcp is not None


# ── wavexis_act tool ─────────────────────────────────────


@pytest.mark.unit
async def test_wavexis_act_no_match(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.models import ActInput
    from wavexis_mcp.server import create_server

    session_manager_with_mock.get(mock_session_id).backend.a11y_tree = AsyncMock(
        return_value={"children": []}
    )

    from wavexis_mcp import server as server_module
    original = server_module._session_manager
    server_module._session_manager = session_manager_with_mock
    try:
        mcp = create_server("core")
        tool = mcp._tool_manager.get_tool("wavexis_act")
        if tool is None:
            pytest.skip("wavexis_act not available with core caps")
        result = await tool.fn(
            ActInput(
                instruction="click the nonexistent button",
                session_id=mock_session_id,
            )
        )
        data = json.loads(result)
        assert data["status"] == "no_match"
    finally:
        server_module._session_manager = original


@pytest.mark.unit
async def test_wavexis_act_error(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.models import ActInput
    from wavexis_mcp.server import create_server

    session_manager_with_mock.get(mock_session_id).backend.a11y_tree = AsyncMock(
        side_effect=RuntimeError("backend error")
    )

    mcp = create_server("core")
    tool = mcp._tool_manager.get_tool("wavexis_act")
    if tool is None:
        pytest.skip("wavexis_act not available with core caps")

    from wavexis_mcp import server as server_module
    original = server_module._session_manager
    server_module._session_manager = session_manager_with_mock
    try:
        result = await tool.fn(
            ActInput(
                instruction="click submit",
                session_id=mock_session_id,
            )
        )
        data = json.loads(result)
        assert "error" in data
        assert data["tool"] == "wavexis_act"
    finally:
        server_module._session_manager = original


# ── main entry point ─────────────────────────────────────


@pytest.mark.unit
def test_main_stdio(capsys) -> None:
    from wavexis_mcp import server as server_module

    with patch.object(server_module, "_parse_args") as mock_parse:
        mock_parse.return_value = MagicMock(
            caps="core",
            transport="stdio",
            host="127.0.0.1",
            port=8765,
            allow_remote=False,
            rate_limit=60,
            rate_burst=10,
        )
        with patch.object(server_module, "_is_help_request", return_value=False):
            with patch.object(server_module, "create_server") as mock_create:
                mock_mcp = MagicMock()
                mock_create.return_value = mock_mcp
                server_module.main()
                mock_mcp.run.assert_called_once_with(transport="stdio")


@pytest.mark.unit
def test_main_http(capsys) -> None:
    from wavexis_mcp import server as server_module

    with patch.object(server_module, "_parse_args") as mock_parse:
        mock_parse.return_value = MagicMock(
            caps="all",
            transport="http",
            host="127.0.0.1",
            port=9999,
            allow_remote=False,
            rate_limit=60,
            rate_burst=10,
        )
        with patch.object(server_module, "_is_help_request", return_value=False):
            with patch.object(server_module, "create_server") as mock_create:
                mock_mcp = MagicMock()
                mock_create.return_value = mock_mcp
                server_module.main()
                assert mock_mcp.settings.host == "127.0.0.1"
                assert mock_mcp.settings.port == 9999
                mock_mcp.run.assert_called_once_with(transport="sse")


@pytest.mark.unit
def test_main_http_allow_remote(capsys) -> None:
    from wavexis_mcp import server as server_module

    with patch.object(server_module, "_parse_args") as mock_parse:
        mock_parse.return_value = MagicMock(
            caps="all",
            transport="http",
            host="127.0.0.1",
            port=8765,
            allow_remote=True,
            rate_limit=60,
            rate_burst=10,
        )
        with patch.object(server_module, "_is_help_request", return_value=False):
            with patch.object(server_module, "create_server") as mock_create:
                mock_mcp = MagicMock()
                mock_create.return_value = mock_mcp
                server_module.main()
                assert mock_mcp.settings.host == "0.0.0.0"
