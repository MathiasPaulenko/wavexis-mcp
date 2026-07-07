"""Integration tests for HTTP transport (Phase 8)."""

from __future__ import annotations

import pytest

from wavexis_mcp.server import _parse_args


class TestCLIParsing:
    """Tests for CLI argument parsing."""

    @pytest.mark.unit
    def test_default_args(self) -> None:
        args = _parse_args([])
        assert args.transport == "stdio"
        assert args.host == "127.0.0.1"
        assert args.port == 8765
        assert args.caps == "core"
        assert args.allow_remote is False
        assert args.rate_limit == 60
        assert args.rate_burst == 10

    @pytest.mark.unit
    def test_http_transport(self) -> None:
        args = _parse_args(["--transport", "http", "--port", "3000"])
        assert args.transport == "http"
        assert args.port == 3000

    @pytest.mark.unit
    def test_allow_remote(self) -> None:
        args = _parse_args(["--transport", "http", "--allow-remote"])
        assert args.allow_remote is True

    @pytest.mark.unit
    def test_rate_limit_config(self) -> None:
        args = _parse_args(["--rate-limit", "10", "--rate-burst", "5"])
        assert args.rate_limit == 10
        assert args.rate_burst == 5

    @pytest.mark.unit
    def test_caps_arg(self) -> None:
        args = _parse_args(["--caps", "all"])
        assert args.caps == "all"

    @pytest.mark.unit
    def test_host_arg(self) -> None:
        args = _parse_args(["--transport", "http", "--host", "0.0.0.0"])
        assert args.host == "0.0.0.0"


class TestServerCreation:
    """Tests for server creation with M1-M4 features."""

    @pytest.mark.unit
    def test_create_server_with_rate_limit(self) -> None:
        from wavexis_mcp.server import create_server

        mcp = create_server(caps="core", rate_limit=10, rate_burst=5)
        assert mcp is not None

    @pytest.mark.unit
    def test_create_server_all_caps(self) -> None:
        from wavexis_mcp.server import create_server

        mcp = create_server(caps="all")
        assert mcp is not None
