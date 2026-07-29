"""Pydantic v2 input models for all WaveXisMCP tools.

This module defines every ``BaseModel`` used as the typed input for
the MCP tools exposed by WaveXisMCP.  Models are grouped by
capability tier (Session, Navigation, Capture, JavaScript, DOM,
Input, Cookies, Tabs, Utility, Network, Storage, Emulation, A11y,
Interactions, and DevTools) and separated by section comments.
"""

from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    field_validator,
    model_validator,
)

SelectorStr = Annotated[str, StringConstraints(min_length=1, strip_whitespace=True)]

_WaitStrategy = Literal["load", "domcontentloaded", "networkidle", "selector", "url", "none"]

# Reasonable limits to prevent DoS from maliciously large payloads.
_MAX_STRING_LENGTH = 50_000
_MAX_CONTAINER_SIZE = 1_000
_MAX_TOTAL_FIELDS = 10_000


def _limit_input_size(data: Any) -> Any:
    """Reject oversized strings, lists, and dicts before field validation.

    Uses an explicit traversal stack so deeply nested payloads cannot
    overflow the Python call stack before validation begins.  The total
    number of container entries across the whole payload is also bounded
    so attackers cannot split a large payload across many small nested
    containers.
    """
    if isinstance(data, dict):
        if len(data) > _MAX_CONTAINER_SIZE:
            raise ValueError(f"input exceeds {_MAX_CONTAINER_SIZE} fields")
        stack = list(data.values())
        total = len(stack)
    elif isinstance(data, list):
        if len(data) > _MAX_CONTAINER_SIZE:
            raise ValueError(f"input list exceeds {_MAX_CONTAINER_SIZE} items")
        stack = list(data)
        total = len(stack)
    else:
        return data

    while stack:
        item = stack.pop()
        if isinstance(item, dict):
            if len(item) > _MAX_CONTAINER_SIZE:
                raise ValueError(f"input exceeds {_MAX_CONTAINER_SIZE} fields")
            total += len(item)
            if total > _MAX_TOTAL_FIELDS:
                raise ValueError(f"input exceeds {_MAX_TOTAL_FIELDS} total fields")
            stack.extend(item.values())
        elif isinstance(item, list):
            if len(item) > _MAX_CONTAINER_SIZE:
                raise ValueError(f"input list exceeds {_MAX_CONTAINER_SIZE} items")
            total += len(item)
            if total > _MAX_TOTAL_FIELDS:
                raise ValueError(f"input exceeds {_MAX_TOTAL_FIELDS} total items")
            stack.extend(item)
        elif isinstance(item, str) and len(item) > _MAX_STRING_LENGTH:
            raise ValueError(f"input string exceeds {_MAX_STRING_LENGTH} characters")

    return data


class BaseInput(BaseModel):
    """Base class for all tool inputs.

    Provides a reusable ``model_validator`` that limits string lengths and
    container sizes so a single request cannot exhaust server memory or
    browser resources.
    """

    @model_validator(mode="before")
    @classmethod
    def _limit(cls, data: Any) -> Any:
        return _limit_input_size(data)

    @field_validator("session_id", mode="before", check_fields=False)
    @classmethod
    def _session_id_not_empty(cls, value: Any) -> Any:
        """Reject empty or whitespace-only session IDs in every input model.

        Non-empty session IDs are stripped so accidental leading or trailing
        whitespace does not cause a ``SessionNotFoundError`` later.
        """
        if isinstance(value, str):
            value = value.strip()
            if not value:
                raise ValueError("session_id cannot be empty")
        return value


# ── Session management ──────────────────────────────────────────


class SessionOpenInput(BaseInput):
    """Input for opening a new browser session."""

    backend: Literal["cdp", "bidi", "auto"] = Field(
        default="cdp", description="Backend: 'cdp', 'bidi', or 'auto'"
    )
    headless: bool = Field(default=True, description="Run browser in headless mode")
    width: int = Field(default=1280, ge=320, le=3840, description="Viewport width in pixels")
    height: int = Field(default=800, ge=240, le=2160, description="Viewport height in pixels")
    user_agent: str | None = Field(default=None, description="Custom User-Agent string")
    extra_headers: dict[str, str] = Field(
        default_factory=dict, description="Extra HTTP headers to send"
    )
    proxy: str | None = Field(default=None, description="Proxy server URL (e.g. http://host:port)")
    timeout: int = Field(default=30000, ge=1000, le=300000, description="Operation timeout in ms")
    user_data_dir: str | None = Field(
        default=None, description="Persistent Chrome user data directory"
    )
    browser_url: str | None = Field(
        default=None, description="WebSocket URL of an existing browser (e.g. ws://localhost:9222)"
    )
    remote_url: str | None = Field(default=None, description="Cloud browser WebSocket URL")
    stealth: bool = Field(default=False, description="Enable anti-bot stealth mode")
    browser: Literal["chrome", "firefox"] = Field(
        default="chrome",
        description=(
            "Browser engine for BiDi backend: 'chrome' (chromedriver) or "
            "'firefox' (geckodriver). Only used when backend='bidi'."
        ),
    )
    connect_existing: bool = Field(
        default=False,
        description=(
            "Launch Chrome with --remote-debugging-port and connect to it. "
            "Useful for reusing an existing browser profile with logged-in "
            "sessions. The browser is launched headed (headless is ignored)."
        ),
    )


class SessionCloseInput(BaseInput):
    """Input for closing an existing browser session."""

    session_id: str = Field(..., description="Session ID from wavexis_session_open")


class SessionInfoInput(BaseInput):
    """Input for querying session metadata."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")


# ── Navigation ──────────────────────────────────────────────────


class NavigateInput(BaseInput):
    """Input for navigating to a URL."""

    url: str = Field(..., description="URL to navigate to")
    session_id: str | None = Field(
        default=None,
        description="Active session ID. If omitted, a stateless session is created for this call.",
    )
    wait_strategy: _WaitStrategy = Field(
        default="load",
        description="Wait strategy: load, domcontentloaded, networkidle, selector, url, none",
    )
    wait_selector: str | None = Field(
        default=None, description="CSS selector to wait for (used when wait_strategy='selector')"
    )
    wait_url_pattern: str | None = Field(
        default=None, description="URL pattern to wait for (used when wait_strategy='url')"
    )
    wait_timeout: int = Field(
        default=30000, ge=1000, le=300000, description="Timeout in ms for wait conditions"
    )
    headless: bool = Field(default=True, description="Run browser in headless mode")
    backend: Literal["cdp", "bidi", "auto"] = Field(
        default="cdp", description="Backend: 'cdp', 'bidi', or 'auto'"
    )


class SimpleNavInput(BaseInput):
    """Input for session-only navigation actions (back, forward, stop)."""

    session_id: str = Field(..., description="Active session ID")


class ReloadInput(BaseInput):
    """Input for reloading the current page."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    ignore_cache: bool = Field(default=False, description="Bypass cache on reload")


class WaitInput(BaseInput):
    """Input for waiting on a page condition."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    strategy: _WaitStrategy = Field(
        default="load",
        description="load, domcontentloaded, networkidle, selector, url, none",
    )
    selector: str | None = Field(default=None, description="CSS selector to target an element")
    url_pattern: str | None = Field(
        default=None, description="URL pattern to wait for (used when strategy='url')"
    )
    timeout: int = Field(default=30000, ge=1000, le=300000, description="Operation timeout in ms")


# ── Capture ─────────────────────────────────────────────────────


class ScreenshotInput(BaseInput):
    """Input for taking a screenshot."""

    url: str | None = Field(
        default=None, description="URL to navigate to (required without session_id)"
    )
    session_id: str | None = Field(
        default=None,
        description="Active session ID. If omitted, a stateless session is created for this call.",
    )
    full_page: bool = Field(default=True, description="Capture full scrollable page")
    format: Literal["png", "jpeg"] = Field(
        default="png", description="Image format: 'png' or 'jpeg'"
    )
    quality: int = Field(default=80, ge=1, le=100, description="JPEG quality (ignored for PNG)")
    selector: str | None = Field(
        default=None, description="CSS selector — screenshot only this element"
    )
    js: str | None = Field(default=None, description="JavaScript to execute before screenshot")
    device: str | None = Field(default=None, description="Device preset name (e.g. 'iphone-15')")
    output_path: str | None = Field(
        default=None, description="Save to file instead of returning base64"
    )
    wait_strategy: _WaitStrategy = Field(
        default="load",
        description="Wait strategy: load, domcontentloaded, networkidle, selector, url, none",
    )
    wait_selector: str | None = Field(
        default=None, description="CSS selector to wait for (used when wait_strategy='selector')"
    )
    wait_timeout: int = Field(
        default=30000, ge=1000, le=300000, description="Timeout in ms for wait conditions"
    )
    headless: bool = Field(default=True, description="Run browser in headless mode")
    width: int = Field(default=1280, ge=320, le=3840, description="Viewport width in pixels")
    height: int = Field(default=800, ge=240, le=2160, description="Viewport height in pixels")
    backend: Literal["cdp", "bidi", "auto"] = Field(
        default="cdp", description="Backend: 'cdp', 'bidi', or 'auto'"
    )


class PDFInput(BaseInput):
    """Input for generating a PDF."""

    url: str | None = Field(
        default=None, description="URL to navigate to (required without session_id)"
    )
    session_id: str | None = Field(
        default=None,
        description="Active session ID. If omitted, a stateless session is created for this call.",
    )
    paper: Literal["a4", "letter", "legal", "a3", "a5"] = Field(
        default="letter", description="Paper size: a4, letter, legal, a3, a5"
    )
    landscape: bool = Field(default=False, description="Use landscape orientation")
    margin: str = Field(default="0.4in", description="Page margin (e.g. '0.4in')")
    no_header_footer: bool = Field(default=False, description="Exclude header and footer from PDF")
    media: Literal["print", "screen"] = Field(
        default="print", description="CSS media: 'print' or 'screen'"
    )
    js: str | None = Field(default=None, description="JavaScript to execute before the action")
    output_path: str | None = Field(
        default=None,
        description="File path to save the output. If omitted, a default path is used.",
    )
    wait_timeout: int = Field(
        default=30000, ge=1000, le=300000, description="Timeout in ms for wait conditions"
    )
    headless: bool = Field(default=True, description="Run browser in headless mode")
    backend: Literal["cdp", "bidi", "auto"] = Field(
        default="cdp", description="Backend: 'cdp', 'bidi', or 'auto'"
    )


class PagePDFInput(BaseInput):
    """Input for generating a PDF via the low-level Page.printToPDF CDP method."""

    url: str | None = Field(
        default=None, description="URL to navigate to (required without session_id)"
    )
    session_id: str | None = Field(
        default=None,
        description="Active session ID. If omitted, a stateless session is created for this call.",
    )
    landscape: bool = Field(default=False, description="Use landscape orientation")
    display_header_footer: bool = Field(
        default=False, description="Include header and footer in PDF"
    )
    print_background: bool = Field(default=False, description="Print background graphics in PDF")
    scale: float = Field(default=1.0, ge=0.1, le=2.0, description="Scale factor for PDF rendering")
    paper_width: float = Field(default=8.5, ge=1.0, le=100.0, description="Paper width in inches")
    paper_height: float = Field(
        default=11.0, ge=1.0, le=100.0, description="Paper height in inches"
    )
    margin_top: float = Field(default=0.4, ge=0.0, description="Top margin in inches")
    margin_bottom: float = Field(default=0.4, ge=0.0, description="Bottom margin in inches")
    margin_left: float = Field(default=0.4, ge=0.0, description="Left margin in inches")
    margin_right: float = Field(default=0.4, ge=0.0, description="Right margin in inches")
    output_path: str | None = Field(default=None, description="Path to save the decoded PDF bytes")
    wait_timeout: int = Field(
        default=30000, ge=1000, le=300000, description="Timeout in ms for wait conditions"
    )
    headless: bool = Field(default=True, description="Run browser in headless mode")
    backend: Literal["cdp", "bidi", "auto"] = Field(
        default="cdp", description="Backend: 'cdp', 'bidi', or 'auto'"
    )


class PageSnapshotInput(BaseInput):
    """Input for capturing a page snapshot as MHTML or text."""

    url: str | None = Field(
        default=None, description="URL to navigate to (required without session_id)"
    )
    session_id: str | None = Field(
        default=None,
        description="Active session ID. If omitted, a stateless session is created for this call.",
    )
    format: Literal["mhtml", "text"] = Field(
        default="mhtml", description="Output format: 'mhtml' or 'text'"
    )
    output_path: str | None = Field(
        default=None,
        description="File path to save the output. If omitted, a default path is used.",
    )
    wait_timeout: int = Field(
        default=30000, ge=1000, le=300000, description="Timeout in ms for wait conditions"
    )
    headless: bool = Field(default=True, description="Run browser in headless mode")
    backend: Literal["cdp", "bidi", "auto"] = Field(
        default="cdp", description="Backend: 'cdp', 'bidi', or 'auto'"
    )


class ScrapeInput(BaseInput):
    """Input for scraping multiple URLs."""

    urls: list[str] = Field(..., min_length=1, max_length=50, description="URLs to scrape")
    session_id: str | None = Field(
        default=None,
        description="Active session ID. If omitted, a stateless session is created for this call.",
    )
    expression: str = Field(
        default="document.title", description="JS expression to evaluate on each page"
    )
    output_format: Literal["json", "csv"] = Field(
        default="json", description="Output format: 'json' or 'csv'"
    )
    selector: str | None = Field(default=None, description="CSS selector to wait for")
    wait_timeout: int = Field(
        default=30000, ge=1000, le=300000, description="Timeout in ms for wait conditions"
    )
    headless: bool = Field(default=True, description="Run browser in headless mode")
    backend: Literal["cdp", "bidi", "auto"] = Field(
        default="cdp", description="Backend: 'cdp', 'bidi', or 'auto'"
    )
    limit: int = Field(default=50, ge=1, le=500, description="Max results to return")
    offset: int = Field(default=0, ge=0, description="Skip first N results for pagination")


class ScreencastInput(BaseInput):
    """Input for capturing a frame sequence."""

    url: str | None = Field(
        default=None, description="URL to navigate to (required without session_id)"
    )
    session_id: str | None = Field(
        default=None,
        description="Active session ID. If omitted, a stateless session is created for this call.",
    )
    format: Literal["png", "jpeg"] = Field(
        default="png", description="Image format: 'png' or 'jpeg'"
    )
    quality: int = Field(
        default=80, ge=1, le=100, description="JPEG quality 1-100 (ignored for PNG)"
    )
    max_width: int = Field(
        default=1280, ge=320, le=3840, description="Maximum screenshot width in pixels"
    )
    max_height: int = Field(
        default=800, ge=240, le=2160, description="Maximum screenshot height in pixels"
    )
    duration: float = Field(default=5.0, ge=0.5, le=60.0, description="Capture duration in seconds")
    interval: float = Field(default=1.0, ge=0.1, le=10.0, description="Seconds between frames")
    output_dir: str | None = Field(default=None, description="Save frames to directory")
    wait_timeout: int = Field(
        default=30000, ge=1000, le=300000, description="Timeout in ms for wait conditions"
    )
    headless: bool = Field(default=True, description="Run browser in headless mode")
    backend: Literal["cdp", "bidi", "auto"] = Field(
        default="cdp", description="Backend: 'cdp', 'bidi', or 'auto'"
    )


# ── JavaScript ──────────────────────────────────────────────────


class EvalInput(BaseInput):
    """Input for evaluating a JavaScript expression."""

    expression: str = Field(..., description="JavaScript expression to evaluate")
    session_id: str | None = Field(
        default=None,
        description="Active session ID. If omitted, a stateless session is created for this call.",
    )
    url: str | None = Field(
        default=None, description="URL to navigate to first (required without session)"
    )
    await_promise: bool = Field(default=False, description="Await a returned Promise")
    wait_timeout: int = Field(
        default=30000, ge=1000, le=300000, description="Timeout in ms for wait conditions"
    )
    headless: bool = Field(default=True, description="Run browser in headless mode")
    backend: Literal["cdp", "bidi", "auto"] = Field(
        default="cdp", description="Backend: 'cdp', 'bidi', or 'auto'"
    )


# ── DOM ─────────────────────────────────────────────────────────


class DOMGetInput(BaseInput):
    """Input for getting HTML of an element."""

    selector: SelectorStr = Field(..., description="CSS selector for the target element")
    session_id: str | None = Field(
        default=None,
        description="Active session ID. If omitted, a stateless session is created for this call.",
    )
    url: str | None = Field(
        default=None, description="URL to navigate to (required without session_id)"
    )
    outer: bool = Field(default=True, description="Return outerHTML (True) or innerHTML (False)")
    wait_timeout: int = Field(
        default=30000, ge=1000, le=300000, description="Timeout in ms for wait conditions"
    )
    headless: bool = Field(default=True, description="Run browser in headless mode")
    backend: Literal["cdp", "bidi", "auto"] = Field(
        default="cdp", description="Backend: 'cdp', 'bidi', or 'auto'"
    )


class DOMQueryInput(BaseInput):
    """Input for querying elements by CSS selector."""

    selector: SelectorStr = Field(..., description="CSS selector for the target element")
    session_id: str | None = Field(
        default=None,
        description="Active session ID. If omitted, a stateless session is created for this call.",
    )
    url: str | None = Field(
        default=None, description="URL to navigate to (required without session_id)"
    )
    all: bool = Field(default=False, description="Return all matches (True) or first only (False)")
    limit: int = Field(default=50, ge=1, le=500, description="Max elements to return when all=True")
    offset: int = Field(default=0, ge=0, description="Skip first N elements for pagination")
    wait_timeout: int = Field(
        default=30000, ge=1000, le=300000, description="Timeout in ms for wait conditions"
    )
    headless: bool = Field(default=True, description="Run browser in headless mode")
    backend: Literal["cdp", "bidi", "auto"] = Field(
        default="cdp", description="Backend: 'cdp', 'bidi', or 'auto'"
    )


class DOMSetAttrInput(BaseInput):
    """Input for setting an attribute on an element."""

    selector: SelectorStr = Field(..., description="CSS selector for the target element")
    name: str = Field(..., min_length=1, description="Attribute name")
    value: str = Field(..., description="Attribute value")
    session_id: str = Field(..., description="Active session ID from wavexis_session_open")


class DOMGetAttrInput(BaseInput):
    """Input for getting an attribute value from an element."""

    selector: SelectorStr = Field(..., description="CSS selector for the target element")
    name: str = Field(..., min_length=1, description="Name of the item")
    session_id: str = Field(..., description="Active session ID from wavexis_session_open")


class DOMRemoveAttrInput(BaseInput):
    """Input for removing an attribute from an element."""

    selector: SelectorStr = Field(..., description="CSS selector for the target element")
    name: str = Field(..., min_length=1, description="Name of the item")
    session_id: str = Field(..., description="Active session ID from wavexis_session_open")


class DOMRemoveInput(BaseInput):
    """Input for removing an element from the DOM."""

    selector: SelectorStr = Field(..., description="CSS selector for the target element")
    session_id: str = Field(..., description="Active session ID from wavexis_session_open")


class DOMFocusInput(BaseInput):
    """Input for focusing an element."""

    selector: SelectorStr = Field(..., description="CSS selector for the target element")
    session_id: str = Field(..., description="Active session ID from wavexis_session_open")


class DOMScrollInput(BaseInput):
    """Input for scrolling to an element or by offset."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    selector: str | None = Field(default=None, description="CSS selector to scroll to")
    x: int = Field(default=0, description="Horizontal scroll offset")
    y: int = Field(default=0, description="Vertical scroll offset")


class DOMSnapshotInput(BaseInput):
    """Input for capturing a full DOM snapshot."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")


# ── Input ───────────────────────────────────────────────────────


class ClickInput(BaseInput):
    """Input for clicking an element."""

    selector: SelectorStr = Field(..., description="CSS selector for element to click")
    session_id: str | None = Field(
        default=None,
        description="Active session ID. If omitted, a stateless session is created for this call.",
    )
    url: str | None = Field(
        default=None, description="URL to navigate to (required without session_id)"
    )
    button: Literal["left", "right", "middle"] = Field(
        default="left", description="left, right, middle"
    )
    click_count: int = Field(default=1, ge=1, le=10, description="Number of clicks to perform")
    wait_timeout: int = Field(
        default=30000, ge=1000, le=300000, description="Timeout in ms for wait conditions"
    )
    headless: bool = Field(default=True, description="Run browser in headless mode")
    backend: Literal["cdp", "bidi", "auto"] = Field(
        default="cdp", description="Backend: 'cdp', 'bidi', or 'auto'"
    )


class DoubleClickInput(BaseInput):
    """Input for double-clicking an element."""

    selector: SelectorStr = Field(..., description="CSS selector for element to double-click")
    session_id: str | None = Field(
        default=None,
        description="Active session ID. If omitted, a stateless session is created for this call.",
    )
    url: str | None = Field(
        default=None, description="URL to navigate to (required without session_id)"
    )
    auto_wait: bool = Field(default=True, description="Wait for the element before clicking")
    wait_timeout: int = Field(
        default=30000, ge=1000, le=300000, description="Timeout in ms for wait conditions"
    )
    headless: bool = Field(default=True, description="Run browser in headless mode")
    backend: Literal["cdp", "bidi", "auto"] = Field(
        default="cdp", description="Backend: 'cdp', 'bidi', or 'auto'"
    )


class RightClickInput(BaseInput):
    """Input for right-clicking an element."""

    selector: SelectorStr = Field(..., description="CSS selector for element to right-click")
    session_id: str | None = Field(
        default=None,
        description="Active session ID. If omitted, a stateless session is created for this call.",
    )
    url: str | None = Field(
        default=None, description="URL to navigate to (required without session_id)"
    )
    auto_wait: bool = Field(default=True, description="Wait for the element before clicking")
    wait_timeout: int = Field(
        default=30000, ge=1000, le=300000, description="Timeout in ms for wait conditions"
    )
    headless: bool = Field(default=True, description="Run browser in headless mode")
    backend: Literal["cdp", "bidi", "auto"] = Field(
        default="cdp", description="Backend: 'cdp', 'bidi', or 'auto'"
    )


class TypeInput(BaseInput):
    """Input for typing text into an element."""

    selector: SelectorStr = Field(..., description="CSS selector for the target element")
    text: str = Field(..., min_length=1, description="Text to type character by character")
    session_id: str | None = Field(
        default=None,
        description="Active session ID. If omitted, a stateless session is created for this call.",
    )
    url: str | None = Field(
        default=None, description="URL to navigate to (required without session_id)"
    )
    delay: int = Field(default=0, ge=0, le=1000, description="Delay between keystrokes in ms")
    wait_timeout: int = Field(
        default=30000, ge=1000, le=300000, description="Timeout in ms for wait conditions"
    )
    headless: bool = Field(default=True, description="Run browser in headless mode")
    backend: Literal["cdp", "bidi", "auto"] = Field(
        default="cdp", description="Backend: 'cdp', 'bidi', or 'auto'"
    )


class FillInput(BaseInput):
    """Input for filling an input element."""

    selector: SelectorStr = Field(..., description="CSS selector for the target element")
    value: str = Field(..., description="Value to fill (replaces existing content)")
    session_id: str | None = Field(
        default=None,
        description="Active session ID. If omitted, a stateless session is created for this call.",
    )
    url: str | None = Field(
        default=None, description="URL to navigate to (required without session_id)"
    )
    wait_timeout: int = Field(
        default=30000, ge=1000, le=300000, description="Timeout in ms for wait conditions"
    )
    headless: bool = Field(default=True, description="Run browser in headless mode")
    backend: Literal["cdp", "bidi", "auto"] = Field(
        default="cdp", description="Backend: 'cdp', 'bidi', or 'auto'"
    )


class FindByTextInput(BaseInput):
    """Input for finding elements by visible text content."""

    query: str = Field(..., min_length=1, description="Text to search for in visible page content")
    all: bool = Field(default=False, description="Return all matches (True) or first match (False)")
    session_id: str = Field(..., description="Active session ID from wavexis_session_open")


class NLClickInput(BaseInput):
    """Input for clicking an element by natural language query."""

    query: str = Field(
        ..., min_length=1, description="Natural language description of the element to click"
    )
    auto_wait: bool = Field(
        default=True, description="Wait for element to be ready before clicking"
    )
    session_id: str = Field(..., description="Active session ID from wavexis_session_open")


class NLFillInput(BaseInput):
    """Input for filling an element by natural language query."""

    query: str = Field(
        ..., min_length=1, description="Natural language description of the element to fill"
    )
    value: str = Field(..., min_length=1, description="Value to fill")
    auto_wait: bool = Field(default=True, description="Wait for element to be ready before filling")
    session_id: str = Field(..., description="Active session ID from wavexis_session_open")


class FormField(BaseModel):
    """A single form field descriptor for ``FillFormInput``."""

    selector: SelectorStr = Field(
        ..., min_length=1, description="CSS selector for the input element"
    )
    value: str = Field(..., description="Value to fill")


class FillFormInput(BaseInput):
    """Input for filling multiple form fields in one call."""

    fields: list[FormField] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Form fields to fill",
    )
    session_id: str | None = Field(
        default=None,
        description="Active session ID. If omitted, a stateless session is created for this call.",
    )
    url: str | None = Field(
        default=None, description="URL to navigate to (required without session_id)"
    )
    wait_timeout: int = Field(
        default=30000, ge=1000, le=300000, description="Timeout in ms for wait conditions"
    )
    headless: bool = Field(default=True, description="Run browser in headless mode")
    backend: Literal["cdp", "bidi", "auto"] = Field(
        default="cdp", description="Backend: 'cdp', 'bidi', or 'auto'"
    )


class SelectOptionInput(BaseInput):
    """Input for selecting an option in a ``<select>`` element."""

    selector: SelectorStr = Field(..., description="CSS selector for <select> element")
    value: str = Field(..., min_length=1, description="Option value to select")
    session_id: str | None = Field(
        default=None,
        description="Active session ID. If omitted, a stateless session is created for this call.",
    )
    url: str | None = Field(
        default=None, description="URL to navigate to (required without session_id)"
    )
    wait_timeout: int = Field(
        default=30000, ge=1000, le=300000, description="Timeout in ms for wait conditions"
    )
    headless: bool = Field(default=True, description="Run browser in headless mode")
    backend: Literal["cdp", "bidi", "auto"] = Field(
        default="cdp", description="Backend: 'cdp', 'bidi', or 'auto'"
    )


class HoverInput(BaseInput):
    """Input for hovering over an element."""

    selector: SelectorStr = Field(..., description="CSS selector for the target element")
    session_id: str | None = Field(
        default=None,
        description="Active session ID. If omitted, a stateless session is created for this call.",
    )
    url: str | None = Field(
        default=None, description="URL to navigate to (required without session_id)"
    )
    wait_timeout: int = Field(
        default=30000, ge=1000, le=300000, description="Timeout in ms for wait conditions"
    )
    headless: bool = Field(default=True, description="Run browser in headless mode")
    backend: Literal["cdp", "bidi", "auto"] = Field(
        default="cdp", description="Backend: 'cdp', 'bidi', or 'auto'"
    )


class KeyPressInput(BaseInput):
    """Input for pressing a keyboard key."""

    key: str = Field(..., description="Key to press (e.g. 'Enter', 'Tab', 'Escape', 'a')")
    session_id: str = Field(..., description="Active session ID from wavexis_session_open")


class DragInput(BaseInput):
    """Input for dragging an element from source to target."""

    source: str = Field(..., description="CSS selector for drag source")
    target: str = Field(..., description="CSS selector for drop target")
    session_id: str | None = Field(
        default=None,
        description="Active session ID. If omitted, a stateless session is created for this call.",
    )
    url: str | None = Field(
        default=None, description="URL to navigate to (required without session_id)"
    )
    wait_timeout: int = Field(
        default=30000, ge=1000, le=300000, description="Timeout in ms for wait conditions"
    )
    headless: bool = Field(default=True, description="Run browser in headless mode")
    backend: Literal["cdp", "bidi", "auto"] = Field(
        default="cdp", description="Backend: 'cdp', 'bidi', or 'auto'"
    )


class TapInput(BaseInput):
    """Input for tapping an element (touch emulation)."""

    selector: SelectorStr = Field(..., description="CSS selector for element to tap")
    session_id: str | None = Field(
        default=None,
        description="Active session ID. If omitted, a stateless session is created for this call.",
    )
    url: str | None = Field(
        default=None, description="URL to navigate to (required without session_id)"
    )
    wait_timeout: int = Field(
        default=30000, ge=1000, le=300000, description="Timeout in ms for wait conditions"
    )
    headless: bool = Field(default=True, description="Run browser in headless mode")
    backend: Literal["cdp", "bidi", "auto"] = Field(
        default="cdp", description="Backend: 'cdp', 'bidi', or 'auto'"
    )


class SetFilesInput(BaseInput):
    """Input for uploading files to a file input element."""

    selector: SelectorStr = Field(..., description="CSS selector for <input type='file'> element")
    files: list[str] = Field(..., min_length=1, description="Absolute file paths to upload")
    session_id: str | None = Field(
        default=None,
        description="Active session ID. If omitted, a stateless session is created for this call.",
    )
    url: str | None = Field(
        default=None, description="URL to navigate to (required without session_id)"
    )
    wait_timeout: int = Field(
        default=30000, ge=1000, le=300000, description="Timeout in ms for wait conditions"
    )
    headless: bool = Field(default=True, description="Run browser in headless mode")
    backend: Literal["cdp", "bidi", "auto"] = Field(
        default="cdp", description="Backend: 'cdp', 'bidi', or 'auto'"
    )


class DropInput(BaseInput):
    """Input for dropping files or MIME-typed data onto an element."""

    selector: SelectorStr = Field(..., description="CSS selector for the drop target")
    data: dict[str, str] = Field(
        default_factory=dict, description="MIME type to string payload map"
    )
    paths: list[str] = Field(default_factory=list, description="Absolute file paths to drop")
    session_id: str | None = Field(
        default=None,
        description="Active session ID. If omitted, a stateless session is created for this call.",
    )
    url: str | None = Field(
        default=None, description="URL to navigate to (required without session_id)"
    )
    wait_timeout: int = Field(
        default=30000, ge=1000, le=300000, description="Timeout in ms for wait conditions"
    )
    headless: bool = Field(default=True, description="Run browser in headless mode")
    backend: Literal["cdp", "bidi", "auto"] = Field(
        default="cdp", description="Backend: 'cdp', 'bidi', or 'auto'"
    )


class CheckInput(BaseInput):
    """Input for checking/unchecking a checkbox or radio."""

    selector: SelectorStr = Field(..., description="CSS selector for checkbox/radio")
    session_id: str = Field(..., description="Active session ID from wavexis_session_open")


# ── Cookies ─────────────────────────────────────────────────────


class CookiesGetInput(BaseInput):
    """Input for getting cookies."""

    session_id: str | None = Field(
        default=None,
        description="Active session ID. If omitted, a stateless session is created for this call.",
    )
    url: str | None = Field(
        default=None, description="URL to navigate to (required without session_id)"
    )
    wait_timeout: int = Field(
        default=30000, ge=1000, le=300000, description="Timeout in ms for wait conditions"
    )
    headless: bool = Field(default=True, description="Run browser in headless mode")
    backend: Literal["cdp", "bidi", "auto"] = Field(
        default="cdp", description="Backend: 'cdp', 'bidi', or 'auto'"
    )


class CookiesSetInput(BaseInput):
    """Input for setting a cookie."""

    name: str = Field(..., min_length=1, description="Name of the item")
    value: str = Field(..., min_length=1, description="Value to set")
    domain: str = Field(..., min_length=1, description="Cookie domain")
    path: str = Field(default="/", min_length=1, description="Cookie path")
    secure: bool = Field(default=True, description="Whether the cookie is Secure")
    http_only: bool = Field(default=False, description="Whether the cookie is HttpOnly")
    same_site: Literal["Strict", "Lax", "None"] = Field(
        default="Lax", description="SameSite attribute: Strict, Lax, or None"
    )
    session_id: str | None = Field(
        default=None,
        description="Active session ID. If omitted, a stateless session is created for this call.",
    )
    url: str | None = Field(
        default=None, description="URL to navigate to (required without session_id)"
    )
    wait_timeout: int = Field(
        default=30000, ge=1000, le=300000, description="Timeout in ms for wait conditions"
    )
    headless: bool = Field(default=True, description="Run browser in headless mode")
    backend: Literal["cdp", "bidi", "auto"] = Field(
        default="cdp", description="Backend: 'cdp', 'bidi', or 'auto'"
    )


class CookiesDeleteInput(BaseInput):
    """Input for deleting cookies."""

    name: str = Field(..., min_length=1, description="Name of the item")
    domain: str = Field(..., min_length=1, description="Cookie domain")
    session_id: str | None = Field(
        default=None,
        description="Active session ID. If omitted, a stateless session is created for this call.",
    )
    url: str | None = Field(
        default=None, description="URL to navigate to (required without session_id)"
    )
    wait_timeout: int = Field(
        default=30000, ge=1000, le=300000, description="Timeout in ms for wait conditions"
    )
    headless: bool = Field(default=True, description="Run browser in headless mode")
    backend: Literal["cdp", "bidi", "auto"] = Field(
        default="cdp", description="Backend: 'cdp', 'bidi', or 'auto'"
    )


class CookiesClearInput(BaseInput):
    """Input for clearing all cookies."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")


# ── Tabs ────────────────────────────────────────────────────────


class ListTabsInput(BaseInput):
    """Input for listing browser tabs."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")


class NewTabInput(BaseInput):
    """Input for creating a new browser tab."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    url: str = Field(default="about:blank", description="URL for the new tab")


class CloseTabInput(BaseInput):
    """Input for closing a browser tab."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    tab_id: str = Field(..., description="Tab ID to operate on")


class ActivateTabInput(BaseInput):
    """Input for activating (focusing) a browser tab."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    tab_id: str = Field(..., description="Tab ID to operate on")


# ── Utility ─────────────────────────────────────────────────────


class BrowserVersionInput(BaseInput):
    """Input for getting the browser version."""

    session_id: str | None = Field(
        default=None,
        description="Active session ID. If omitted, a stateless session is created for this call.",
    )
    backend: Literal["cdp", "bidi", "auto"] = Field(
        default="cdp", description="Backend: 'cdp', 'bidi', or 'auto'"
    )


# ── Network ─────────────────────────────────────────────────────


class SetHeadersInput(BaseInput):
    """Input for setting extra HTTP headers."""

    headers: dict[str, str] = Field(..., description="HTTP headers to set")
    session_id: str = Field(..., description="Active session ID from wavexis_session_open")


class SetUserAgentInput(BaseInput):
    """Input for setting a custom User-Agent string."""

    user_agent: str = Field(..., description="User-Agent string to set")
    session_id: str = Field(..., description="Active session ID from wavexis_session_open")


class BlockRequestsInput(BaseInput):
    """Input for blocking requests matching URL patterns."""

    patterns: list[str] = Field(..., description="URL patterns to block (glob-style)")
    session_id: str = Field(..., description="Active session ID from wavexis_session_open")


class ThrottleNetworkInput(BaseInput):
    """Input for throttling network speed."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    preset: str | None = Field(default=None, description="Preset: none, 2g, 3g, 4g, offline")
    latency_ms: int = Field(default=0, ge=0, le=10000, description="Emulated network latency in ms")
    download_bps: int = Field(
        default=-1, ge=-1, description="Download throughput in bytes/s (-1 for unlimited)"
    )
    upload_bps: int = Field(
        default=-1, ge=-1, description="Upload throughput in bytes/s (-1 for unlimited)"
    )
    offline: bool = Field(default=False, description="Set the browser to offline mode")


class SetNetworkStateInput(BaseInput):
    """Input for overriding the browser network state (online/offline)."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    state: str = Field(
        default="online",
        pattern=r"^(online|offline)$",
        description="Network state: 'online' or 'offline'",
    )


class SetCacheDisabledInput(BaseInput):
    """Input for enabling or disabling the browser cache."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    disabled: bool = Field(default=True, description="Whether the network is disabled")


class CaptureHARInput(BaseInput):
    """Input for capturing HAR data for a page load."""

    url: str = Field(..., description="URL to navigate to for HAR capture")
    session_id: str | None = Field(
        default=None,
        description="Active session ID. If omitted, a stateless session is created for this call.",
    )
    wait_ms: int = Field(default=3000, ge=500, le=30000, description="Time to wait in ms")
    filter: str | None = Field(default=None, description="URL filter pattern")
    timeout: int = Field(default=30000, ge=1000, le=300000, description="Operation timeout in ms")
    path: str | None = Field(default=None, description="Optional file path to write the HAR to")
    headless: bool = Field(default=True, description="Run browser in headless mode")
    backend: Literal["cdp", "bidi", "auto"] = Field(
        default="cdp", description="Backend: 'cdp', 'bidi', or 'auto'"
    )


class InterceptRequestsInput(BaseInput):
    """Input for registering a request interception pattern."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    pattern: dict[str, str] = Field(
        ..., description="Interception pattern (urlPattern, resourceType, etc.)"
    )


class MockResponseInput(BaseInput):
    """Input for registering a mock response for a URL pattern."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    url: str = Field(..., description="URL pattern to match")
    status: int = Field(default=200, description="HTTP status code for the mocked response")
    content_type: str = Field(
        default="application/json", description="Content-Type header for the mocked response"
    )
    body: str = Field(default="", description="Response body for the mocked response")
    headers: dict[str, str] = Field(
        default_factory=dict, description="Response headers for the mocked response"
    )


class NetworkRequestsInput(BaseInput):
    """Input for listing network requests with pagination."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    filter: str | None = Field(default=None, description="URL filter pattern")
    resource_type: str | None = Field(
        default=None, description="Filter by type: document, stylesheet, image, etc."
    )
    limit: int = Field(default=100, ge=1, le=1000, description="Max requests to return")
    offset: int = Field(default=0, ge=0, description="Skip first N requests for pagination")
    mode: Literal["performance", "events"] = Field(
        default="performance",
        description="Use performance.getEntriesByType or CDP network event log",
    )


class NetworkRequestInput(BaseInput):
    """Input for getting full details of a single network request by index."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    index: int = Field(..., ge=1, description="1-based index from wavexis_network_requests")
    part: Literal["request-headers", "request-body", "response-headers", "response-body"] | None = (
        Field(default=None, description="Return only this part")
    )


class NetworkClearInput(BaseInput):
    """Input for clearing the network event log."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")


class RouteInput(BaseInput):
    """Input for adding a network route/mock."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    pattern: str = Field(..., description="URL glob to match (e.g. '**/api/users')")
    status: int | None = Field(
        default=None, ge=100, le=599, description="HTTP status code to return"
    )
    body: str | None = Field(default=None, description="Response body for mocked requests")
    content_type: str | None = Field(
        default=None, description="Content-Type header for mocked response"
    )
    headers: list[str] | None = Field(default=None, description='Headers in "Name: Value" format')
    remove_headers: str | None = Field(
        default=None, description="Comma-separated header names to remove"
    )


class UnrouteInput(BaseInput):
    """Input for removing network routes."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    pattern: str | None = Field(default=None, description="Pattern to remove; omit to remove all")


class RouteListInput(BaseInput):
    """Input for listing active network routes."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")


# ── Storage ─────────────────────────────────────────────────────


class LocalStorageGetInput(BaseInput):
    """Input for getting a localStorage value."""

    key: str = Field(..., min_length=1, description="Storage key")
    session_id: str = Field(..., description="Active session ID from wavexis_session_open")


class LocalStorageSetInput(BaseInput):
    """Input for setting a localStorage key/value pair."""

    key: str = Field(..., min_length=1, description="Storage key")
    value: str = Field(..., description="Storage value")
    session_id: str = Field(..., description="Active session ID from wavexis_session_open")


class LocalStorageDeleteInput(BaseInput):
    """Input for deleting a localStorage key."""

    key: str = Field(..., min_length=1, description="Storage key")
    session_id: str = Field(..., description="Active session ID from wavexis_session_open")


class LocalStorageClearInput(BaseInput):
    """Input for clearing all localStorage entries."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")


class LocalStorageListInput(BaseInput):
    """Input for listing all localStorage entries."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")


class SessionStorageGetInput(BaseInput):
    """Input for getting a sessionStorage value."""

    key: str = Field(..., min_length=1, description="Storage key")
    session_id: str = Field(..., description="Active session ID from wavexis_session_open")


class SessionStorageSetInput(BaseInput):
    """Input for setting a sessionStorage key/value pair."""

    key: str = Field(..., min_length=1, description="Storage key")
    value: str = Field(..., description="Storage value")
    session_id: str = Field(..., description="Active session ID from wavexis_session_open")


class SessionStorageDeleteInput(BaseInput):
    """Input for deleting a sessionStorage key."""

    key: str = Field(..., min_length=1, description="Storage key")
    session_id: str = Field(..., description="Active session ID from wavexis_session_open")


class SessionStorageClearInput(BaseInput):
    """Input for clearing all sessionStorage entries."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")


class SessionStorageListInput(BaseInput):
    """Input for listing all sessionStorage entries."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")


class CacheStorageListInput(BaseInput):
    """Input for listing Cache Storage cache names."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")


class CacheStorageEntriesInput(BaseInput):
    """Input for listing entries in a Cache Storage cache."""

    cache_name: str = Field(..., min_length=1, description="Cache storage name")
    session_id: str = Field(..., description="Active session ID from wavexis_session_open")


class CacheStorageDeleteInput(BaseInput):
    """Input for deleting a Cache Storage cache."""

    cache_name: str = Field(..., min_length=1, description="Cache storage name")
    session_id: str = Field(..., description="Active session ID from wavexis_session_open")


class IndexedDBListInput(BaseInput):
    """Input for listing IndexedDB databases."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")


class IndexedDBGetDataInput(BaseInput):
    """Input for getting data from an IndexedDB object store."""

    database: str = Field(..., description="IndexedDB database name")
    store: str = Field(..., description="Object store name")
    key: str = Field(default="", description="Specific key (empty = all entries)")
    session_id: str = Field(..., description="Active session ID from wavexis_session_open")


class IndexedDBClearInput(BaseInput):
    """Input for clearing an IndexedDB object store."""

    database: str = Field(..., description="IndexedDB database name")
    store: str = Field(..., description="IndexedDB object store name")
    session_id: str = Field(..., description="Active session ID from wavexis_session_open")


class StorageStateSaveInput(BaseInput):
    """Input for saving browser state to a JSON file."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    output_path: str = Field(..., min_length=1, description="File path to save state JSON")


class StorageStateRestoreInput(BaseInput):
    """Input for restoring browser state from a JSON file."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    input_path: str = Field(..., min_length=1, description="Path to saved state JSON file")


# ── Emulation ───────────────────────────────────────────────────


class EmulateDeviceInput(BaseInput):
    """Input for emulating a specific device."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    device: str = Field(
        ...,
        description="Device preset: iphone-15, iphone-se, pixel-8, ipad-pro, "
        "galaxy-s23, desktop-1080p, desktop-1440p",
    )


class SetViewportInput(BaseInput):
    """Input for setting a custom viewport size."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    width: int = Field(..., ge=320, le=3840, description="Viewport width in pixels")
    height: int = Field(..., ge=240, le=2160, description="Viewport height in pixels")
    device_scale_factor: float = Field(
        default=1.0, ge=0.1, le=10.0, description="Device scale factor (DPR)"
    )


class SetGeolocationInput(BaseInput):
    """Input for overriding the browser geolocation."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    latitude: float = Field(..., ge=-90, le=90, description="Geolocation latitude")
    longitude: float = Field(..., ge=-180, le=180, description="Geolocation longitude")
    accuracy: float = Field(default=100.0, ge=0, description="Geolocation accuracy in meters")


class SetTimezoneInput(BaseInput):
    """Input for overriding the browser timezone."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    timezone: str = Field(..., description="IANA timezone ID (e.g. 'America/New_York')")


class SetDarkModeInput(BaseInput):
    """Input for enabling or disabling dark mode emulation."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    enabled: bool = Field(default=True, description="Whether the feature is enabled")


class SetLocaleInput(BaseInput):
    """Input for overriding the browser locale."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    locale: str = Field(..., description="Locale code (e.g. 'en-US', 'fr-FR', 'ja-JP')")


class SetCPUThrottleInput(BaseInput):
    """Input for enabling CPU throttling."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    rate: float = Field(
        ..., ge=1.0, le=20.0, description="CPU throttle multiplier (e.g. 4 = 4x slower)"
    )


class SetTouchEmulationInput(BaseInput):
    """Input for enabling or disabling touch emulation."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    enabled: bool = Field(default=True, description="Whether the feature is enabled")


class SetSensorsInput(BaseInput):
    """Input for overriding sensor values."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    sensor_type: str = Field(
        ..., description="Sensor type: 'orientation', 'motion', 'light', 'proximity'"
    )
    values: dict[str, float] = Field(
        ..., description="Sensor values (e.g. {'alpha': 0, 'beta': 90, 'gamma': 0})"
    )


# ── A11y ────────────────────────────────────────────────────────


class A11ySnapshotInput(BaseInput):
    """Input for capturing the full accessibility tree."""

    session_id: str | None = Field(
        default=None,
        description="Active session ID. If omitted, a stateless session is created for this call.",
    )
    url: str | None = Field(
        default=None, description="URL to navigate to first (required without session)"
    )
    wait_timeout: int = Field(
        default=30000, ge=1000, le=300000, description="Timeout in ms for wait conditions"
    )
    headless: bool = Field(default=True, description="Run browser in headless mode")
    backend: Literal["cdp", "bidi", "auto"] = Field(
        default="cdp", description="Backend: 'cdp', 'bidi', or 'auto'"
    )


class A11yNodeInput(BaseInput):
    """Input for getting a specific accessibility node."""

    node_id: str = Field(..., description="Node ID from a11y_snapshot")
    session_id: str = Field(..., description="Active session ID from wavexis_session_open")


class A11yAncestorsInput(BaseInput):
    """Input for getting the ancestor chain of a node."""

    node_id: str = Field(..., description="DOM node ID")
    session_id: str = Field(..., description="Active session ID from wavexis_session_open")


# ── Interactions ────────────────────────────────────────────────


class DialogAcceptInput(BaseInput):
    """Input for accepting a JavaScript dialog."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    prompt_text: str | None = Field(default=None, description="Text for prompt dialogs")


class DialogDismissInput(BaseInput):
    """Input for dismissing a JavaScript dialog."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")


class InterceptDownloadInput(BaseInput):
    """Input for intercepting a download."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    pattern: str = Field(default=".*", description="URL pattern to match")
    output_path: str | None = Field(
        default=None, description="Save to file instead of returning base64"
    )


class GrantPermissionInput(BaseInput):
    """Input for granting a browser permission."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    permission: str = Field(
        ...,
        description="Permission name: geolocation, notifications, camera, microphone, etc.",
    )


class ResetPermissionsInput(BaseInput):
    """Input for resetting all granted permissions."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")


# ── DevTools — Performance ──────────────────────────────────────


class PerfMetricsInput(BaseInput):
    """Input for getting performance metrics."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")


class PerfTraceInput(BaseInput):
    """Input for capturing a performance trace."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    duration_ms: int = Field(default=3000, ge=500, le=30000, description="Duration in ms")
    output_path: str | None = Field(
        default=None,
        description="File path to save the output. If omitted, a default path is used.",
    )


class PerfProfileInput(BaseInput):
    """Input for capturing a CPU profile."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    duration_ms: int = Field(default=3000, ge=500, le=30000, description="Duration in ms")
    output_path: str | None = Field(
        default=None,
        description="File path to save the output. If omitted, a default path is used.",
    )


class PerfHeapSnapshotInput(BaseInput):
    """Input for capturing a heap snapshot."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    output_path: str | None = Field(
        default=None,
        description="File path to save the output. If omitted, a default path is used.",
    )


class PerfCoverageInput(BaseInput):
    """Input for getting JavaScript code coverage."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")


class PerfCSSCoverageInput(BaseInput):
    """Input for getting CSS code coverage."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")


# ── DevTools — CSS ──────────────────────────────────────────────


class CSSGetStylesInput(BaseInput):
    """Input for getting inline and matched CSS styles."""

    selector: SelectorStr = Field(..., description="CSS selector for the target element")
    session_id: str = Field(..., description="Active session ID from wavexis_session_open")


class CSSGetStylesheetsInput(BaseInput):
    """Input for listing all stylesheets."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")


class CSSGetRulesInput(BaseInput):
    """Input for getting CSS rules from a stylesheet."""

    stylesheet_id: str = Field(..., description="CSS stylesheet ID")
    session_id: str = Field(..., description="Active session ID from wavexis_session_open")


class CSSGetComputedInput(BaseInput):
    """Input for getting computed styles for an element."""

    selector: SelectorStr = Field(..., description="CSS selector for the target element")
    session_id: str = Field(..., description="Active session ID from wavexis_session_open")


# ── DevTools — Debugging ────────────────────────────────────────


class DebugSetBreakpointInput(BaseInput):
    """Input for setting a breakpoint by URL and line."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    url: str = Field(..., description="URL of the script")
    line: int = Field(..., ge=0, description="Line number (0-based)")
    condition: str | None = Field(default=None, description="Optional condition expression")


class DebugSetBreakpointFunctionInput(BaseInput):
    """Input for setting a breakpoint by function name."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    function_name: str = Field(..., description="JavaScript function name to set breakpoint on")


class DebugRemoveBreakpointInput(BaseInput):
    """Input for removing a breakpoint by ID."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    breakpoint_id: str = Field(..., description="Breakpoint ID to remove")


class DebugStepInput(BaseInput):
    """Input for debugger step actions (over, into, out)."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")


class DebugPauseInput(BaseInput):
    """Input for pausing or resuming script execution."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")


class DebugGetListenersInput(BaseInput):
    """Input for getting event listeners on an element."""

    selector: SelectorStr = Field(..., description="CSS selector for the target element")
    session_id: str = Field(..., description="Active session ID from wavexis_session_open")


# ── DevTools — Overlay ──────────────────────────────────────────


class OverlayHighlightInput(BaseInput):
    """Input for highlighting an element with a colored overlay."""

    selector: SelectorStr = Field(..., description="CSS selector for the target element")
    color: str = Field(default="rgba(255,0,0,0.5)", description="RGBA color string")
    session_id: str = Field(..., description="Active session ID from wavexis_session_open")


class OverlayClearInput(BaseInput):
    """Input for clearing all overlay highlights."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")


# ── DevTools — Console & Logs ───────────────────────────────────


class ConsoleMessagesInput(BaseInput):
    """Input for getting console messages with pagination."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    level: str = Field(default="info", description="Minimum level: error, warning, info, debug")
    all: bool = Field(
        default=False,
        description="Return all messages since session start, not just last navigation",
    )
    limit: int = Field(default=100, ge=1, le=1000, description="Max messages to return")
    offset: int = Field(default=0, ge=0, description="Skip first N messages for pagination")


class BrowserLogsInput(BaseInput):
    """Input for getting browser-level log entries."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")


# ── DevTools — Security ─────────────────────────────────────────


class GetSecurityStateInput(BaseInput):
    """Input for getting the page security state."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")


class IgnoreCertErrorsInput(BaseInput):
    """Input for enabling or disabling certificate error ignoring."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    ignore: bool = Field(default=True, description="Whether to ignore cache")


# ── DevTools — Window ───────────────────────────────────────────


class GetWindowBoundsInput(BaseInput):
    """Input for getting the browser window bounds."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")


class SetWindowBoundsInput(BaseInput):
    """Input for setting the browser window bounds."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    width: int = Field(..., ge=320, le=3840, description="Viewport width in pixels")
    height: int = Field(..., ge=240, le=2160, description="Viewport height in pixels")
    x: int = Field(default=0, description="X coordinate")
    y: int = Field(default=0, description="Y coordinate")


# ── Vision ───────────────────────────────────────────────────────


class MouseMoveInput(BaseInput):
    """Input for moving the mouse to an element by CSS selector."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    selector: SelectorStr = Field(..., description="CSS selector for the target element")


class MouseMoveXYInput(BaseInput):
    """Input for moving the mouse to absolute pixel coordinates."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    x: int = Field(..., description="X coordinate in CSS pixels")
    y: int = Field(..., description="Y coordinate in CSS pixels")


class MouseDownInput(BaseInput):
    """Input for pressing a mouse button at coordinates."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    button: Literal["left", "right", "middle"] = Field(
        default="left", description="Mouse button: left, right, or middle"
    )
    x: int = Field(default=0, description="X coordinate")
    y: int = Field(default=0, description="Y coordinate")


class MouseUpInput(BaseInput):
    """Input for releasing a mouse button at coordinates."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    button: Literal["left", "right", "middle"] = Field(
        default="left", description="Mouse button: left, right, or middle"
    )
    x: int = Field(default=0, description="X coordinate")
    y: int = Field(default=0, description="Y coordinate")


class MouseClickXYInput(BaseInput):
    """Input for clicking at absolute pixel coordinates."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    x: int = Field(..., description="X coordinate")
    y: int = Field(..., description="Y coordinate")
    button: Literal["left", "right", "middle"] = Field(
        default="left", description="Mouse button: left, right, or middle"
    )
    click_count: int = Field(default=1, ge=1, le=10, description="Number of clicks to perform")


class MouseDoubleClickXYInput(BaseInput):
    """Input for double-clicking at absolute pixel coordinates."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    x: int = Field(..., description="X coordinate")
    y: int = Field(..., description="Y coordinate")
    button: Literal["left", "right", "middle"] = Field(
        default="left", description="Mouse button: left, right, or middle"
    )


class MouseWheelInput(BaseInput):
    """Input for simulating a mouse wheel event at coordinates."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    x: int = Field(default=0, description="X coordinate of the wheel event")
    y: int = Field(default=0, description="Y coordinate of the wheel event")
    delta_x: int = Field(default=0, description="Horizontal scroll amount")
    delta_y: int = Field(default=0, description="Vertical scroll amount")


# ── Video ────────────────────────────────────────────────────────


class VideoRecordInput(BaseInput):
    """Input for starting video recording."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    output_path: str | None = Field(default=None, description="Output file path")
    width: int = Field(default=1280, description="Viewport width in pixels")
    height: int = Field(default=800, description="Viewport height in pixels")


class VideoStopInput(BaseInput):
    """Input for stopping video recording."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    output_path: str | None = Field(default=None, description="Output file path")


class VideoAddChapterInput(BaseInput):
    """Input for adding a chapter marker to a recording."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    recording_id: str = Field(..., description="Recording ID from video_record")
    title: str = Field(..., description="Chapter title")
    timestamp_ms: int | None = Field(default=None, description="Timestamp in ms")


class VideoActionOverlayInput(BaseInput):
    """Input for toggling action overlay on video."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    show: bool = Field(default=True, description="Whether to show the overlay")


# ── Testing ──────────────────────────────────────────────────────


class AssertVisibleInput(BaseInput):
    """Input for asserting element visibility."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    selector: SelectorStr = Field(..., description="CSS selector for the element")
    timeout: int = Field(default=5000, ge=100, le=30000, description="Timeout in ms")


class AssertTextVisibleInput(BaseInput):
    """Input for asserting text visibility on the page."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    text: str = Field(..., min_length=1, description="Text to search for")
    timeout: int = Field(default=5000, ge=100, le=30000, description="Timeout in ms")


class AssertValueInput(BaseInput):
    """Input for asserting the value of a form element."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    selector: SelectorStr = Field(..., description="CSS selector for the input element")
    value: str = Field(..., description="Expected value")
    timeout: int = Field(default=5000, ge=100, le=30000, description="Timeout in ms")


class AssertListInput(BaseInput):
    """Input for asserting all text items appear inside a list element."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    selector: SelectorStr = Field(..., description="CSS selector for the list element")
    items: list[str] = Field(..., min_length=1, description="Expected visible text items")
    timeout: int = Field(default=5000, ge=100, le=30000, description="Timeout in ms")


class AssertURLInput(BaseInput):
    """Input for asserting the current URL matches a pattern."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    url_pattern: str = Field(..., min_length=1, description="URL substring or pattern to match")


class GenerateLocatorInput(BaseInput):
    """Input for generating a robust CSS selector."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    selector: SelectorStr = Field(..., description="Approximate CSS selector")
    description: str | None = Field(default=None, description="Natural-language description")


# ── Workflows ────────────────────────────────────────────────────


class MultiActionInput(BaseInput):
    """Input for executing multiple actions from a YAML config."""

    config: str = Field(..., description="YAML config string (not file path)")
    session_id: str | None = Field(
        default=None,
        description="Active session ID. If omitted, a stateless session is created for this call.",
    )
    backend: Literal["cdp", "bidi", "auto"] = Field(
        default="cdp", description="Backend: 'cdp', 'bidi', or 'auto'"
    )
    headless: bool = Field(default=True, description="Run browser in headless mode")
    continue_on_error: bool = Field(default=False, description="Continue on action errors")


class RawCDPInput(BaseInput):
    """Input for sending a raw CDP command."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    method: str = Field(..., description="CDP method (e.g. 'Page.reload')")
    params: dict[str, Any] | None = Field(
        default=None, description="Parameters to pass to the CDP/BiDi method"
    )


class RawBiDiInput(BaseInput):
    """Input for sending a raw BiDi command."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    method: str = Field(..., description="BiDi command (e.g. 'browsingContext.navigate')")
    params: dict[str, Any] | None = Field(
        default=None, description="Parameters to pass to the CDP/BiDi method"
    )


class BrowserContextCreateInput(BaseInput):
    """Input for creating an isolated browser context."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")


class BrowserContextCloseInput(BaseInput):
    """Input for closing a browser context."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    context_id: str = Field(..., description="Execution context ID")


class BrowserContextListInput(BaseInput):
    """Input for listing browser contexts."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")


class InvokeInput(BaseInput):
    """Input for invoking any wavexis backend method by name.

    This is a generic escape hatch that exposes the hundreds of high-level
    methods available on ``AbstractBackend`` (e.g. ``page_print_to_pdf``,
    ``perf_trace``, ``runtime_evaluate``, ``pwa_install``, etc.) without
    requiring a dedicated MCP tool for each one.
    """

    method: str = Field(
        ...,
        min_length=1,
        description=(
            "Backend method name (snake_case), e.g. 'page_print_to_pdf' or 'runtime_evaluate'."
        ),
    )
    params: dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "Keyword arguments for the method. For methods that expect a "
            "single dataclass parameter (e.g. 'pdf'), pass the dataclass "
            "fields here as a JSON object."
        ),
    )
    session_id: str | None = Field(
        default=None,
        description=(
            "Existing session ID. If omitted, an ephemeral browser is "
            "launched and closed automatically."
        ),
    )
    url: str | None = Field(
        default=None, description="URL to navigate to before invoking the method."
    )
    output_path: str | None = Field(
        default=None,
        description="If the method returns bytes, save to this path instead of base64.",
    )
    backend: str = Field(
        default="cdp", description="Backend type for ephemeral sessions: 'cdp', 'bidi', or 'auto'."
    )
    headless: bool = Field(default=True, description="Run browser in headless mode")
    width: int = Field(default=1280, ge=320, le=3840, description="Viewport width in pixels")
    height: int = Field(default=800, ge=240, le=2160, description="Viewport height in pixels")
    user_agent: str | None = Field(default=None, description="Custom User-Agent string")
    extra_headers: dict[str, str] = Field(
        default_factory=dict, description="Extra HTTP headers to send"
    )
    proxy: str | None = Field(default=None, description="Proxy server URL (e.g. http://host:port)")
    timeout: int = Field(default=30000, ge=1000, le=300000, description="Operation timeout in ms")
    user_data_dir: str | None = Field(
        default=None, description="Persistent Chrome user data directory"
    )
    browser_url: str | None = Field(
        default=None, description="WebSocket URL of an existing browser (e.g. ws://localhost:9222)"
    )
    remote_url: str | None = Field(default=None, description="Cloud browser WebSocket URL")
    stealth: bool = Field(default=False, description="Enable anti-bot stealth mode")
    browser: Literal["chrome", "firefox"] = Field(
        default="chrome",
        description="Browser engine for BiDi backend: 'chrome' or 'firefox'.",
    )
    wait_strategy: _WaitStrategy = Field(
        default="load",
        description="Wait strategy: load, domcontentloaded, networkidle, selector, url, none",
    )
    wait_selector: str | None = Field(
        default=None, description="CSS selector to wait for (used when wait_strategy='selector')"
    )
    wait_timeout: int = Field(
        default=30000, ge=1000, le=300000, description="Timeout in ms for wait conditions"
    )


# ── Data ─────────────────────────────────────────────────────────


class RecordInput(BaseInput):
    """Input for recording browser interactions."""

    session_id: str | None = Field(
        default=None,
        description="Existing session ID to reuse; a new session is created if omitted",
    )
    url: str = Field(..., description="URL to navigate to for recording")
    duration: int = Field(default=60, ge=5, le=300, description="Recording duration in seconds")
    headless: bool = Field(default=False, description="Must be False for user interaction")
    backend: Literal["cdp", "bidi", "auto"] = Field(
        default="cdp", description="Backend: 'cdp', 'bidi', or 'auto'"
    )


class LighthouseInput(BaseInput):
    """Input for running a Lighthouse-style audit."""

    url: str = Field(..., description="URL to audit")
    categories: list[str] = Field(
        default_factory=list,
        description=(
            "Categories: 'performance', 'accessibility', 'seo', 'best-practices'. Empty = all."
        ),
    )
    session_id: str | None = Field(
        default=None,
        description="Active session ID. If omitted, a stateless session is created for this call.",
    )
    wait_timeout: int = Field(
        default=30000, ge=1000, le=300000, description="Timeout in ms for wait conditions"
    )
    headless: bool = Field(default=True, description="Run browser in headless mode")
    backend: Literal["cdp", "bidi", "auto"] = Field(
        default="cdp", description="Backend: 'cdp', 'bidi', or 'auto'"
    )


class ExtractInput(BaseInput):
    """Input for structured data extraction via CSS selector schema."""

    model_config = ConfigDict(populate_by_name=True)

    url: str = Field(..., description="URL to navigate to")
    json_schema: dict[str, str] = Field(
        ...,
        alias="schema",
        description='Mapping of field names to CSS selectors, e.g. {"title": "h1"}',
    )
    selector: str | None = Field(
        default=None, description="Optional scoping selector for repeating elements"
    )
    session_id: str | None = Field(
        default=None,
        description="Active session ID. If omitted, a stateless session is created for this call.",
    )
    wait_timeout: int = Field(
        default=30000, ge=1000, le=300000, description="Timeout in ms for wait conditions"
    )
    headless: bool = Field(default=True, description="Run browser in headless mode")
    backend: Literal["cdp", "bidi", "auto"] = Field(
        default="cdp", description="Backend: 'cdp', 'bidi', or 'auto'"
    )


class WebsocketInterceptInput(BaseInput):
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
    session_id: str | None = Field(
        default=None,
        description="Active session ID. If omitted, a stateless session is created for this call.",
    )
    wait_timeout: int = Field(
        default=30000, ge=1000, le=300000, description="Timeout in ms for wait conditions"
    )
    headless: bool = Field(default=True, description="Run browser in headless mode")
    backend: Literal["cdp", "bidi", "auto"] = Field(
        default="cdp", description="Backend: 'cdp', 'bidi', or 'auto'"
    )


class CrawlInput(BaseInput):
    """Input for crawling a website."""

    start_url: str = Field(..., description="Starting URL for the crawl")
    max_depth: int = Field(default=2, ge=1, le=10, description="Maximum crawl depth")
    max_pages: int = Field(default=50, ge=1, le=500, description="Maximum pages to visit")
    same_origin: bool = Field(default=True, description="Only crawl same-origin links")
    url_pattern: str = Field(default="", description="Regex pattern to filter URLs (empty = all)")
    session_id: str | None = Field(
        default=None,
        description="Active session ID. If omitted, a stateless session is created for this call.",
    )
    wait_timeout: int = Field(
        default=30000, ge=1000, le=300000, description="Timeout in ms for wait conditions"
    )
    headless: bool = Field(default=True, description="Run browser in headless mode")
    backend: Literal["cdp", "bidi", "auto"] = Field(
        default="cdp", description="Backend: 'cdp', 'bidi', or 'auto'"
    )


class VisualDiffInput(BaseInput):
    """Input for visual regression comparison."""

    url: str = Field(..., description="URL to navigate to")
    baseline_path: str = Field(..., min_length=1, description="Path to baseline screenshot file")
    selector: str | None = Field(
        default=None,
        description="CSS selector — compare only this element",
    )
    threshold: float = Field(default=0.1, ge=0.0, le=1.0, description="Pixel difference threshold")
    output_path: str | None = Field(default=None, description="Save diff image to this path")
    session_id: str | None = Field(
        default=None,
        description="Active session ID. If omitted, a stateless session is created for this call.",
    )
    wait_timeout: int = Field(
        default=30000, ge=1000, le=300000, description="Timeout in ms for wait conditions"
    )
    headless: bool = Field(default=True, description="Run browser in headless mode")
    backend: Literal["cdp", "bidi", "auto"] = Field(
        default="cdp", description="Backend: 'cdp', 'bidi', or 'auto'"
    )


# ── Experimental ─────────────────────────────────────────────────


class ServiceWorkerListInput(BaseInput):
    """Input for listing service workers."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")


class ServiceWorkerUnregisterInput(BaseInput):
    """Input for unregistering a service worker."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    registration_id: str = Field(..., description="Service worker registration ID")


class ServiceWorkerUpdateInput(BaseInput):
    """Input for triggering a service worker update."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    registration_id: str = Field(..., description="Service worker registration ID")


class ServiceWorkerEmulateInput(BaseInput):
    """Input for emulating a service worker."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    script_url: str = Field(..., description="Script URL for the emulated service worker")


class AnimationListInput(BaseInput):
    """Input for listing active animations."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")


class AnimationPlayInput(BaseInput):
    """Input for playing/resuming an animation."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    animation_id: str = Field(..., description="Animation ID")


class AnimationPauseInput(BaseInput):
    """Input for pausing an animation."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    animation_id: str = Field(..., description="Animation ID")


class AnimationSetRateInput(BaseInput):
    """Input for setting animation playback rate."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    animation_id: str = Field(..., description="Animation ID")
    playback_rate: float = Field(default=1.0, ge=0.0, description="Playback rate multiplier")


class WebAuthnAddAuthenticatorInput(BaseInput):
    """Input for adding a virtual WebAuthn authenticator."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    protocol: str = Field(
        default="ctap2",
        description="Authenticator protocol: 'ctap2' or 'u2f'",
    )
    transport: str = Field(
        default="usb",
        description="Transport type: 'usb', 'nfc', 'ble', 'internal'",
    )


class WebAuthnAddCredentialInput(BaseInput):
    """Input for adding a WebAuthn credential."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    authenticator_id: str = Field(..., description="WebAuthn authenticator ID")
    credential: dict[str, Any] = Field(..., description="WebAuthn credential to add")


class WebAuthnGetCredentialInput(BaseInput):
    """Input for getting WebAuthn credentials."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    authenticator_id: str = Field(..., description="WebAuthn authenticator ID")


class WebAuthnRemoveCredentialInput(BaseInput):
    """Input for removing a WebAuthn authenticator."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    authenticator_id: str = Field(..., description="WebAuthn authenticator ID")


class WebAudioCaptureInput(BaseInput):
    """Input for capturing WebAudio context data."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    context_id: str | None = Field(default=None, description="Specific context ID (empty = all)")


class WebAudioStopCaptureInput(BaseInput):
    """Input for stopping WebAudio capture."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")


class MediaGetPlayersInput(BaseInput):
    """Input for listing media players."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")


class MediaGetMessagesInput(BaseInput):
    """Input for getting messages from a media player."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    player_id: str = Field(..., description="Media player ID")


class MediaPlayerPlayInput(BaseInput):
    """Input for playing a media player."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    player_id: str = Field(..., description="Media player ID")


class MediaPlayerPauseInput(BaseInput):
    """Input for pausing a media player."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    player_id: str = Field(..., description="Media player ID")


class MediaPlayerSeekInput(BaseInput):
    """Input for seeking a media player."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    player_id: str = Field(..., description="Media player ID")
    time_ms: int = Field(..., ge=0, description="Seek time in milliseconds")


class CastListInput(BaseInput):
    """Input for listing available cast sinks."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")


class CastStartInput(BaseInput):
    """Input for starting tab casting."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    sink_name: str = Field(..., min_length=1, description="Cast sink name")


class CastStopInput(BaseInput):
    """Input for stopping casting."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")


class BluetoothAdapterStateInput(BaseInput):
    """Input for setting Bluetooth adapter state."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    state: str = Field(..., description="Adapter state: 'powered-on' or 'powered-off'")


class BluetoothDeviceConnectInput(BaseInput):
    """Input for connecting a Bluetooth device."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    name: str = Field(..., min_length=1, description="Device name")
    address: str = Field(default="00:00:00:00:00:01", description="Device MAC address")


class BluetoothDeviceDisconnectInput(BaseInput):
    """Input for disconnecting Bluetooth emulation."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")


class BluetoothDeviceListInput(BaseInput):
    """Input for listing Bluetooth devices."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")


class GetRequestBodyInput(BaseInput):
    """Input for getting a network request body (W3)."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    request_id: str = Field(..., description="Network request ID")


class GetResponseBodyInput(BaseInput):
    """Input for getting a network response body (W3)."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    request_id: str = Field(..., description="Network request ID")


class ModifyRequestInput(BaseInput):
    """Input for modifying requests in-flight (W6)."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    pattern: dict[str, Any] = Field(
        ..., description="Interception pattern (urlPattern, resourceType, requestStage)"
    )
    modifications: dict[str, Any] = Field(
        default_factory=dict,
        description="Modifications: headers, url, method, post_data",
    )


class ModifyResponseInput(BaseInput):
    """Input for modifying responses in-flight."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    pattern: dict[str, Any] = Field(
        ..., description="Interception pattern (urlPattern, resourceType, requestStage)"
    )
    modifications: dict[str, Any] = Field(
        default_factory=dict,
        description="Modifications: status, headers, body",
    )


class ReplayHARInput(BaseInput):
    """Input for replaying HAR entries (W7)."""

    har_path: str = Field(..., min_length=1, description="Path to HAR file")
    url_filter: str = Field(default="", description="Optional URL filter pattern")
    session_id: str | None = Field(
        default=None,
        description="Active session ID. If omitted, a stateless session is created for this call.",
    )
    url: str = Field(default="", description="URL to navigate to before replay")
    headless: bool = Field(default=True, description="Run browser in headless mode")
    backend: Literal["cdp", "bidi", "auto"] = Field(
        default="cdp", description="Backend: 'cdp', 'bidi', or 'auto'"
    )


class StartCombinedTraceInput(BaseInput):
    """Input for starting a combined trace (W8)."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    capture_screenshots: bool = Field(
        default=True, description="Capture screenshots during the trace"
    )
    capture_network: bool = Field(
        default=True, description="Capture network activity during the trace"
    )
    capture_console: bool = Field(
        default=True, description="Capture console messages during the trace"
    )


class StopCombinedTraceInput(BaseInput):
    """Input for stopping a combined trace (W8)."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    trace_id: str = Field(..., description="Trace ID from start_combined_trace")


class CoreWebVitalsInput(BaseInput):
    """Input for measuring Core Web Vitals (LCP, CLS, INP)."""

    url: str = Field(..., description="URL to navigate to for measurement")
    session_id: str | None = Field(
        default=None,
        description="Active session ID. If omitted, a stateless session is created for this call.",
    )
    observe_ms: int = Field(
        default=5000, ge=1000, le=30000, description="Observation window in milliseconds"
    )
    budgets: dict[str, float] = Field(
        default_factory=dict,
        description="Optional budgets: lcp_ms, cls, inp_ms, fcp_ms, ttfb_ms, tbt_ms, load_ms",
    )
    headless: bool = Field(default=True, description="Run browser in headless mode")
    backend: Literal["cdp", "bidi", "auto"] = Field(
        default="cdp", description="Backend: 'cdp', 'bidi', or 'auto'"
    )


class AxeAuditInput(BaseInput):
    """Input for running axe-core accessibility audit (W9)."""

    session_id: str | None = Field(
        default=None,
        description="Active session ID. If omitted, a stateless session is created for this call.",
    )
    url: str = Field(default="", description="URL to navigate to before audit")
    headless: bool = Field(default=True, description="Run browser in headless mode")
    backend: Literal["cdp", "bidi", "auto"] = Field(
        default="cdp", description="Backend: 'cdp', 'bidi', or 'auto'"
    )


class ActInput(BaseInput):
    """Input for natural language interaction (M1)."""

    instruction: str = Field(
        ...,
        min_length=1,
        description="Natural language instruction (e.g. 'click the login button')",
    )
    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    max_retries: int = Field(default=3, ge=1, le=10, description="Maximum number of retry attempts")
    value: str | None = Field(
        default=None,
        description="Explicit text value for type/fill actions (overrides auto-extraction)",
    )


# ── Annotated screenshot ────────────────────────────────────────


class AnnotatedScreenshotInput(BaseInput):
    """Input for taking a screenshot with numbered labels on elements."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    selectors: list[str] = Field(
        ..., min_length=1, description="CSS selectors to annotate with labels"
    )
    format: str = Field(default="png", description="Image format: 'png' or 'jpeg'")
    output_path: str | None = Field(
        default=None,
        description="File path to save the output. If omitted, a default path is used.",
    )


# ── iframe ──────────────────────────────────────────────────────


class IframeEvalInput(BaseInput):
    """Input for evaluating JS inside an iframe."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    iframe_selector: SelectorStr = Field(..., description="CSS selector for the <iframe> element")
    expression: str = Field(..., description="JavaScript expression to evaluate")
    await_promise: bool = Field(default=False, description="Whether to await the returned promise")


class IframeClickInput(BaseInput):
    """Input for clicking an element inside an iframe."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    iframe_selector: SelectorStr = Field(..., description="CSS selector for the <iframe> element")
    selector: SelectorStr = Field(..., description="CSS selector inside the iframe")


class IframeFillInput(BaseInput):
    """Input for filling an input inside an iframe."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    iframe_selector: SelectorStr = Field(..., description="CSS selector for the <iframe> element")
    selector: SelectorStr = Field(..., description="CSS selector inside the iframe")
    value: str = Field(..., description="Value to set in the input field")


# ── Shadow DOM ──────────────────────────────────────────────────


class ShadowEvalInput(BaseInput):
    """Input for evaluating JS inside a shadow DOM tree."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    selectors: list[str] = Field(
        ...,
        min_length=1,
        description="CSS selectors piercing shadow boundaries (selectors[0] in document, "
        "selectors[1] in selectors[0].shadowRoot, etc.)",
    )
    expression: str = Field(..., description="JavaScript expression to evaluate")
    await_promise: bool = Field(default=False, description="Whether to await the returned promise")


class ShadowClickInput(BaseInput):
    """Input for clicking an element inside a shadow DOM tree."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    selectors: list[str] = Field(
        ...,
        min_length=1,
        description="CSS selectors piercing shadow boundaries",
    )


class ShadowFillInput(BaseInput):
    """Input for filling an input inside a shadow DOM tree."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    selectors: list[str] = Field(
        ...,
        min_length=1,
        description="CSS selectors piercing shadow boundaries",
    )
    value: str = Field(..., description="Value to set in the input field")


# ── Event subscription (W10) ────────────────────────────────────


class SubscribeEventsInput(BaseInput):
    """Input for subscribing to real-time browser events (W10)."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    event_types: list[str] = Field(
        ...,
        min_length=1,
        description="Event types: 'console', 'network_request', 'network_response', "
        "'dom_mutation', 'dialog', 'navigation'",
    )


class UnsubscribeEventsInput(BaseInput):
    """Input for unsubscribing from browser events (W10)."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    subscription_id: str = Field(..., description="Subscription ID from subscribe_events")


# ── WebExtensions ───────────────────────────────────────────────


class ExtensionInstallInput(BaseInput):
    """Input for installing a browser extension."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    path: str = Field(
        ..., min_length=1, description="Path to .crx file or unpacked extension directory"
    )


class ExtensionUninstallInput(BaseInput):
    """Input for uninstalling a browser extension."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    extension_id: str = Field(..., description="Extension ID returned by extension_install")


class ExtensionListInput(BaseInput):
    """Input for listing installed browser extensions."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")


# ── Browser preferences ─────────────────────────────────────────


class GetPrefInput(BaseInput):
    """Input for getting a browser preference value."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    key: str = Field(
        ..., min_length=1, description="Preference key (e.g. 'download.default_directory')"
    )


class SetPrefInput(BaseInput):
    """Input for setting a browser preference value."""

    session_id: str = Field(..., description="Active session ID from wavexis_session_open")
    key: str = Field(..., min_length=1, description="Preference key")
    value: str = Field(..., description="Preference value to set")
