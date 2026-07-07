"""Pytest configuration and fixtures for WaveXisMCP tests."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from wavexis_mcp.session import SessionManager


@pytest.fixture
def mock_backend() -> AsyncMock:
    """Return a mock backend that implements AbstractBackend async methods."""
    backend = AsyncMock()
    backend.launch = AsyncMock()
    backend.close = AsyncMock()
    backend.navigate = AsyncMock()
    backend.screenshot = AsyncMock(return_value=b"\x89PNG\r\n\x1a\n")
    backend.screenshot_selector = AsyncMock(return_value=b"\x89PNG\r\n\x1a\n")
    backend.eval = AsyncMock(return_value="result")
    backend.go_back = AsyncMock()
    backend.go_forward = AsyncMock()
    backend.reload = AsyncMock()
    backend.stop_loading = AsyncMock()
    backend.wait_for = AsyncMock()
    backend.pdf = AsyncMock(return_value=b"%PDF-1.4")
    backend.screencast = AsyncMock(return_value=[b"\x89PNG\r\n\x1a\n"])
    backend.list_tabs = AsyncMock(return_value=[{"id": "1", "url": "about:blank"}])
    backend.new_tab = AsyncMock(return_value="tab-2")
    backend.close_tab = AsyncMock()
    backend.activate_tab = AsyncMock()
    backend.dom_get = AsyncMock(return_value="<h1>Hello</h1>")
    backend.dom_query = AsyncMock(return_value=[{"tag": "div", "text": "hi"}])
    backend.dom_set_attr = AsyncMock()
    backend.dom_get_attr = AsyncMock(return_value="value")
    backend.dom_remove_attr = AsyncMock()
    backend.dom_remove = AsyncMock()
    backend.dom_focus = AsyncMock()
    backend.dom_scroll = AsyncMock()
    backend.dom_snapshot = AsyncMock(return_value={"documents": []})
    backend.click = AsyncMock()
    backend.type_text = AsyncMock()
    backend.fill = AsyncMock()
    backend.select_option = AsyncMock()
    backend.hover = AsyncMock()
    backend.key_press = AsyncMock()
    backend.drag = AsyncMock()
    backend.tap = AsyncMock()
    backend.set_files = AsyncMock()
    backend.get_cookies = AsyncMock(return_value=[{"name": "session", "value": "abc"}])
    backend.set_cookie = AsyncMock()
    backend.delete_cookie = AsyncMock()
    backend.clear_cookies = AsyncMock()
    backend.browser_version = AsyncMock(return_value="Chrome 119.0.6045.105")
    backend.__class__.__name__ = "CDPBackend"

    backend.set_headers = AsyncMock()
    backend.set_user_agent = AsyncMock()
    backend.block_requests = AsyncMock()
    backend.throttle_network = AsyncMock()
    backend.set_cache_disabled = AsyncMock()
    backend.capture_har = AsyncMock(return_value={"log": {"entries": [{"request": {}}]}})
    backend.intercept_requests = AsyncMock()
    backend.mock_response = AsyncMock()

    backend.cache_storage_list = AsyncMock(return_value=["cache1", "cache2"])
    backend.cache_storage_entries = AsyncMock(
        return_value=[{"url": "https://example.com/resource"}]
    )
    backend.cache_storage_delete = AsyncMock()
    backend.indexeddb_list = AsyncMock(return_value=[{"name": "db1", "stores": ["store1"]}])
    backend.indexeddb_get_data = AsyncMock(return_value={"key": "value"})
    backend.indexeddb_clear = AsyncMock()

    backend.emulate_device = AsyncMock()
    backend.set_viewport = AsyncMock()
    backend.set_geolocation = AsyncMock()
    backend.set_timezone = AsyncMock()
    backend.set_dark_mode = AsyncMock()
    backend.set_locale = AsyncMock()
    backend.set_cpu_throttle = AsyncMock()
    backend.set_touch_emulation = AsyncMock()
    backend.set_sensors = AsyncMock()

    backend.a11y_tree = AsyncMock(
        return_value={
            "role": "WebArea",
            "name": "Test Page",
            "children": [
                {"role": "heading", "name": "Hello", "children": []},
                {"role": "button", "name": "Submit", "children": []},
            ],
        }
    )
    backend.a11y_node = AsyncMock(return_value={"role": "button", "name": "Submit"})
    backend.a11y_ancestors = AsyncMock(return_value=[{"role": "WebArea", "name": "Test Page"}])

    backend.dialog_accept = AsyncMock()
    backend.dialog_dismiss = AsyncMock()
    backend.intercept_download = AsyncMock(return_value=b"file-content")
    backend.grant_permission = AsyncMock()
    backend.reset_permissions = AsyncMock()

    backend.perf_metrics = AsyncMock(
        return_value={"LCP": 1234, "FCP": 567, "CLS": 0.1, "TTFB": 234}
    )
    backend.perf_trace = AsyncMock(return_value={"traceEvents": []})
    backend.perf_profile = AsyncMock(return_value={"nodes": [], "startTime": 0, "endTime": 3000})
    backend.perf_heap_snapshot = AsyncMock(return_value={"snapshot": {}})
    backend.perf_coverage = AsyncMock(return_value=[{"url": "script.js", "ranges": []}])
    backend.perf_css_coverage = AsyncMock(return_value=[{"url": "style.css", "ranges": []}])

    backend.css_get_styles = AsyncMock(
        return_value={"inlineStyles": "color: red;", "matchedStyles": []}
    )
    backend.css_get_stylesheets = AsyncMock(
        return_value=[{"styleSheetId": "s1", "origin": "regular", "sourceURL": "style.css"}]
    )
    backend.css_get_rules = AsyncMock(return_value=[{"selectorText": "h1", "style": {}}])
    backend.css_get_computed = AsyncMock(return_value={"color": "rgb(0, 0, 0)", "display": "block"})

    backend.debug_set_breakpoint = AsyncMock(return_value="bp-1")
    backend.debug_set_breakpoint_function = AsyncMock(return_value="bp-2")
    backend.debug_remove_breakpoint = AsyncMock()
    backend.debug_step_over = AsyncMock()
    backend.debug_step_into = AsyncMock()
    backend.debug_step_out = AsyncMock()
    backend.debug_pause = AsyncMock()
    backend.debug_resume = AsyncMock()
    backend.debug_get_listeners = AsyncMock(
        return_value=[{"type": "click", "useCapture": False, "passive": False}]
    )

    backend.overlay_highlight = AsyncMock()
    backend.overlay_clear = AsyncMock()

    backend.capture_console = AsyncMock(
        return_value=[
            {"level": "error", "text": "Test error", "url": "https://example.com", "line": 42},
            {"level": "info", "text": "Hello", "url": "", "line": 0},
        ]
    )
    backend.capture_logs = AsyncMock(
        return_value=[{"level": "info", "message": "Browser log entry"}]
    )

    backend.get_security_state = AsyncMock(return_value={"state": "secure", "explanations": []})
    backend.ignore_cert_errors = AsyncMock()

    backend.get_window_bounds = AsyncMock(
        return_value={"width": 1280, "height": 800, "x": 0, "y": 0}
    )
    backend.set_window_bounds = AsyncMock()

    backend.raw = AsyncMock(return_value={"result": {}})
    backend.suggest_locator = AsyncMock(return_value=["#submit-btn", "button[type=submit]"])

    backend.sw_list = AsyncMock(return_value=[])
    backend.sw_unregister = AsyncMock()
    backend.sw_update = AsyncMock()

    backend.animation_list = AsyncMock(return_value=[])
    backend.animation_pause = AsyncMock()
    backend.animation_play = AsyncMock()
    backend.animation_seek = AsyncMock()

    backend.webauthn_add_virtual_authenticator = AsyncMock(return_value="auth-1")
    backend.webauthn_remove_authenticator = AsyncMock()
    backend.webauthn_add_credential = AsyncMock()
    backend.webauthn_get_credentials = AsyncMock(return_value=[])

    backend.webaudio_get_contexts = AsyncMock(return_value=[])
    backend.webaudio_get_context = AsyncMock(return_value={})

    backend.media_get_players = AsyncMock(return_value=[])
    backend.media_get_messages = AsyncMock(return_value=[])

    backend.cast_list = AsyncMock(return_value=[])
    backend.cast_start_tab = AsyncMock()
    backend.cast_stop = AsyncMock()

    backend.bluetooth_emulate = AsyncMock()
    backend.bluetooth_stop = AsyncMock()

    backend.find_by_text = AsyncMock(return_value="button:has-text('Submit')")
    backend.nl_click = AsyncMock()
    backend.nl_fill = AsyncMock()
    backend.list_contexts = AsyncMock(return_value=["ctx-1", "ctx-2"])
    backend.modify_response = AsyncMock()

    return backend


@pytest.fixture
def session_manager_with_mock(mock_backend: AsyncMock) -> SessionManager:
    """Return a SessionManager with a pre-registered mock session."""
    import time
    import uuid

    from wavexis_mcp.session import BrowserSession

    mgr = SessionManager()
    sid = str(uuid.uuid4())
    mgr._sessions[sid] = BrowserSession(
        session_id=sid,
        backend=mock_backend,
        backend_name="cdp",
        created_at=time.time(),
        last_used=time.time(),
    )
    return mgr


@pytest.fixture
def mock_session_id(session_manager_with_mock: SessionManager) -> str:
    """Return the session ID for the mock session."""
    return next(iter(session_manager_with_mock._sessions.keys()))
