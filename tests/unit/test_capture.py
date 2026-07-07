"""Unit tests for capture tools."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from wavexis_mcp.models import (
    AnnotatedScreenshotInput,
    PDFInput,
    ScrapeInput,
    ScreencastInput,
    ScreenshotInput,
)
from wavexis_mcp.session import SessionManager


@pytest.mark.unit
async def test_screenshot_stateless(mock_backend: AsyncMock, tmp_path) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.capture import register

    mcp = FastMCP("test")
    mgr = SessionManager()
    mgr._backend_manager.select = MagicMock(return_value=mock_backend)
    register(mcp, mgr)

    tool = mcp._tool_manager.get_tool("wavexis_screenshot")
    out = tmp_path / "shot.png"
    result = await tool.fn(ScreenshotInput(url="https://example.com", output_path=str(out)))
    data = json.loads(result)
    assert data["status"] == "ok"
    assert data["size_bytes"] > 0
    assert out.exists()


@pytest.mark.unit
async def test_screenshot_base64(mock_backend: AsyncMock) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.capture import register

    mcp = FastMCP("test")
    mgr = SessionManager()
    mgr._backend_manager.select = MagicMock(return_value=mock_backend)
    register(mcp, mgr)

    tool = mcp._tool_manager.get_tool("wavexis_screenshot")
    result = await tool.fn(ScreenshotInput(url="https://example.com"))
    data = json.loads(result)
    assert data["status"] == "ok"
    assert "base64" in data
    assert data["format"] == "png"


@pytest.mark.unit
async def test_pdf(mock_backend: AsyncMock) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.capture import register

    mcp = FastMCP("test")
    mgr = SessionManager()
    mgr._backend_manager.select = MagicMock(return_value=mock_backend)
    register(mcp, mgr)

    tool = mcp._tool_manager.get_tool("wavexis_pdf")
    result = await tool.fn(PDFInput(url="https://example.com"))
    data = json.loads(result)
    assert data["status"] == "ok"
    assert "base64" in data


@pytest.mark.unit
async def test_scrape_pagination(mock_backend: AsyncMock) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.capture import register

    mcp = FastMCP("test")
    mgr = SessionManager()
    mgr._backend_manager.select = MagicMock(return_value=mock_backend)
    register(mcp, mgr)

    tool = mcp._tool_manager.get_tool("wavexis_scrape")
    result = await tool.fn(ScrapeInput(urls=["https://a.com", "https://b.com"], limit=1, offset=0))
    data = json.loads(result)
    assert data["count"] == 1
    assert data["total"] == 2


@pytest.mark.unit
async def test_screencast(mock_backend: AsyncMock) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.capture import register

    mcp = FastMCP("test")
    mgr = SessionManager()
    mgr._backend_manager.select = MagicMock(return_value=mock_backend)
    register(mcp, mgr)

    tool = mcp._tool_manager.get_tool("wavexis_screencast")
    result = await tool.fn(ScreencastInput(url="https://example.com", duration=1.0))
    data = json.loads(result)
    assert data["count"] >= 1


@pytest.mark.unit
async def test_annotated_screenshot(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.capture import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_annotated_screenshot")
    result = await tool.fn(
        AnnotatedScreenshotInput(
            session_id=mock_session_id,
            selectors=["button#submit", "input#email"],
        )
    )
    data = json.loads(result)
    assert data["status"] == "ok"
    assert "base64" in data
    assert data["labels"] == {"@e1": "button#submit"}


@pytest.mark.unit
async def test_annotated_screenshot_file(
    session_manager_with_mock: SessionManager, mock_session_id: str, tmp_path
) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.capture import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    out = tmp_path / "annotated.png"
    tool = mcp._tool_manager.get_tool("wavexis_annotated_screenshot")
    result = await tool.fn(
        AnnotatedScreenshotInput(
            session_id=mock_session_id,
            selectors=["button#submit"],
            output_path=str(out),
        )
    )
    data = json.loads(result)
    assert data["status"] == "ok"
    assert data["labels"] == {"@e1": "button#submit"}
    assert out.exists()
