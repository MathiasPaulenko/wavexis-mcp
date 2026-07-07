"""Unit tests for interactions tools."""

from __future__ import annotations

import json

import pytest

from wavexis_mcp.models import (
    DialogAcceptInput,
    DialogDismissInput,
    GrantPermissionInput,
    InterceptDownloadInput,
    ResetPermissionsInput,
)
from wavexis_mcp.session import SessionManager


@pytest.mark.unit
async def test_dialog_accept(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.interactions import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_dialog_accept")
    result = await tool.fn(DialogAcceptInput(prompt_text="yes", session_id=mock_session_id))
    data = json.loads(result)
    assert data["status"] == "ok"


@pytest.mark.unit
async def test_dialog_dismiss(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.interactions import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_dialog_dismiss")
    result = await tool.fn(DialogDismissInput(session_id=mock_session_id))
    data = json.loads(result)
    assert data["status"] == "ok"


@pytest.mark.unit
async def test_intercept_download_base64(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.interactions import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_intercept_download")
    result = await tool.fn(InterceptDownloadInput(pattern=".*\\.pdf", session_id=mock_session_id))
    data = json.loads(result)
    assert data["status"] == "ok"
    assert data["size_bytes"] > 0
    assert "base64" in data


@pytest.mark.unit
async def test_intercept_download_file(
    session_manager_with_mock: SessionManager, mock_session_id: str, tmp_path
) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.interactions import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    out = tmp_path / "download.bin"
    tool = mcp._tool_manager.get_tool("wavexis_intercept_download")
    result = await tool.fn(
        InterceptDownloadInput(
            pattern=".*",
            output_path=str(out),
            session_id=mock_session_id,
        )
    )
    data = json.loads(result)
    assert data["path"] == str(out)
    assert out.exists()


@pytest.mark.unit
async def test_grant_permission(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.interactions import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_grant_permission")
    result = await tool.fn(
        GrantPermissionInput(permission="geolocation", session_id=mock_session_id)
    )
    data = json.loads(result)
    assert data["status"] == "ok"
    assert data["permission"] == "geolocation"


@pytest.mark.unit
async def test_reset_permissions(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.interactions import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_reset_permissions")
    result = await tool.fn(ResetPermissionsInput(session_id=mock_session_id))
    data = json.loads(result)
    assert data["status"] == "ok"
