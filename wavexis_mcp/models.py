"""Pydantic v2 input models for all WaveXisMCP tools.

This module defines every ``BaseModel`` used as the typed input for
the MCP tools exposed by WaveXisMCP.  Models are grouped by
capability tier (Session, Navigation, Capture, JavaScript, DOM,
Input, Cookies, Tabs, Utility, Network, Storage, Emulation, A11y,
Interactions, and DevTools) and separated by section comments.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

# ── Session management ──────────────────────────────────────────


class SessionOpenInput(BaseModel):
    """Input for opening a new browser session."""
    backend: str = Field(default="cdp", description="Backend: 'cdp', 'bidi', or 'auto'")
    headless: bool = Field(default=True)
    width: int = Field(default=1280, ge=320, le=3840)
    height: int = Field(default=800, ge=240, le=2160)
    user_agent: str | None = Field(default=None)
    extra_headers: dict[str, str] = Field(default_factory=dict)
    proxy: str | None = Field(default=None)
    timeout: int = Field(default=30000, ge=1000, le=300000)


class SessionCloseInput(BaseModel):
    """Input for closing an existing browser session."""
    session_id: str = Field(..., description="Session ID from wavexis_session_open")


class SessionInfoInput(BaseModel):
    """Input for querying session metadata."""
    session_id: str = Field(...)


# ── Navigation ──────────────────────────────────────────────────


class NavigateInput(BaseModel):
    """Input for navigating to a URL."""
    url: str = Field(..., description="URL to navigate to")
    session_id: str | None = Field(default=None)
    wait_strategy: str = Field(default="load")
    wait_selector: str | None = Field(default=None)
    wait_url_pattern: str | None = Field(default=None)
    wait_timeout: int = Field(default=30000, ge=1000, le=300000)
    headless: bool = Field(default=True)
    backend: str = Field(default="cdp")


class SimpleNavInput(BaseModel):
    """Input for session-only navigation actions (back, forward, stop)."""
    session_id: str = Field(..., description="Active session ID")


class ReloadInput(BaseModel):
    """Input for reloading the current page."""
    session_id: str = Field(...)
    ignore_cache: bool = Field(default=False, description="Bypass cache on reload")


class WaitInput(BaseModel):
    """Input for waiting on a page condition."""
    session_id: str = Field(...)
    strategy: str = Field(
        default="load", description="load, domcontentloaded, networkidle, selector, url"
    )
    selector: str | None = Field(default=None)
    url_pattern: str | None = Field(default=None)
    timeout: int = Field(default=30000, ge=1000, le=300000)


# ── Capture ─────────────────────────────────────────────────────


class ScreenshotInput(BaseModel):
    """Input for taking a screenshot."""
    url: str | None = Field(
        default=None, description="URL to navigate to (required without session_id)"
    )
    session_id: str | None = Field(default=None)
    full_page: bool = Field(default=True, description="Capture full scrollable page")
    format: str = Field(default="png", description="Image format: 'png' or 'jpeg'")
    quality: int = Field(default=80, ge=1, le=100, description="JPEG quality (ignored for PNG)")
    selector: str | None = Field(
        default=None, description="CSS selector — screenshot only this element"
    )
    js: str | None = Field(default=None, description="JavaScript to execute before screenshot")
    device: str | None = Field(default=None, description="Device preset name (e.g. 'iphone-15')")
    output_path: str | None = Field(
        default=None, description="Save to file instead of returning base64"
    )
    wait_strategy: str = Field(default="load")
    wait_selector: str | None = Field(default=None)
    wait_timeout: int = Field(default=30000, ge=1000, le=300000)
    headless: bool = Field(default=True)
    width: int = Field(default=1280, ge=320, le=3840)
    height: int = Field(default=800, ge=240, le=2160)
    backend: str = Field(default="cdp")


class PDFInput(BaseModel):
    """Input for generating a PDF."""
    url: str | None = Field(default=None)
    session_id: str | None = Field(default=None)
    paper: str = Field(default="letter", description="Paper size: a4, letter, legal, a3, a5")
    landscape: bool = Field(default=False)
    margin: str = Field(default="0.4in")
    no_header_footer: bool = Field(default=False)
    media: str = Field(default="print", description="CSS media: 'print' or 'screen'")
    js: str | None = Field(default=None)
    output_path: str | None = Field(default=None)
    wait_timeout: int = Field(default=30000)
    headless: bool = Field(default=True)
    backend: str = Field(default="cdp")


class ScrapeInput(BaseModel):
    """Input for scraping multiple URLs."""
    urls: list[str] = Field(..., min_length=1, max_length=50, description="URLs to scrape")
    session_id: str | None = Field(default=None)
    expression: str = Field(
        default="document.title", description="JS expression to evaluate on each page"
    )
    output_format: str = Field(default="json", description="Output format: 'json' or 'csv'")
    selector: str | None = Field(default=None, description="CSS selector to wait for")
    wait_timeout: int = Field(default=30000)
    headless: bool = Field(default=True)
    backend: str = Field(default="cdp")
    limit: int = Field(default=50, ge=1, le=500, description="Max results to return")
    offset: int = Field(default=0, ge=0, description="Skip first N results for pagination")


class ScreencastInput(BaseModel):
    """Input for capturing a frame sequence."""
    url: str | None = Field(default=None)
    session_id: str | None = Field(default=None)
    format: str = Field(default="png")
    quality: int = Field(default=80, ge=1, le=100)
    max_width: int = Field(default=1280, ge=320, le=3840)
    max_height: int = Field(default=800, ge=240, le=2160)
    duration: float = Field(
        default=5.0, ge=0.5, le=60.0, description="Capture duration in seconds"
    )
    interval: float = Field(
        default=1.0, ge=0.1, le=10.0, description="Seconds between frames"
    )
    output_dir: str | None = Field(default=None, description="Save frames to directory")
    wait_timeout: int = Field(default=30000)
    headless: bool = Field(default=True)
    backend: str = Field(default="cdp")


# ── JavaScript ──────────────────────────────────────────────────


class EvalInput(BaseModel):
    """Input for evaluating a JavaScript expression."""
    expression: str = Field(..., description="JavaScript expression to evaluate")
    session_id: str | None = Field(default=None)
    url: str | None = Field(
        default=None, description="URL to navigate to first (required without session)"
    )
    await_promise: bool = Field(default=False, description="Await a returned Promise")
    wait_timeout: int = Field(default=30000)
    headless: bool = Field(default=True)
    backend: str = Field(default="cdp")


# ── DOM ─────────────────────────────────────────────────────────


class DOMGetInput(BaseModel):
    """Input for getting HTML of an element."""
    selector: str = Field(..., description="CSS selector for the target element")
    session_id: str | None = Field(default=None)
    url: str | None = Field(default=None)
    outer: bool = Field(default=True, description="Return outerHTML (True) or innerHTML (False)")
    wait_timeout: int = Field(default=30000)
    headless: bool = Field(default=True)
    backend: str = Field(default="cdp")


class DOMQueryInput(BaseModel):
    """Input for querying elements by CSS selector."""
    selector: str = Field(...)
    session_id: str | None = Field(default=None)
    url: str | None = Field(default=None)
    all: bool = Field(default=False, description="Return all matches (True) or first only (False)")
    limit: int = Field(default=50, ge=1, le=500, description="Max elements to return when all=True")
    offset: int = Field(default=0, ge=0, description="Skip first N elements for pagination")
    wait_timeout: int = Field(default=30000)
    headless: bool = Field(default=True)
    backend: str = Field(default="cdp")


class DOMSetAttrInput(BaseModel):
    """Input for setting an attribute on an element."""
    selector: str = Field(...)
    name: str = Field(..., description="Attribute name")
    value: str = Field(..., description="Attribute value")
    session_id: str = Field(...)


class DOMGetAttrInput(BaseModel):
    """Input for getting an attribute value from an element."""
    selector: str = Field(...)
    name: str = Field(...)
    session_id: str = Field(...)


class DOMRemoveAttrInput(BaseModel):
    """Input for removing an attribute from an element."""
    selector: str = Field(...)
    name: str = Field(...)
    session_id: str = Field(...)


class DOMRemoveInput(BaseModel):
    """Input for removing an element from the DOM."""
    selector: str = Field(...)
    session_id: str = Field(...)


class DOMFocusInput(BaseModel):
    """Input for focusing an element."""
    selector: str = Field(...)
    session_id: str = Field(...)


class DOMScrollInput(BaseModel):
    """Input for scrolling to an element or by offset."""
    session_id: str = Field(...)
    selector: str | None = Field(default=None, description="CSS selector to scroll to")
    x: int = Field(default=0, description="Horizontal scroll offset")
    y: int = Field(default=0, description="Vertical scroll offset")


class DOMSnapshotInput(BaseModel):
    """Input for capturing a full DOM snapshot."""
    session_id: str = Field(...)


# ── Input ───────────────────────────────────────────────────────


class ClickInput(BaseModel):
    """Input for clicking an element."""
    selector: str = Field(..., description="CSS selector for element to click")
    session_id: str | None = Field(default=None)
    url: str | None = Field(default=None)
    button: str = Field(default="left", description="left, right, middle")
    click_count: int = Field(default=1, ge=1, le=10)
    wait_timeout: int = Field(default=30000)
    headless: bool = Field(default=True)
    backend: str = Field(default="cdp")


class TypeInput(BaseModel):
    """Input for typing text into an element."""
    selector: str = Field(...)
    text: str = Field(..., description="Text to type character by character")
    session_id: str | None = Field(default=None)
    url: str | None = Field(default=None)
    delay: int = Field(default=0, ge=0, le=1000, description="Delay between keystrokes in ms")
    wait_timeout: int = Field(default=30000)
    headless: bool = Field(default=True)
    backend: str = Field(default="cdp")


class FillInput(BaseModel):
    """Input for filling an input element."""
    selector: str = Field(...)
    value: str = Field(..., description="Value to fill (replaces existing content)")
    session_id: str | None = Field(default=None)
    url: str | None = Field(default=None)
    wait_timeout: int = Field(default=30000)
    headless: bool = Field(default=True)
    backend: str = Field(default="cdp")


class FormField(BaseModel):
    """A single form field descriptor for ``FillFormInput``."""
    selector: str = Field(..., description="CSS selector for the input element")
    value: str = Field(..., description="Value to fill")


class FillFormInput(BaseModel):
    """Input for filling multiple form fields in one call."""
    fields: list[FormField] = Field(..., min_length=1, description="Form fields to fill")
    session_id: str | None = Field(default=None)
    url: str | None = Field(default=None)
    wait_timeout: int = Field(default=30000)
    headless: bool = Field(default=True)
    backend: str = Field(default="cdp")


class SelectOptionInput(BaseModel):
    """Input for selecting an option in a ``<select>`` element."""
    selector: str = Field(..., description="CSS selector for <select> element")
    value: str = Field(..., description="Option value to select")
    session_id: str | None = Field(default=None)
    url: str | None = Field(default=None)
    wait_timeout: int = Field(default=30000)
    headless: bool = Field(default=True)
    backend: str = Field(default="cdp")


class HoverInput(BaseModel):
    """Input for hovering over an element."""
    selector: str = Field(...)
    session_id: str | None = Field(default=None)
    url: str | None = Field(default=None)
    wait_timeout: int = Field(default=30000)
    headless: bool = Field(default=True)
    backend: str = Field(default="cdp")


class KeyPressInput(BaseModel):
    """Input for pressing a keyboard key."""
    key: str = Field(..., description="Key to press (e.g. 'Enter', 'Tab', 'Escape', 'a')")
    session_id: str = Field(...)


class DragInput(BaseModel):
    """Input for dragging an element from source to target."""
    source: str = Field(..., description="CSS selector for drag source")
    target: str = Field(..., description="CSS selector for drop target")
    session_id: str | None = Field(default=None)
    url: str | None = Field(default=None)
    wait_timeout: int = Field(default=30000)
    headless: bool = Field(default=True)
    backend: str = Field(default="cdp")


class TapInput(BaseModel):
    """Input for tapping an element (touch emulation)."""
    selector: str = Field(..., description="CSS selector for element to tap")
    session_id: str | None = Field(default=None)
    url: str | None = Field(default=None)
    wait_timeout: int = Field(default=30000)
    headless: bool = Field(default=True)
    backend: str = Field(default="cdp")


class SetFilesInput(BaseModel):
    """Input for uploading files to a file input element."""
    selector: str = Field(..., description="CSS selector for <input type='file'> element")
    files: list[str] = Field(..., min_length=1, description="Absolute file paths to upload")
    session_id: str | None = Field(default=None)
    url: str | None = Field(default=None)
    wait_timeout: int = Field(default=30000)
    headless: bool = Field(default=True)
    backend: str = Field(default="cdp")


class CheckInput(BaseModel):
    """Input for checking/unchecking a checkbox or radio."""
    selector: str = Field(..., description="CSS selector for checkbox/radio")
    session_id: str = Field(...)


# ── Cookies ─────────────────────────────────────────────────────


class CookiesGetInput(BaseModel):
    """Input for getting cookies."""
    session_id: str | None = Field(default=None)
    url: str | None = Field(default=None)
    wait_timeout: int = Field(default=30000)
    headless: bool = Field(default=True)
    backend: str = Field(default="cdp")


class CookiesSetInput(BaseModel):
    """Input for setting a cookie."""
    name: str = Field(...)
    value: str = Field(...)
    domain: str = Field(...)
    path: str = Field(default="/")
    secure: bool = Field(default=True)
    http_only: bool = Field(default=False)
    same_site: str = Field(default="Lax")
    session_id: str | None = Field(default=None)
    url: str | None = Field(default=None)
    wait_timeout: int = Field(default=30000)
    headless: bool = Field(default=True)
    backend: str = Field(default="cdp")


class CookiesDeleteInput(BaseModel):
    """Input for deleting cookies."""
    name: str = Field(...)
    domain: str = Field(...)
    session_id: str | None = Field(default=None)
    url: str | None = Field(default=None)
    wait_timeout: int = Field(default=30000)
    headless: bool = Field(default=True)
    backend: str = Field(default="cdp")


class CookiesClearInput(BaseModel):
    """Input for clearing all cookies."""
    session_id: str = Field(...)


# ── Tabs ────────────────────────────────────────────────────────


class ListTabsInput(BaseModel):
    """Input for listing browser tabs."""
    session_id: str = Field(...)


class NewTabInput(BaseModel):
    """Input for creating a new browser tab."""
    session_id: str = Field(...)
    url: str = Field(default="about:blank")


class CloseTabInput(BaseModel):
    """Input for closing a browser tab."""
    session_id: str = Field(...)
    tab_id: str = Field(...)


class ActivateTabInput(BaseModel):
    """Input for activating (focusing) a browser tab."""
    session_id: str = Field(...)
    tab_id: str = Field(...)


# ── Utility ─────────────────────────────────────────────────────


class BrowserVersionInput(BaseModel):
    """Input for getting the browser version."""
    session_id: str | None = Field(default=None)
    backend: str = Field(default="cdp")


# ── Network ─────────────────────────────────────────────────────


class SetHeadersInput(BaseModel):
    """Input for setting extra HTTP headers."""
    headers: dict[str, str] = Field(...)
    session_id: str = Field(...)


class SetUserAgentInput(BaseModel):
    """Input for setting a custom User-Agent string."""
    user_agent: str = Field(...)
    session_id: str = Field(...)


class BlockRequestsInput(BaseModel):
    """Input for blocking requests matching URL patterns."""
    patterns: list[str] = Field(
        ..., description="URL patterns to block (glob-style)"
    )
    session_id: str = Field(...)


class ThrottleNetworkInput(BaseModel):
    """Input for throttling network speed."""
    session_id: str = Field(...)
    preset: str | None = Field(
        default=None, description="Preset: none, 2g, 3g, 4g, offline"
    )
    latency_ms: int = Field(default=0, ge=0, le=10000)
    download_bps: int = Field(default=-1, ge=-1)
    upload_bps: int = Field(default=-1, ge=-1)
    offline: bool = Field(default=False)


class SetCacheDisabledInput(BaseModel):
    """Input for enabling or disabling the browser cache."""
    session_id: str = Field(...)
    disabled: bool = Field(default=True)


class CaptureHARInput(BaseModel):
    """Input for capturing HAR data for a page load."""
    url: str = Field(..., description="URL to navigate to for HAR capture")
    session_id: str | None = Field(default=None)
    wait_ms: int = Field(default=3000, ge=500, le=30000)
    filter: str | None = Field(default=None, description="URL filter pattern")
    timeout: int = Field(default=30000)
    headless: bool = Field(default=True)
    backend: str = Field(default="cdp")


class InterceptRequestsInput(BaseModel):
    """Input for registering a request interception pattern."""
    session_id: str = Field(...)
    pattern: dict[str, str] = Field(
        ..., description="Interception pattern (urlPattern, resourceType, etc.)"
    )


class MockResponseInput(BaseModel):
    """Input for registering a mock response for a URL pattern."""
    session_id: str = Field(...)
    url: str = Field(..., description="URL pattern to match")
    status: int = Field(default=200)
    content_type: str = Field(default="application/json")
    body: str = Field(default="")
    headers: dict[str, str] = Field(default_factory=dict)


class NetworkRequestsInput(BaseModel):
    """Input for listing network requests with pagination."""
    session_id: str = Field(...)
    filter: str | None = Field(default=None, description="URL filter pattern")
    resource_type: str | None = Field(
        default=None, description="Filter by type: document, stylesheet, image, etc."
    )
    limit: int = Field(default=100, ge=1, le=1000, description="Max requests to return")
    offset: int = Field(default=0, ge=0, description="Skip first N requests for pagination")


# ── Storage ─────────────────────────────────────────────────────


class LocalStorageGetInput(BaseModel):
    """Input for getting a localStorage value."""
    key: str = Field(...)
    session_id: str = Field(...)


class LocalStorageSetInput(BaseModel):
    """Input for setting a localStorage key/value pair."""
    key: str = Field(...)
    value: str = Field(...)
    session_id: str = Field(...)


class LocalStorageDeleteInput(BaseModel):
    """Input for deleting a localStorage key."""
    key: str = Field(...)
    session_id: str = Field(...)


class LocalStorageClearInput(BaseModel):
    """Input for clearing all localStorage entries."""
    session_id: str = Field(...)


class LocalStorageListInput(BaseModel):
    """Input for listing all localStorage entries."""
    session_id: str = Field(...)


class SessionStorageGetInput(BaseModel):
    """Input for getting a sessionStorage value."""
    key: str = Field(...)
    session_id: str = Field(...)


class SessionStorageSetInput(BaseModel):
    """Input for setting a sessionStorage key/value pair."""
    key: str = Field(...)
    value: str = Field(...)
    session_id: str = Field(...)


class SessionStorageDeleteInput(BaseModel):
    """Input for deleting a sessionStorage key."""
    key: str = Field(...)
    session_id: str = Field(...)


class SessionStorageClearInput(BaseModel):
    """Input for clearing all sessionStorage entries."""
    session_id: str = Field(...)


class SessionStorageListInput(BaseModel):
    """Input for listing all sessionStorage entries."""
    session_id: str = Field(...)


class CacheStorageListInput(BaseModel):
    """Input for listing Cache Storage cache names."""
    session_id: str = Field(...)


class CacheStorageEntriesInput(BaseModel):
    """Input for listing entries in a Cache Storage cache."""
    cache_name: str = Field(...)
    session_id: str = Field(...)


class CacheStorageDeleteInput(BaseModel):
    """Input for deleting a Cache Storage cache."""
    cache_name: str = Field(...)
    session_id: str = Field(...)


class IndexedDBListInput(BaseModel):
    """Input for listing IndexedDB databases."""
    session_id: str = Field(...)


class IndexedDBGetDataInput(BaseModel):
    """Input for getting data from an IndexedDB object store."""
    database: str = Field(...)
    store: str = Field(..., description="Object store name")
    key: str = Field(default="", description="Specific key (empty = all entries)")
    session_id: str = Field(...)


class IndexedDBClearInput(BaseModel):
    """Input for clearing an IndexedDB object store."""
    database: str = Field(...)
    store: str = Field(...)
    session_id: str = Field(...)


class StorageStateSaveInput(BaseModel):
    """Input for saving browser state to a JSON file."""
    session_id: str = Field(...)
    output_path: str = Field(..., description="File path to save state JSON")


class StorageStateRestoreInput(BaseModel):
    """Input for restoring browser state from a JSON file."""
    session_id: str = Field(...)
    input_path: str = Field(..., description="Path to saved state JSON file")


# ── Emulation ───────────────────────────────────────────────────


class EmulateDeviceInput(BaseModel):
    """Input for emulating a specific device."""
    session_id: str = Field(...)
    device: str = Field(
        ...,
        description="Device preset: iphone-15, iphone-se, pixel-8, ipad-pro, "
        "galaxy-s23, desktop-1080p, desktop-1440p",
    )


class SetViewportInput(BaseModel):
    """Input for setting a custom viewport size."""
    session_id: str = Field(...)
    width: int = Field(..., ge=320, le=3840)
    height: int = Field(..., ge=240, le=2160)
    device_scale_factor: float = Field(default=1.0, ge=0.1, le=10.0)


class SetGeolocationInput(BaseModel):
    """Input for overriding the browser geolocation."""
    session_id: str = Field(...)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    accuracy: float = Field(default=100.0, ge=0)


class SetTimezoneInput(BaseModel):
    """Input for overriding the browser timezone."""
    session_id: str = Field(...)
    timezone: str = Field(..., description="IANA timezone ID (e.g. 'America/New_York')")


class SetDarkModeInput(BaseModel):
    """Input for enabling or disabling dark mode emulation."""
    session_id: str = Field(...)
    enabled: bool = Field(default=True)


class SetLocaleInput(BaseModel):
    """Input for overriding the browser locale."""
    session_id: str = Field(...)
    locale: str = Field(..., description="Locale code (e.g. 'en-US', 'fr-FR', 'ja-JP')")


class SetCPUThrottleInput(BaseModel):
    """Input for enabling CPU throttling."""
    session_id: str = Field(...)
    rate: float = Field(
        ..., ge=1.0, le=20.0, description="CPU throttle multiplier (e.g. 4 = 4x slower)"
    )


class SetTouchEmulationInput(BaseModel):
    """Input for enabling or disabling touch emulation."""
    session_id: str = Field(...)
    enabled: bool = Field(default=True)


class SetSensorsInput(BaseModel):
    """Input for overriding sensor values."""
    session_id: str = Field(...)
    sensor_type: str = Field(
        ..., description="Sensor type: 'orientation', 'motion', 'light', 'proximity'"
    )
    values: dict[str, float] = Field(
        ..., description="Sensor values (e.g. {'alpha': 0, 'beta': 90, 'gamma': 0})"
    )


# ── A11y ────────────────────────────────────────────────────────


class A11ySnapshotInput(BaseModel):
    """Input for capturing the full accessibility tree."""
    session_id: str | None = Field(default=None)
    url: str | None = Field(
        default=None, description="URL to navigate to first (required without session)"
    )
    wait_timeout: int = Field(default=30000)
    headless: bool = Field(default=True)
    backend: str = Field(default="cdp")


class A11yNodeInput(BaseModel):
    """Input for getting a specific accessibility node."""
    node_id: str = Field(..., description="Node ID from a11y_snapshot")
    session_id: str = Field(...)


class A11yAncestorsInput(BaseModel):
    """Input for getting the ancestor chain of a node."""
    node_id: str = Field(...)
    session_id: str = Field(...)


# ── Interactions ────────────────────────────────────────────────


class DialogAcceptInput(BaseModel):
    """Input for accepting a JavaScript dialog."""
    session_id: str = Field(...)
    prompt_text: str | None = Field(default=None, description="Text for prompt dialogs")


class DialogDismissInput(BaseModel):
    """Input for dismissing a JavaScript dialog."""
    session_id: str = Field(...)


class InterceptDownloadInput(BaseModel):
    """Input for intercepting a download."""
    session_id: str = Field(...)
    pattern: str = Field(default=".*", description="URL pattern to match")
    output_path: str | None = Field(
        default=None, description="Save to file instead of returning base64"
    )


class GrantPermissionInput(BaseModel):
    """Input for granting a browser permission."""
    session_id: str = Field(...)
    permission: str = Field(
        ...,
        description="Permission name: geolocation, notifications, camera, microphone, etc.",
    )


class ResetPermissionsInput(BaseModel):
    """Input for resetting all granted permissions."""
    session_id: str = Field(...)


# ── DevTools — Performance ──────────────────────────────────────


class PerfMetricsInput(BaseModel):
    """Input for getting performance metrics."""
    session_id: str = Field(...)


class PerfTraceInput(BaseModel):
    """Input for capturing a performance trace."""
    session_id: str = Field(...)
    duration_ms: int = Field(default=3000, ge=500, le=30000)
    output_path: str | None = Field(default=None)


class PerfProfileInput(BaseModel):
    """Input for capturing a CPU profile."""
    session_id: str = Field(...)
    duration_ms: int = Field(default=3000, ge=500, le=30000)
    output_path: str | None = Field(default=None)


class PerfHeapSnapshotInput(BaseModel):
    """Input for capturing a heap snapshot."""
    session_id: str = Field(...)
    output_path: str | None = Field(default=None)


class PerfCoverageInput(BaseModel):
    """Input for getting JavaScript code coverage."""
    session_id: str = Field(...)


class PerfCSSCoverageInput(BaseModel):
    """Input for getting CSS code coverage."""
    session_id: str = Field(...)


# ── DevTools — CSS ──────────────────────────────────────────────


class CSSGetStylesInput(BaseModel):
    """Input for getting inline and matched CSS styles."""
    selector: str = Field(...)
    session_id: str = Field(...)


class CSSGetStylesheetsInput(BaseModel):
    """Input for listing all stylesheets."""
    session_id: str = Field(...)


class CSSGetRulesInput(BaseModel):
    """Input for getting CSS rules from a stylesheet."""
    stylesheet_id: str = Field(...)
    session_id: str = Field(...)


class CSSGetComputedInput(BaseModel):
    """Input for getting computed styles for an element."""
    selector: str = Field(...)
    session_id: str = Field(...)


# ── DevTools — Debugging ────────────────────────────────────────


class DebugSetBreakpointInput(BaseModel):
    """Input for setting a breakpoint by URL and line."""
    session_id: str = Field(...)
    url: str = Field(..., description="URL of the script")
    line: int = Field(..., ge=0, description="Line number (0-based)")
    condition: str | None = Field(default=None, description="Optional condition expression")


class DebugSetBreakpointFunctionInput(BaseModel):
    """Input for setting a breakpoint by function name."""
    session_id: str = Field(...)
    function_name: str = Field(...)


class DebugRemoveBreakpointInput(BaseModel):
    """Input for removing a breakpoint by ID."""
    session_id: str = Field(...)
    breakpoint_id: str = Field(...)


class DebugStepInput(BaseModel):
    """Input for debugger step actions (over, into, out)."""
    session_id: str = Field(...)


class DebugPauseInput(BaseModel):
    """Input for pausing or resuming script execution."""
    session_id: str = Field(...)


class DebugGetListenersInput(BaseModel):
    """Input for getting event listeners on an element."""
    selector: str = Field(...)
    session_id: str = Field(...)


# ── DevTools — Overlay ──────────────────────────────────────────


class OverlayHighlightInput(BaseModel):
    """Input for highlighting an element with a colored overlay."""
    selector: str = Field(...)
    color: str = Field(default="rgba(255,0,0,0.5)", description="RGBA color string")
    session_id: str = Field(...)


class OverlayClearInput(BaseModel):
    """Input for clearing all overlay highlights."""
    session_id: str = Field(...)


# ── DevTools — Console & Logs ───────────────────────────────────


class ConsoleMessagesInput(BaseModel):
    """Input for getting console messages with pagination."""
    session_id: str = Field(...)
    level: str = Field(
        default="info", description="Minimum level: error, warning, info, debug"
    )
    all: bool = Field(
        default=False,
        description="Return all messages since session start, not just last navigation",
    )
    limit: int = Field(default=100, ge=1, le=1000, description="Max messages to return")
    offset: int = Field(default=0, ge=0, description="Skip first N messages for pagination")


class BrowserLogsInput(BaseModel):
    """Input for getting browser-level log entries."""
    session_id: str = Field(...)


# ── DevTools — Security ─────────────────────────────────────────


class GetSecurityStateInput(BaseModel):
    """Input for getting the page security state."""
    session_id: str = Field(...)


class IgnoreCertErrorsInput(BaseModel):
    """Input for enabling or disabling certificate error ignoring."""
    session_id: str = Field(...)
    ignore: bool = Field(default=True)


# ── DevTools — Window ───────────────────────────────────────────


class GetWindowBoundsInput(BaseModel):
    """Input for getting the browser window bounds."""
    session_id: str = Field(...)


class SetWindowBoundsInput(BaseModel):
    """Input for setting the browser window bounds."""
    session_id: str = Field(...)
    width: int = Field(..., ge=320, le=3840)
    height: int = Field(..., ge=240, le=2160)
    x: int = Field(default=0)
    y: int = Field(default=0)


# ── Vision ───────────────────────────────────────────────────────


class MouseMoveInput(BaseModel):
    """Input for moving the mouse to an element by CSS selector."""
    session_id: str = Field(...)
    selector: str = Field(..., description="CSS selector for the target element")


class MouseMoveXYInput(BaseModel):
    """Input for moving the mouse to absolute pixel coordinates."""
    session_id: str = Field(...)
    x: int = Field(..., description="X coordinate in CSS pixels")
    y: int = Field(..., description="Y coordinate in CSS pixels")


class MouseDownInput(BaseModel):
    """Input for pressing a mouse button at coordinates."""
    session_id: str = Field(...)
    button: str = Field(default="left")
    x: int = Field(default=0)
    y: int = Field(default=0)


class MouseUpInput(BaseModel):
    """Input for releasing a mouse button at coordinates."""
    session_id: str = Field(...)
    button: str = Field(default="left")
    x: int = Field(default=0)
    y: int = Field(default=0)


class MouseClickXYInput(BaseModel):
    """Input for clicking at absolute pixel coordinates."""
    session_id: str = Field(...)
    x: int = Field(...)
    y: int = Field(...)
    button: str = Field(default="left")
    click_count: int = Field(default=1, ge=1, le=10)


class MouseDoubleClickXYInput(BaseModel):
    """Input for double-clicking at absolute pixel coordinates."""
    session_id: str = Field(...)
    x: int = Field(...)
    y: int = Field(...)
    button: str = Field(default="left")


# ── Video ────────────────────────────────────────────────────────


class VideoRecordInput(BaseModel):
    """Input for starting video recording."""
    session_id: str = Field(...)
    output_path: str | None = Field(default=None, description="Output file path")
    width: int = Field(default=1280)
    height: int = Field(default=800)


class VideoStopInput(BaseModel):
    """Input for stopping video recording."""
    session_id: str = Field(...)
    output_path: str | None = Field(default=None, description="Output file path")


class VideoAddChapterInput(BaseModel):
    """Input for adding a chapter marker to a recording."""
    session_id: str = Field(...)
    recording_id: str = Field(..., description="Recording ID from video_record")
    title: str = Field(..., description="Chapter title")
    timestamp_ms: int | None = Field(default=None, description="Timestamp in ms")


class VideoActionOverlayInput(BaseModel):
    """Input for toggling action overlay on video."""
    session_id: str = Field(...)
    show: bool = Field(default=True)


# ── Testing ──────────────────────────────────────────────────────


class AssertVisibleInput(BaseModel):
    """Input for asserting element visibility."""
    session_id: str = Field(...)
    selector: str = Field(..., description="CSS selector for the element")
    timeout: int = Field(default=5000, ge=100, le=30000)


class AssertTextVisibleInput(BaseModel):
    """Input for asserting text visibility on the page."""
    session_id: str = Field(...)
    text: str = Field(..., description="Text to search for")
    timeout: int = Field(default=5000, ge=100, le=30000)


class AssertURLInput(BaseModel):
    """Input for asserting the current URL matches a pattern."""
    session_id: str = Field(...)
    url_pattern: str = Field(..., description="URL substring or pattern to match")


class GenerateLocatorInput(BaseModel):
    """Input for generating a robust CSS selector."""
    session_id: str = Field(...)
    selector: str = Field(..., description="Approximate CSS selector")
    description: str | None = Field(default=None, description="Natural-language description")


# ── Workflows ────────────────────────────────────────────────────


class MultiActionInput(BaseModel):
    """Input for executing multiple actions from a YAML config."""
    config: str = Field(..., description="YAML config string (not file path)")
    session_id: str | None = Field(default=None)
    backend: str = Field(default="cdp")
    headless: bool = Field(default=True)
    continue_on_error: bool = Field(default=False, description="Continue on action errors")


class RawCDPInput(BaseModel):
    """Input for sending a raw CDP command."""
    session_id: str = Field(...)
    method: str = Field(..., description="CDP method (e.g. 'Page.reload')")
    params: dict[str, Any] | None = Field(default=None)


class RawBiDiInput(BaseModel):
    """Input for sending a raw BiDi command."""
    session_id: str = Field(...)
    method: str = Field(..., description="BiDi command (e.g. 'browsingContext.navigate')")
    params: dict[str, Any] | None = Field(default=None)


class BrowserContextCreateInput(BaseModel):
    """Input for creating an isolated browser context."""
    session_id: str = Field(...)


class BrowserContextCloseInput(BaseModel):
    """Input for closing a browser context."""
    session_id: str = Field(...)
    context_id: str = Field(...)


# ── Data ─────────────────────────────────────────────────────────


class RecordInput(BaseModel):
    """Input for recording browser interactions."""
    url: str = Field(..., description="URL to navigate to for recording")
    duration: int = Field(default=60, ge=5, le=300, description="Recording duration in seconds")
    headless: bool = Field(default=False, description="Must be False for user interaction")
    backend: str = Field(default="cdp")


class LighthouseInput(BaseModel):
    """Input for running a Lighthouse-style audit."""
    url: str = Field(..., description="URL to audit")
    categories: list[str] = Field(
        default_factory=list,
        description=(
            "Categories: 'performance', 'accessibility', "
            "'seo', 'best-practices'. Empty = all."
        ),
    )
    session_id: str | None = Field(default=None)
    wait_timeout: int = Field(default=30000)
    headless: bool = Field(default=True)
    backend: str = Field(default="cdp")


class ExtractInput(BaseModel):
    """Input for structured data extraction via CSS selector schema."""
    url: str = Field(..., description="URL to navigate to")
    schema: dict[str, str] = Field(  # type: ignore[assignment]
        ..., description='Mapping of field names to CSS selectors, e.g. {"title": "h1"}'
    )
    selector: str | None = Field(
        default=None, description="Optional scoping selector for repeating elements"
    )
    session_id: str | None = Field(default=None)
    wait_timeout: int = Field(default=30000)
    headless: bool = Field(default=True)
    backend: str = Field(default="cdp")


class WebsocketInterceptInput(BaseModel):
    """Input for capturing WebSocket frames."""
    url: str = Field(..., description="URL to navigate to")
    url_pattern: str = Field(
        default="",
        description="Regex pattern to filter WS URLs (empty = all)",
    )
    duration_ms: int = Field(default=5000, ge=500, le=60000, description="Capture duration in ms")
    mock_responses: dict[str, str] = Field(
        default_factory=dict, description="Map request payloads to mock response payloads"
    )
    session_id: str | None = Field(default=None)
    wait_timeout: int = Field(default=30000)
    headless: bool = Field(default=True)
    backend: str = Field(default="cdp")


class CrawlInput(BaseModel):
    """Input for crawling a website."""
    start_url: str = Field(..., description="Starting URL for the crawl")
    max_depth: int = Field(default=2, ge=1, le=10, description="Maximum crawl depth")
    max_pages: int = Field(default=50, ge=1, le=500, description="Maximum pages to visit")
    same_origin: bool = Field(default=True, description="Only crawl same-origin links")
    url_pattern: str = Field(default="", description="Regex pattern to filter URLs (empty = all)")
    session_id: str | None = Field(default=None)
    wait_timeout: int = Field(default=30000)
    headless: bool = Field(default=True)
    backend: str = Field(default="cdp")


class VisualDiffInput(BaseModel):
    """Input for visual regression comparison."""
    url: str = Field(..., description="URL to navigate to")
    baseline_path: str = Field(..., description="Path to baseline screenshot file")
    selector: str | None = Field(
        default=None,
        description="CSS selector — compare only this element",
    )
    threshold: float = Field(default=0.1, ge=0.0, le=1.0, description="Pixel difference threshold")
    output_path: str | None = Field(default=None, description="Save diff image to this path")
    session_id: str | None = Field(default=None)
    wait_timeout: int = Field(default=30000)
    headless: bool = Field(default=True)
    backend: str = Field(default="cdp")


# ── Experimental ─────────────────────────────────────────────────


class ServiceWorkerListInput(BaseModel):
    """Input for listing service workers."""
    session_id: str = Field(...)


class ServiceWorkerUnregisterInput(BaseModel):
    """Input for unregistering a service worker."""
    session_id: str = Field(...)
    registration_id: str = Field(...)


class ServiceWorkerEmulateInput(BaseModel):
    """Input for emulating a service worker."""
    session_id: str = Field(...)
    script_url: str = Field(..., description="Script URL for the emulated service worker")


class AnimationPlayInput(BaseModel):
    """Input for playing/resuming an animation."""
    session_id: str = Field(...)
    animation_id: str = Field(...)


class AnimationPauseInput(BaseModel):
    """Input for pausing an animation."""
    session_id: str = Field(...)
    animation_id: str = Field(...)


class AnimationSetRateInput(BaseModel):
    """Input for setting animation playback rate."""
    session_id: str = Field(...)
    animation_id: str = Field(...)
    playback_rate: float = Field(default=1.0, ge=0.0, description="Playback rate multiplier")


class WebAuthnAddCredentialInput(BaseModel):
    """Input for adding a WebAuthn credential."""
    session_id: str = Field(...)
    authenticator_id: str = Field(...)
    credential: dict[str, Any] = Field(...)


class WebAuthnGetCredentialInput(BaseModel):
    """Input for getting WebAuthn credentials."""
    session_id: str = Field(...)
    authenticator_id: str = Field(...)


class WebAuthnRemoveCredentialInput(BaseModel):
    """Input for removing a WebAuthn authenticator."""
    session_id: str = Field(...)
    authenticator_id: str = Field(...)


class WebAudioCaptureInput(BaseModel):
    """Input for capturing WebAudio context data."""
    session_id: str = Field(...)
    context_id: str | None = Field(default=None, description="Specific context ID (empty = all)")


class WebAudioStopCaptureInput(BaseModel):
    """Input for stopping WebAudio capture."""
    session_id: str = Field(...)


class MediaPlayerPlayInput(BaseModel):
    """Input for playing a media player."""
    session_id: str = Field(...)
    player_id: str = Field(...)


class MediaPlayerPauseInput(BaseModel):
    """Input for pausing a media player."""
    session_id: str = Field(...)
    player_id: str = Field(...)


class MediaPlayerSeekInput(BaseModel):
    """Input for seeking a media player."""
    session_id: str = Field(...)
    player_id: str = Field(...)
    time_ms: int = Field(..., ge=0, description="Seek time in milliseconds")


class CastStartInput(BaseModel):
    """Input for starting tab casting."""
    session_id: str = Field(...)
    sink_name: str = Field(..., description="Cast sink name")


class CastStopInput(BaseModel):
    """Input for stopping casting."""
    session_id: str = Field(...)


class BluetoothAdapterStateInput(BaseModel):
    """Input for setting Bluetooth adapter state."""
    session_id: str = Field(...)
    state: str = Field(..., description="Adapter state: 'powered-on' or 'powered-off'")


class BluetoothDeviceConnectInput(BaseModel):
    """Input for connecting a Bluetooth device."""
    session_id: str = Field(...)
    name: str = Field(..., description="Device name")
    address: str = Field(default="00:00:00:00:00:01", description="Device MAC address")


class BluetoothDeviceDisconnectInput(BaseModel):
    """Input for disconnecting Bluetooth emulation."""
    session_id: str = Field(...)


class BluetoothDeviceListInput(BaseModel):
    """Input for listing Bluetooth devices."""
    session_id: str = Field(...)


class GetRequestBodyInput(BaseModel):
    """Input for getting a network request body (W3)."""
    session_id: str = Field(...)
    request_id: str = Field(..., description="Network request ID")


class GetResponseBodyInput(BaseModel):
    """Input for getting a network response body (W3)."""
    session_id: str = Field(...)
    request_id: str = Field(..., description="Network request ID")


class ModifyRequestInput(BaseModel):
    """Input for modifying requests in-flight (W6)."""
    session_id: str = Field(...)
    pattern: dict[str, Any] = Field(
        ..., description="Interception pattern (urlPattern, resourceType, requestStage)"
    )
    modifications: dict[str, Any] = Field(
        default_factory=dict,
        description="Modifications: headers, url, method, post_data",
    )


class ReplayHARInput(BaseModel):
    """Input for replaying HAR entries (W7)."""
    har_path: str = Field(..., description="Path to HAR file")
    url_filter: str = Field(default="", description="Optional URL filter pattern")
    session_id: str | None = Field(default=None)
    url: str = Field(default="", description="URL to navigate to before replay")
    headless: bool = Field(default=True)
    backend: str = Field(default="cdp")


class StartCombinedTraceInput(BaseModel):
    """Input for starting a combined trace (W8)."""
    session_id: str = Field(...)
    capture_screenshots: bool = Field(default=True)
    capture_network: bool = Field(default=True)
    capture_console: bool = Field(default=True)


class StopCombinedTraceInput(BaseModel):
    """Input for stopping a combined trace (W8)."""
    session_id: str = Field(...)
    trace_id: str = Field(..., description="Trace ID from start_combined_trace")


class AxeAuditInput(BaseModel):
    """Input for running axe-core accessibility audit (W9)."""
    session_id: str | None = Field(default=None)
    url: str = Field(default="", description="URL to navigate to before audit")
    headless: bool = Field(default=True)
    backend: str = Field(default="cdp")


class ActInput(BaseModel):
    """Input for natural language interaction (M1)."""
    instruction: str = Field(
        ..., description="Natural language instruction (e.g. 'click the login button')"
    )
    session_id: str = Field(...)
    max_retries: int = Field(default=3, ge=1, le=10)


# ── Annotated screenshot ────────────────────────────────────────


class AnnotatedScreenshotInput(BaseModel):
    """Input for taking a screenshot with numbered labels on elements."""
    session_id: str = Field(...)
    selectors: list[str] = Field(
        ..., min_length=1, description="CSS selectors to annotate with labels"
    )
    format: str = Field(default="png", description="Image format: 'png' or 'jpeg'")
    output_path: str | None = Field(default=None)


# ── iframe ──────────────────────────────────────────────────────


class IframeEvalInput(BaseModel):
    """Input for evaluating JS inside an iframe."""
    session_id: str = Field(...)
    iframe_selector: str = Field(..., description="CSS selector for the <iframe> element")
    expression: str = Field(..., description="JavaScript expression to evaluate")
    await_promise: bool = Field(default=False)


class IframeClickInput(BaseModel):
    """Input for clicking an element inside an iframe."""
    session_id: str = Field(...)
    iframe_selector: str = Field(..., description="CSS selector for the <iframe> element")
    selector: str = Field(..., description="CSS selector inside the iframe")


class IframeFillInput(BaseModel):
    """Input for filling an input inside an iframe."""
    session_id: str = Field(...)
    iframe_selector: str = Field(..., description="CSS selector for the <iframe> element")
    selector: str = Field(..., description="CSS selector inside the iframe")
    value: str = Field(..., description="Value to set in the input field")


# ── Shadow DOM ──────────────────────────────────────────────────


class ShadowEvalInput(BaseModel):
    """Input for evaluating JS inside a shadow DOM tree."""
    session_id: str = Field(...)
    selectors: list[str] = Field(
        ...,
        min_length=1,
        description="CSS selectors piercing shadow boundaries (selectors[0] in document, "
        "selectors[1] in selectors[0].shadowRoot, etc.)",
    )
    expression: str = Field(..., description="JavaScript expression to evaluate")
    await_promise: bool = Field(default=False)


class ShadowClickInput(BaseModel):
    """Input for clicking an element inside a shadow DOM tree."""
    session_id: str = Field(...)
    selectors: list[str] = Field(
        ...,
        min_length=1,
        description="CSS selectors piercing shadow boundaries",
    )


class ShadowFillInput(BaseModel):
    """Input for filling an input inside a shadow DOM tree."""
    session_id: str = Field(...)
    selectors: list[str] = Field(
        ...,
        min_length=1,
        description="CSS selectors piercing shadow boundaries",
    )
    value: str = Field(..., description="Value to set in the input field")


# ── Event subscription (W10) ────────────────────────────────────


class SubscribeEventsInput(BaseModel):
    """Input for subscribing to real-time browser events (W10)."""
    session_id: str = Field(...)
    event_types: list[str] = Field(
        ...,
        min_length=1,
        description="Event types: 'console', 'network_request', 'network_response', "
        "'dom_mutation', 'dialog', 'navigation'",
    )


class UnsubscribeEventsInput(BaseModel):
    """Input for unsubscribing from browser events (W10)."""
    session_id: str = Field(...)
    subscription_id: str = Field(..., description="Subscription ID from subscribe_events")


# ── WebExtensions ───────────────────────────────────────────────


class ExtensionInstallInput(BaseModel):
    """Input for installing a browser extension."""
    session_id: str = Field(...)
    path: str = Field(..., description="Path to .crx file or unpacked extension directory")


class ExtensionUninstallInput(BaseModel):
    """Input for uninstalling a browser extension."""
    session_id: str = Field(...)
    extension_id: str = Field(..., description="Extension ID returned by extension_install")


class ExtensionListInput(BaseModel):
    """Input for listing installed browser extensions."""
    session_id: str = Field(...)


# ── Browser preferences ─────────────────────────────────────────


class GetPrefInput(BaseModel):
    """Input for getting a browser preference value."""
    session_id: str = Field(...)
    key: str = Field(..., description="Preference key (e.g. 'download.default_directory')")


class SetPrefInput(BaseModel):
    """Input for setting a browser preference value."""
    session_id: str = Field(...)
    key: str = Field(..., description="Preference key")
    value: str = Field(..., description="Preference value to set")
