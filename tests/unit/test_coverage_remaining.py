"""Targeted tests for remaining coverage gaps after smoke tests."""

from __future__ import annotations

import builtins
import json
import runpy
import sys
import threading
import types
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from wavexis_mcp import server as server_module
from wavexis_mcp.session import SessionManager
from wavexis_mcp.tools.playwright_parity import (
    ClosePageInput,
    CookieListInput,
    FindInput,
    KeyDownInput,
    PressKeysInput,
)


@pytest.fixture
def coverage_mcp(session_manager_with_mock: SessionManager, mock_session_id: str) -> Any:
    """Build a FastMCP server with all tools registered to the mock session."""
    with patch("wavexis.backend.manager.BackendManager") as mock_mgr_cls:
        mock_mgr = MagicMock()
        mock_mgr.list_available = MagicMock(return_value=["cdp"])
        mock_mgr.install_check = MagicMock(return_value={"cdp": "1.0.0"})
        mock_mgr.select = MagicMock(
            return_value=session_manager_with_mock._backend_manager.select()
        )
        mock_mgr_cls.return_value = mock_mgr

        original_session_manager = server_module._session_manager
        server_module._session_manager = session_manager_with_mock
        try:
            mcp = server_module.create_server(caps="all")
            yield mcp
        finally:
            server_module._session_manager = original_session_manager


# -- utility.py


@pytest.mark.unit
async def test_wavexis_backends_exception(coverage_mcp: Any, monkeypatch) -> None:
    class Boom:
        def list_available(self):
            raise RuntimeError("boom")

    monkeypatch.setattr("wavexis.backend.manager.BackendManager", Boom)

    tool = coverage_mcp._tool_manager.get_tool("wavexis_backends")
    result = await tool.fn()
    assert "error" in json.loads(result)


@pytest.mark.unit
async def test_wavexis_invoke_bytes_and_list_output(
    coverage_mcp: Any, session_manager_with_mock: SessionManager, mock_session_id: str, tmp_path
) -> None:
    from wavexis_mcp.models import InvokeInput

    tool = coverage_mcp._tool_manager.get_tool("wavexis_invoke")

    file_path = str(tmp_path / "shot.png")
    result = await tool.fn(
        InvokeInput(session_id=mock_session_id, method="screenshot", output_path=file_path)
    )
    data = json.loads(result)
    assert data["path"] == file_path

    frames_dir = str(tmp_path / "frames")
    result = await tool.fn(
        InvokeInput(
            session_id=mock_session_id,
            method="screencast",
            output_path=frames_dir,
        )
    )
    data = json.loads(result)
    assert data["dir"] == frames_dir


@pytest.mark.unit
async def test_wavexis_invoke_errors_and_dataclass(
    coverage_mcp: Any, session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from wavexis_mcp.models import InvokeInput

    class FakeBackend:
        async def some_method(self, params: dict):
            return {"ok": True, "params": params}

        async def _private(self):
            return "nope"

    session = session_manager_with_mock.get(mock_session_id)
    session.backend = FakeBackend()

    tool = coverage_mcp._tool_manager.get_tool("wavexis_invoke")

    result = await tool.fn(
        InvokeInput(session_id=mock_session_id, method="some_method", params={"x": 1})
    )
    data = json.loads(result)
    assert data["result"]["ok"] is True

    result = await tool.fn(InvokeInput(session_id=mock_session_id, method="missing_method"))
    assert "error" in json.loads(result)

    result = await tool.fn(InvokeInput(session_id=mock_session_id, method="_private"))
    assert "error" in json.loads(result)


@pytest.mark.unit
async def test_wavexis_invoke_ephemeral_with_url(
    coverage_mcp: Any, session_manager_with_mock: SessionManager, monkeypatch
) -> None:
    from wavexis_mcp.models import InvokeInput

    class FakeBackend:
        navigate = AsyncMock()
        screenshot = AsyncMock(return_value=b"png")
        close = AsyncMock()

    fake = FakeBackend()
    monkeypatch.setattr(
        session_manager_with_mock, "acquire_backend", AsyncMock(return_value=(fake, None))
    )
    monkeypatch.setattr(session_manager_with_mock, "release_backend", AsyncMock())

    tool = coverage_mcp._tool_manager.get_tool("wavexis_invoke")
    result = await tool.fn(
        InvokeInput(method="screenshot", url="https://example.com", output_path="/tmp/shot.png")
    )
    data = json.loads(result)
    assert data["status"] == "ok"
    fake.navigate.assert_awaited()


# -- capture.py


@pytest.mark.unit
async def test_screenshot_js_and_selector(
    coverage_mcp: Any, session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from wavexis_mcp.models import ScreenshotInput

    session = session_manager_with_mock.get(mock_session_id)
    session.backend.screenshot_selector = AsyncMock(return_value=b"png")
    session.backend.eval = AsyncMock(return_value="ok")

    tool = coverage_mcp._tool_manager.get_tool("wavexis_screenshot")
    result = await tool.fn(
        ScreenshotInput(
            session_id=mock_session_id,
            url="https://example.com",
            js="window.scrollTo(0,0)",
            selector="#hero",
        )
    )
    data = json.loads(result)
    assert data["status"] == "ok"
    session.backend.screenshot_selector.assert_awaited()
    session.backend.eval.assert_awaited()


@pytest.mark.unit
async def test_pdf_js_branch(
    coverage_mcp: Any, session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from wavexis_mcp.models import PDFInput

    session = session_manager_with_mock.get(mock_session_id)
    session.backend.eval = AsyncMock(return_value="ok")

    tool = coverage_mcp._tool_manager.get_tool("wavexis_pdf")
    result = await tool.fn(
        PDFInput(session_id=mock_session_id, url="https://example.com", js="document.title")
    )
    data = json.loads(result)
    assert data["status"] == "ok"
    session.backend.eval.assert_awaited()


@pytest.mark.unit
async def test_screencast_output_dir(
    coverage_mcp: Any, session_manager_with_mock: SessionManager, mock_session_id: str, tmp_path
) -> None:
    from wavexis_mcp.models import ScreencastInput

    tool = coverage_mcp._tool_manager.get_tool("wavexis_screencast")
    out_dir = str(tmp_path / "screencast_frames")
    result = await tool.fn(
        ScreencastInput(session_id=mock_session_id, duration=0.5, output_dir=out_dir, format="png")
    )
    data = json.loads(result)
    assert data["dir"] == out_dir


@pytest.mark.unit
async def test_page_snapshot_output_path(
    coverage_mcp: Any, session_manager_with_mock: SessionManager, mock_session_id: str, tmp_path
) -> None:
    from wavexis_mcp.models import PageSnapshotInput

    session = session_manager_with_mock.get(mock_session_id)
    session.backend.page_capture_snapshot = AsyncMock(return_value="MHTML-DATA")

    tool = coverage_mcp._tool_manager.get_tool("wavexis_page_snapshot")
    path = str(tmp_path / "snapshot.mhtml")
    result = await tool.fn(PageSnapshotInput(session_id=mock_session_id, output_path=path))
    data = json.loads(result)
    assert data["path"] == path


# -- video.py


@pytest.mark.unit
async def test_video_stop_no_recording(coverage_mcp: Any, mock_session_id: str) -> None:
    from wavexis_mcp.models import VideoStopInput

    tool = coverage_mcp._tool_manager.get_tool("wavexis_video_stop")
    result = await tool.fn(VideoStopInput(session_id=mock_session_id))
    assert "error" in json.loads(result)


@pytest.mark.unit
async def test_video_stop_and_add_chapter(
    coverage_mcp: Any, session_manager_with_mock: SessionManager, mock_session_id: str, tmp_path
) -> None:
    from wavexis_mcp.models import VideoAddChapterInput, VideoRecordInput, VideoStopInput

    tool = coverage_mcp._tool_manager.get_tool("wavexis_video_record")
    result = await tool.fn(
        VideoRecordInput(session_id=mock_session_id, output_path=str(tmp_path / "out.mp4"))
    )
    data = json.loads(result)
    rid = data["recording_id"]

    tool = coverage_mcp._tool_manager.get_tool("wavexis_video_add_chapter")
    result = await tool.fn(
        VideoAddChapterInput(session_id=mock_session_id, recording_id=rid, title="chapter")
    )
    data = json.loads(result)
    assert data["chapter"]["title"] == "chapter"
    assert "timestamp_ms" in data["chapter"]

    tool = coverage_mcp._tool_manager.get_tool("wavexis_video_stop")
    result = await tool.fn(VideoStopInput(session_id=mock_session_id))
    data = json.loads(result)
    assert data["size_bytes"] == 0


# -- playwright_parity.py


@pytest.mark.unit
async def test_key_down_modifiers(
    coverage_mcp: Any, session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:

    session = session_manager_with_mock.get(mock_session_id)
    session.backend.input_dispatch_key_event = AsyncMock()

    tool = coverage_mcp._tool_manager.get_tool("wavexis_key_down")
    await tool.fn(
        KeyDownInput(
            session_id=mock_session_id,
            key="A",
            alt=True,
            ctrl=True,
            meta=True,
            shift=True,
        )
    )
    call = session.backend.input_dispatch_key_event.await_args
    assert call.kwargs["modifiers"] == 15


@pytest.mark.unit
async def test_press_keys_delay(
    coverage_mcp: Any, session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:

    session = session_manager_with_mock.get(mock_session_id)
    session.backend.input_dispatch_key_event = AsyncMock()

    tool = coverage_mcp._tool_manager.get_tool("wavexis_press_keys")
    await tool.fn(PressKeysInput(session_id=mock_session_id, text="ab", delay=1))
    assert session.backend.input_dispatch_key_event.await_count == 4


@pytest.mark.unit
async def test_cookie_list_filters(
    coverage_mcp: Any, session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:

    session = session_manager_with_mock.get(mock_session_id)
    session.backend.get_cookies = AsyncMock(
        return_value=[
            {"name": "a", "domain": "example.com", "path": "/"},
            {"name": "b", "domain": "other.com", "path": "/x"},
        ]
    )

    tool = coverage_mcp._tool_manager.get_tool("wavexis_cookie_list")
    result = await tool.fn(
        CookieListInput(session_id=mock_session_id, name="a", domain="example.com", path="/")
    )
    data = json.loads(result)
    assert data["count"] == 1


@pytest.mark.unit
async def test_close_page_with_tab_id(
    coverage_mcp: Any, session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:

    session = session_manager_with_mock.get(mock_session_id)
    session.backend.target_close_target = AsyncMock()

    tool = coverage_mcp._tool_manager.get_tool("wavexis_close_page")
    result = await tool.fn(ClosePageInput(session_id=mock_session_id, tab_id="tab-1"))
    data = json.loads(result)
    assert data["closed"] == "tab-1"


@pytest.mark.unit
async def test_wavexis_find_and_get_config_exception(
    coverage_mcp: Any, session_manager_with_mock: SessionManager, mock_session_id: str, monkeypatch
) -> None:

    session = session_manager_with_mock.get(mock_session_id)
    session.backend.a11y_tree = AsyncMock(
        return_value=[{"role": "button", "name": "Submit", "children": []}]
    )

    tool = coverage_mcp._tool_manager.get_tool("wavexis_find")
    result = await tool.fn(FindInput(session_id=mock_session_id, text="submit"))
    data = json.loads(result)
    assert data["count"] == 1

    class Boom:
        def list_available(self):
            raise RuntimeError("boom")

    monkeypatch.setattr("wavexis.backend.manager.BackendManager", Boom)
    tool = coverage_mcp._tool_manager.get_tool("wavexis_get_config")
    result = await tool.fn(None)
    assert "error" in json.loads(result)


# -- data.py


@pytest.mark.unit
async def test_extract_with_selector(
    coverage_mcp: Any, session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from wavexis_mcp.models import ExtractInput

    session = session_manager_with_mock.get(mock_session_id)
    session.backend.eval = AsyncMock(side_effect=["2", "Title 1", "Body 1", "Title 2", "Body 2"])

    tool = coverage_mcp._tool_manager.get_tool("wavexis_extract")
    result = await tool.fn(
        ExtractInput(
            session_id=mock_session_id,
            url="https://example.com",
            selector=".post",
            schema={"title": "h2", "body": "p"},
        )
    )
    data = json.loads(result)
    assert data["rows"] == 2


@pytest.mark.unit
async def test_crawl_same_origin(
    coverage_mcp: Any, session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from wavexis_mcp.models import CrawlInput

    session = session_manager_with_mock.get(mock_session_id)
    session.backend.eval = AsyncMock(
        side_effect=[
            "",
            ["https://example.com/page2", "https://other.com/ignored"],
            "",
            [],
        ]
    )

    tool = coverage_mcp._tool_manager.get_tool("wavexis_crawl")
    result = await tool.fn(
        CrawlInput(
            session_id=mock_session_id,
            start_url="https://example.com",
            max_depth=1,
            max_pages=2,
            same_origin=True,
        )
    )
    data = json.loads(result)
    assert data["pages_crawled"] == 2


@pytest.mark.unit
async def test_visual_diff_import_missing(
    coverage_mcp: Any, mock_session_id: str, monkeypatch
) -> None:
    from wavexis_mcp.models import VisualDiffInput

    real_import = (
        __builtins__["__import__"] if isinstance(__builtins__, dict) else __builtins__.__import__
    )

    def fake_import(name, *args, **kwargs):
        if name == "wavexis.actions.visual_diff":
            raise ImportError("no module")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", fake_import)

    tool = coverage_mcp._tool_manager.get_tool("wavexis_visual_diff")
    result = await tool.fn(
        VisualDiffInput(
            session_id=mock_session_id,
            url="https://example.com",
            baseline_path="/tmp/base.png",
        )
    )
    data = json.loads(result)
    assert data["status"] == "not_implemented"


# -- a11y.py


@pytest.mark.unit
def test_build_a11y_tree_branches() -> None:
    from wavexis_mcp.tools.a11y import _build_a11y_tree, _extract_name, _extract_role

    assert _extract_role({"role": {"value": "button"}}) == "button"
    assert _extract_name({"name": {"value": "OK"}}) == "OK"

    flat = {
        "nodes": [
            {"nodeId": "1", "role": "WebArea", "name": "page"},
            {"nodeId": "2", "parentId": "1", "role": "button", "name": "Submit"},
            {"nodeId": "3", "childIds": ["2"], "role": "generic", "name": ""},
        ]
    }
    tree = _build_a11y_tree(flat)
    assert len(tree) == 1
    assert tree[0]["role"] == "WebArea"

    assert _build_a11y_tree({"foo": "bar"}) == []
    assert _build_a11y_tree([{"role": "heading", "name": "Hi"}]) == [
        {"role": "heading", "name": "Hi"}
    ]
    assert _build_a11y_tree(None) == []


# -- server.py


@pytest.mark.unit
def test_parse_caps_and_help_request() -> None:
    assert server_module.parse_caps(["--caps", "network"]) == "network"
    assert server_module.parse_caps(["--caps=network"]) == "network"
    assert server_module._is_help_request(["--help"]) is True
    assert server_module._is_help_request(["-h"]) is True
    assert server_module._is_help_request([]) is False


@pytest.mark.unit
def test_print_help_and_startup(capsys) -> None:
    server_module._print_help("core")
    out = capsys.readouterr().out
    assert "WaveXisMCP" in out

    server_module._print_startup_info(server_module.CapsManager("core"))
    err = capsys.readouterr().err
    assert "enabled tiers" in err


@pytest.mark.unit
async def test_lifespan_and_atexit_cleanup(coverage_mcp: Any, monkeypatch) -> None:
    async with server_module.lifespan(None):
        pass

    fake_mgr = MagicMock()
    fake_mgr.cleanup_all = AsyncMock()
    monkeypatch.setattr(server_module, "_session_manager", fake_mgr)

    t = threading.Thread(target=server_module._atexit_cleanup)
    t.start()
    t.join()
    fake_mgr.cleanup_all.assert_awaited_once()


@pytest.mark.unit
async def test_atexit_cleanup_exception(coverage_mcp: Any, monkeypatch) -> None:
    import threading

    fake_mgr = MagicMock()
    fake_mgr.cleanup_all = AsyncMock(side_effect=RuntimeError("boom"))
    monkeypatch.setattr(server_module, "_session_manager", fake_mgr)

    t = threading.Thread(target=server_module._atexit_cleanup)
    t.start()
    t.join()


@pytest.mark.unit
async def test_wavexis_act_wrapper(
    coverage_mcp: Any, session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from wavexis_mcp.models import ActInput

    session = session_manager_with_mock.get(mock_session_id)
    session.backend.a11y_tree = AsyncMock(
        return_value={
            "role": "WebArea",
            "name": "Test",
            "children": [{"role": "button", "name": "Submit", "children": []}],
        }
    )
    session.backend.click = AsyncMock()

    tool = coverage_mcp._tool_manager.get_tool("wavexis_act")
    result = await tool.fn(
        ActInput(session_id=mock_session_id, instruction="click the Submit button")
    )
    data = json.loads(result)
    assert data["action"] == "click"


@pytest.mark.unit
def test_build_a11y_tree_remaining_branches() -> None:
    from wavexis_mcp.tools.a11y import _build_a11y_tree

    # empty nodes -> line 93
    assert _build_a11y_tree({"nodes": []}) == []
    # missing nodeId -> lines 101 and 112
    assert _build_a11y_tree({"nodes": [{"role": "button", "name": "A"}]}) == []
    # all nodes visited -> lines 128 and 131
    raw = {
        "nodes": [
            {"nodeId": "1", "parentId": "2", "role": "A", "name": "a"},
            {"nodeId": "2", "parentId": "1", "role": "B", "name": "b"},
        ]
    }
    tree = _build_a11y_tree(raw)
    assert len(tree) == 1


@pytest.mark.unit
async def test_wavexis_axe_audit_url_branch(
    coverage_mcp: Any, session_manager_with_mock: SessionManager, mock_session_id: str, monkeypatch
) -> None:
    from wavexis_mcp.models import AxeAuditInput

    session = session_manager_with_mock.get(mock_session_id)
    session.backend.axe_audit = AsyncMock(return_value={"violations": []})
    monkeypatch.setattr(
        session_manager_with_mock,
        "acquire_backend",
        AsyncMock(return_value=(session.backend, None)),
    )
    monkeypatch.setattr(session_manager_with_mock, "release_backend", AsyncMock())

    tool = coverage_mcp._tool_manager.get_tool("wavexis_axe_audit")
    result = await tool.fn(AxeAuditInput(url="https://example.com"))
    data = json.loads(result)
    assert data["violations"] == []
    session.backend.navigate.assert_awaited()
    session.backend.axe_audit.assert_awaited()


@pytest.mark.unit
async def test_wavexis_crawl_visited(
    coverage_mcp: Any, session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from wavexis_mcp.models import CrawlInput

    session = session_manager_with_mock.get(mock_session_id)
    start = "https://example.com"
    page3 = "https://example.com/page3"
    # Duplicate link ensures the queued URL is skipped as already visited.
    session.backend.eval = AsyncMock(side_effect=["", [page3, page3], "", []])

    tool = coverage_mcp._tool_manager.get_tool("wavexis_crawl")
    result = await tool.fn(
        CrawlInput(
            session_id=mock_session_id,
            start_url=start,
            max_depth=1,
            max_pages=3,
            same_origin=True,
        )
    )
    data = json.loads(result)
    assert data["pages_crawled"] == 2


@pytest.mark.unit
async def test_wavexis_crawl_exception(
    coverage_mcp: Any, session_manager_with_mock: SessionManager, monkeypatch
) -> None:
    from wavexis_mcp.models import CrawlInput

    monkeypatch.setattr(
        session_manager_with_mock, "acquire_backend", AsyncMock(side_effect=RuntimeError("boom"))
    )

    tool = coverage_mcp._tool_manager.get_tool("wavexis_crawl")
    result = await tool.fn(CrawlInput(start_url="https://example.com", max_depth=1, max_pages=1))
    assert "error" in json.loads(result)


@pytest.mark.unit
async def test_visual_diff_success_with_output_path(
    coverage_mcp: Any,
    session_manager_with_mock: SessionManager,
    mock_session_id: str,
    tmp_path,
    monkeypatch,
) -> None:
    from wavexis_mcp.models import VisualDiffInput

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "wavexis.actions.visual_diff":
            mod = types.ModuleType("wavexis.actions.visual_diff")

            class VisualDiffParams:
                def __init__(
                    self,
                    url="",
                    baseline_path="",
                    selector=None,
                    threshold=10,
                    wait=None,
                    browser=None,
                ):
                    self.url = url
                    self.baseline_path = baseline_path
                    self.selector = selector
                    self.threshold = threshold
                    self.wait = wait
                    self.browser = browser

            class VisualDiffAction:
                def __init__(self, params=None):
                    self.params = params

                async def execute(self, backend):
                    return {
                        "diff_count": 10,
                        "diff_percentage": 0.5,
                        "total_pixels": 100,
                        "threshold": 25,
                        "diff_base64": "ZGlmZg==",
                    }

            mod.VisualDiffAction = VisualDiffAction
            mod.VisualDiffParams = VisualDiffParams
            return mod
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    baseline = tmp_path / "base.png"
    baseline.write_bytes(b"baseline")
    out = tmp_path / "diff.png"

    tool = coverage_mcp._tool_manager.get_tool("wavexis_visual_diff")
    result = await tool.fn(
        VisualDiffInput(
            session_id=mock_session_id,
            url="https://example.com",
            baseline_path=str(baseline),
            output_path=str(out),
        )
    )
    data = json.loads(result)
    assert data["diff_path"] == str(out)
    assert out.exists()


@pytest.mark.unit
async def test_invoke_base64_branches(
    coverage_mcp: Any, session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from wavexis_mcp.models import InvokeInput

    tool = coverage_mcp._tool_manager.get_tool("wavexis_invoke")

    result = await tool.fn(InvokeInput(session_id=mock_session_id, method="screenshot"))
    data = json.loads(result)
    assert data["status"] == "ok"
    assert "base64" in data

    result = await tool.fn(InvokeInput(session_id=mock_session_id, method="screencast"))
    data = json.loads(result)
    assert data["status"] == "ok"
    assert "base64" in data
    assert data["count"] == 1


@pytest.mark.unit
async def test_video_stop_output_path_and_base64(
    coverage_mcp: Any, session_manager_with_mock: SessionManager, mock_session_id: str, tmp_path
) -> None:
    from wavexis_mcp.models import VideoRecordInput, VideoStopInput
    from wavexis_mcp.tools import video as video_module

    tool_record = coverage_mcp._tool_manager.get_tool("wavexis_video_record")
    tool_stop = coverage_mcp._tool_manager.get_tool("wavexis_video_stop")

    # Save to file branch
    video_module._recordings.clear()
    result = await tool_record.fn(
        VideoRecordInput(session_id=mock_session_id, output_path=str(tmp_path / "out.mp4"))
    )
    rid = json.loads(result)["recording_id"]
    video_module._recordings[rid]["frames"].append(b"frame1")

    result = await tool_stop.fn(
        VideoStopInput(session_id=mock_session_id, output_path=str(tmp_path / "out.mp4"))
    )
    data = json.loads(result)
    assert data["path"] == str(tmp_path / "out.mp4")

    # Base64 branch
    video_module._recordings.clear()
    result = await tool_record.fn(VideoRecordInput(session_id=mock_session_id))
    rid = json.loads(result)["recording_id"]
    video_module._recordings[rid]["frames"].append(b"frame2")

    result = await tool_stop.fn(VideoStopInput(session_id=mock_session_id))
    data = json.loads(result)
    assert "base64" in data


@pytest.mark.unit
async def test_video_add_chapter_exception(coverage_mcp: Any, mock_session_id: str) -> None:
    from wavexis_mcp.models import VideoAddChapterInput
    from wavexis_mcp.tools import video as video_module

    video_module._recordings["bad"] = "not-a-dict"

    tool = coverage_mcp._tool_manager.get_tool("wavexis_video_add_chapter")
    result = await tool.fn(
        VideoAddChapterInput(session_id=mock_session_id, recording_id="bad", title="x")
    )
    assert "error" in json.loads(result)
    del video_module._recordings["bad"]


@pytest.mark.unit
async def test_wavexis_find_limit(
    coverage_mcp: Any, session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    session = session_manager_with_mock.get(mock_session_id)
    session.backend.a11y_tree = AsyncMock(
        return_value={
            "role": "WebArea",
            "name": "root",
            "children": [
                {"role": "button", "name": "Submit", "children": []},
                {"role": "button", "name": "Submit", "children": []},
            ],
        }
    )

    tool = coverage_mcp._tool_manager.get_tool("wavexis_find")
    result = await tool.fn(FindInput(session_id=mock_session_id, text="submit", limit=1))
    data = json.loads(result)
    assert data["count"] == 1


@pytest.mark.unit
def test_server_main_help_branch(monkeypatch) -> None:
    from types import SimpleNamespace

    captured: dict[str, Any] = {}
    monkeypatch.setattr(server_module, "_is_help_request", lambda: True)
    monkeypatch.setattr(
        server_module, "_print_help", lambda caps: captured.__setitem__("caps", caps)
    )
    monkeypatch.setattr(server_module, "_parse_args", lambda: SimpleNamespace(caps="network"))
    server_module.main()
    assert captured["caps"] == "network"


@pytest.mark.unit
def test_server_main_guard() -> None:
    with pytest.raises(SystemExit):
        sys.argv = ["wavexis-mcp", "--help"]
        runpy.run_module("wavexis_mcp.server", run_name="__main__")
