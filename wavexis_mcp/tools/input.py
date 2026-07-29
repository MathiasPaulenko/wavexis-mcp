"""Input interaction tools for WaveXisMCP.

Provides click, type, fill, fill_form, select_option, hover,
key_press, drag, tap, set_files, check, and uncheck tools.
"""

from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from wavexis_mcp.convenience import fill_form_composite
from wavexis_mcp.formatter import (
    format_error,
    format_json_response,
    secure_output_path,
    validate_url,
)
from wavexis_mcp.models import (
    CheckInput,
    ClickInput,
    DoubleClickInput,
    DragInput,
    DropInput,
    FillFormInput,
    FillInput,
    FindByTextInput,
    HoverInput,
    KeyPressInput,
    NLClickInput,
    NLFillInput,
    RightClickInput,
    SelectOptionInput,
    SetFilesInput,
    TapInput,
    TypeInput,
)
from wavexis_mcp.session import SessionManager

_logger = logging.getLogger(__name__)

_MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MiB per file
_MAX_TOTAL_FILE_SIZE = 500 * 1024 * 1024  # 500 MiB total

# Stale element retry configuration.
_STALE_RETRY_COUNT = 2
_STALE_RETRY_DELAY_S = 0.1

# Keywords that indicate a stale element error from the backend.
_STALE_KEYWORDS = frozenset(
    {"stale", "not attached", "element not found", "node not found", "detached"}
)


def _is_stale_error(exc: Exception) -> bool:
    """Check if *exc* is a stale-element or detached-element error."""
    msg = str(exc).lower()
    return any(kw in msg for kw in _STALE_KEYWORDS)


async def _with_retry(coro_factory: Any, *, retries: int = _STALE_RETRY_COUNT) -> Any:
    """Execute a coroutine with auto-retry on stale element errors.

    Args:
        coro_factory: A zero-argument callable that returns a new coroutine
            each call (so retries get a fresh attempt).
        retries: Maximum number of retries on stale errors.

    Returns:
        The result of the coroutine.

    Raises:
        The last exception if all retries are exhausted or the error is not stale.
    """
    last_exc: Exception | None = None
    for attempt in range(retries + 1):
        try:
            return await coro_factory()
        except Exception as exc:
            last_exc = exc
            if not _is_stale_error(exc) or attempt >= retries:
                raise
            _logger.debug(
                "Stale element detected (attempt %d/%d), retrying in %.2fs",
                attempt + 1,
                retries + 1,
                _STALE_RETRY_DELAY_S,
            )
            await asyncio.sleep(_STALE_RETRY_DELAY_S)
    if last_exc is not None:
        raise last_exc  # pragma: no cover — unreachable


def _validate_files(paths: list[str]) -> list[Path]:
    """Validate and return resolved file paths with size limits.

    Args:
        paths: Caller-supplied file paths.

    Returns:
        List of resolved ``Path`` objects.

    Raises:
        ValueError: If a file exceeds the per-file limit or the total
            size exceeds the aggregate limit.
    """
    resolved: list[Path] = []
    total = 0
    for p in paths:
        path = secure_output_path(p)
        try:
            size = path.stat().st_size
        except FileNotFoundError as exc:
            raise ValueError(f"File not found: {p!r}") from exc
        except OSError as exc:
            raise ValueError(f"Cannot read file {p!r}: {exc}") from exc
        if size > _MAX_FILE_SIZE:
            raise ValueError(f"File {p!r} exceeds {_MAX_FILE_SIZE} bytes")
        total += size
        if total > _MAX_TOTAL_FILE_SIZE:
            raise ValueError("Total file size exceeds the maximum allowed")
        resolved.append(path)
    return resolved


def register(mcp: FastMCP, session_manager: SessionManager) -> None:
    """Register all input tools on the FastMCP server.

    Args:
        mcp: The FastMCP server instance.
        session_manager: The shared session manager.
    """

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=True,
            idempotentHint=False,
            openWorldHint=True,
        )
    )
    async def wavexis_click(input: ClickInput) -> str:
        """Click an element matching a CSS selector.

        Use wavexis_double_click for double clicks, wavexis_right_click for
        context menus, or wavexis_nl_click when you only have a text description.

        Side effects: Triggers a click event on the target element, which may
        submit forms, toggle controls, or navigate the page.
        Returns: JSON string with keys: 'status' ('ok'/'error'). On error also
        'error', 'tool', 'type', 'message', 'suggestion' (all str).
        """
        try:
            backend, sid = await session_manager.acquire_backend(
                input.session_id,
                backend=input.backend,
                headless=input.headless,
            )
            try:
                if input.url:
                    wait = session_manager.make_wait(timeout=input.wait_timeout)
                    validate_url(input.url)
                    await backend.navigate(input.url, wait)
                await _with_retry(
                    lambda: backend.click(
                        input.selector,
                        button=input.button,
                        click_count=input.click_count,
                    )
                )
                return format_json_response({"status": "ok"})
            finally:
                await session_manager.release_backend(backend, sid)
        except Exception as e:
            return format_error("wavexis_click", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=True,
            idempotentHint=False,
            openWorldHint=True,
        )
    )
    async def wavexis_double_click(input: DoubleClickInput) -> str:
        """Double-click an element matching a CSS selector.

        Use wavexis_click for single clicks or wavexis_nl_click when you only
        have a natural language description of the element.

        Side effects: Fires two rapid click events on the element, which may
        open files, edit cells, or trigger application-specific actions.
        Returns: JSON string with keys: 'status' ('ok'/'error'). On error also
        'error', 'tool', 'type', 'message', 'suggestion' (all str).
        """
        try:
            backend, sid = await session_manager.acquire_backend(
                input.session_id,
                backend=input.backend,
                headless=input.headless,
            )
            try:
                if input.url:
                    wait = session_manager.make_wait(timeout=input.wait_timeout)
                    validate_url(input.url)
                    await backend.navigate(input.url, wait)
                await _with_retry(
                    lambda: backend.double_click(input.selector, auto_wait=input.auto_wait)
                )
                return format_json_response({"status": "ok"})
            finally:
                await session_manager.release_backend(backend, sid)
        except Exception as e:
            return format_error("wavexis_double_click", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=True,
            idempotentHint=False,
            openWorldHint=True,
        )
    )
    async def wavexis_right_click(input: RightClickInput) -> str:
        """Right-click an element matching a CSS selector.

        Use wavexis_click for standard left clicks or wavexis_double_click for
        double clicks.

        Side effects: Fires a contextmenu event on the element, typically
        opening a context menu in the browser.
        Returns: JSON string with keys: 'status' ('ok'/'error'). On error also
        'error', 'tool', 'type', 'message', 'suggestion' (all str).
        """
        try:
            backend, sid = await session_manager.acquire_backend(
                input.session_id,
                backend=input.backend,
                headless=input.headless,
            )
            try:
                if input.url:
                    wait = session_manager.make_wait(timeout=input.wait_timeout)
                    validate_url(input.url)
                    await backend.navigate(input.url, wait)
                await backend.right_click(input.selector, auto_wait=input.auto_wait)
                return format_json_response({"status": "ok"})
            finally:
                await session_manager.release_backend(backend, sid)
        except Exception as e:
            return format_error("wavexis_right_click", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=True,
            idempotentHint=False,
            openWorldHint=True,
        )
    )
    async def wavexis_type(input: TypeInput) -> str:
        """Type text into an element character by character with optional delay.

        Use wavexis_fill instead when you want to set a field's value instantly
        without per-keystroke delays, or wavexis_fill_form for multiple fields.

        Side effects: Appends characters to the target input/textarea element,
        firing keydown/keypress/input/keyup events per character.
        Returns: JSON string with keys: 'status' ('ok'/'error'). On error also
        'error', 'tool', 'type', 'message', 'suggestion' (all str).
        """
        try:
            backend, sid = await session_manager.acquire_backend(
                input.session_id,
                backend=input.backend,
                headless=input.headless,
            )
            try:
                if input.url:
                    wait = session_manager.make_wait(timeout=input.wait_timeout)
                    validate_url(input.url)
                    await backend.navigate(input.url, wait)
                await backend.type_text(input.selector, input.text, delay=input.delay)
                return format_json_response({"status": "ok"})
            finally:
                await session_manager.release_backend(backend, sid)
        except Exception as e:
            return format_error("wavexis_type", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=True,
            idempotentHint=False,
            openWorldHint=True,
        )
    )
    async def wavexis_fill(input: FillInput) -> str:
        """Fill an input element with a value, replacing existing content.

        Use wavexis_type for character-by-character typing with key events, or
        wavexis_fill_form when filling multiple fields in one call.

        Side effects: Clears the target input/textarea and sets its value to
        the provided string, firing a single input event.
        Returns: JSON string with keys: 'status' ('ok'/'error'). On error also
        'error', 'tool', 'type', 'message', 'suggestion' (all str).
        """
        try:
            backend, sid = await session_manager.acquire_backend(
                input.session_id,
                backend=input.backend,
                headless=input.headless,
            )
            try:
                if input.url:
                    wait = session_manager.make_wait(timeout=input.wait_timeout)
                    validate_url(input.url)
                    await backend.navigate(input.url, wait)
                await _with_retry(lambda: backend.fill(input.selector, input.value))
                return format_json_response({"status": "ok"})
            finally:
                await session_manager.release_backend(backend, sid)
        except Exception as e:
            return format_error("wavexis_fill", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=True,
            idempotentHint=False,
            openWorldHint=True,
        )
    )
    async def wavexis_fill_form(input: FillFormInput) -> str:
        """Fill multiple form fields in one call (convenience composite tool).

        Use wavexis_fill for a single field or wavexis_type when per-keystroke
        events are required.

        Side effects: Clears and sets the value of each field in the provided
        list, firing input events on every targeted element.
        Returns: JSON string with keys: 'status' ('ok'/'error'), 'fields_filled'
        (int, number of fields successfully filled). On error also 'error',
        'tool', 'type', 'message', 'suggestion' (all str).
        """
        try:
            backend, sid = await session_manager.acquire_backend(
                input.session_id,
                backend=input.backend,
                headless=input.headless,
            )
            try:
                if input.url:
                    wait = session_manager.make_wait(timeout=input.wait_timeout)
                    validate_url(input.url)
                    await backend.navigate(input.url, wait)
                count = await fill_form_composite(backend, input.fields)
                return format_json_response({"status": "ok", "fields_filled": count})
            finally:
                await session_manager.release_backend(backend, sid)
        except Exception as e:
            return format_error("wavexis_fill_form", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=True,
            idempotentHint=False,
            openWorldHint=True,
        )
    )
    async def wavexis_select_option(input: SelectOptionInput) -> str:
        """Select an option in a ``<select>`` element by value.

        Use wavexis_fill for text inputs or wavexis_click for custom dropdown
        widgets that are not native ``<select>`` elements.

        Side effects: Changes the selected option of the ``<select>`` element,
        firing change and input events.
        Returns: JSON string with keys: 'status' ('ok'/'error'). On error also
        'error', 'tool', 'type', 'message', 'suggestion' (all str).
        """
        try:
            backend, sid = await session_manager.acquire_backend(
                input.session_id,
                backend=input.backend,
                headless=input.headless,
            )
            try:
                if input.url:
                    wait = session_manager.make_wait(timeout=input.wait_timeout)
                    validate_url(input.url)
                    await backend.navigate(input.url, wait)
                await _with_retry(lambda: backend.select_option(input.selector, input.value))
                return format_json_response({"status": "ok"})
            finally:
                await session_manager.release_backend(backend, sid)
        except Exception as e:
            return format_error("wavexis_select_option", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=True,
        )
    )
    async def wavexis_hover(input: HoverInput) -> str:
        """Hover over an element matching a CSS selector.

        Use wavexis_click to actually activate an element; hover only moves the
        cursor without clicking.

        Side effects: Moves the mouse cursor over the target element, firing
        mouseover/mouseenter events that may reveal tooltips or menus.
        Returns: JSON string with keys: 'status' ('ok'/'error'). On error also
        'error', 'tool', 'type', 'message', 'suggestion' (all str).
        """
        try:
            backend, sid = await session_manager.acquire_backend(
                input.session_id,
                backend=input.backend,
                headless=input.headless,
            )
            try:
                if input.url:
                    wait = session_manager.make_wait(timeout=input.wait_timeout)
                    validate_url(input.url)
                    await backend.navigate(input.url, wait)
                await _with_retry(lambda: backend.hover(input.selector))
                return format_json_response({"status": "ok"})
            finally:
                await session_manager.release_backend(backend, sid)
        except Exception as e:
            return format_error("wavexis_hover", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        )
    )
    async def wavexis_key_press(input: KeyPressInput) -> str:
        """Press a single keyboard key on the focused element.

        Use wavexis_type for typing full strings or wavexis_fill for setting
        field values without individual key events.

        Side effects: Dispatches a keydown/keypress/keyup sequence for the
        given key on whatever element currently has focus.
        Returns: JSON string with keys: 'status' ('ok'/'error'). On error also
        'error', 'tool', 'type', 'message', 'suggestion' (all str).
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.key_press(input.key)
            return format_json_response({"status": "ok"})
        except Exception as e:
            return format_error("wavexis_key_press", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=True,
            idempotentHint=False,
            openWorldHint=True,
        )
    )
    async def wavexis_drag(input: DragInput) -> str:
        """Drag an element from a source selector to a target selector.

        Use wavexis_drop when you need to drop arbitrary MIME data or files
        onto an element rather than dragging an existing DOM element.

        Side effects: Performs a drag-and-drop operation between two elements,
        firing drag/dragstart/dragend and drop events.
        Returns: JSON string with keys: 'status' ('ok'/'error'). On error also
        'error', 'tool', 'type', 'message', 'suggestion' (all str).
        """
        try:
            backend, sid = await session_manager.acquire_backend(
                input.session_id,
                backend=input.backend,
                headless=input.headless,
            )
            try:
                if input.url:
                    wait = session_manager.make_wait(timeout=input.wait_timeout)
                    validate_url(input.url)
                    await backend.navigate(input.url, wait)
                await backend.drag(input.source, input.target)
                return format_json_response({"status": "ok"})
            finally:
                await session_manager.release_backend(backend, sid)
        except Exception as e:
            return format_error("wavexis_drag", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=True,
        )
    )
    async def wavexis_tap(input: TapInput) -> str:
        """Tap an element matching a CSS selector (touch-emulated click).

        Use wavexis_click for mouse-based clicking on desktop contexts or
        wavexis_nl_click when you only have a natural language description.

        Side effects: Dispatches a touch tap on the target element, which may
        toggle controls or trigger navigation on mobile-optimised pages.
        Returns: JSON string with keys: 'status' ('ok'/'error'). On error also
        'error', 'tool', 'type', 'message', 'suggestion' (all str).
        """
        try:
            backend, sid = await session_manager.acquire_backend(
                input.session_id,
                backend=input.backend,
                headless=input.headless,
            )
            try:
                if input.url:
                    wait = session_manager.make_wait(timeout=input.wait_timeout)
                    validate_url(input.url)
                    await backend.navigate(input.url, wait)
                await _with_retry(lambda: backend.tap(input.selector))
                return format_json_response({"status": "ok"})
            finally:
                await session_manager.release_backend(backend, sid)
        except Exception as e:
            return format_error("wavexis_tap", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=True,
            idempotentHint=False,
            openWorldHint=True,
        )
    )
    async def wavexis_set_files(input: SetFilesInput) -> str:
        """Upload files to a file input element (``<input type="file">``).

        Use wavexis_drop when you need to simulate drag-and-drop of files or
        MIME data onto a non-file-input element.

        Side effects: Sets the selected files on the target file input element,
        firing change events that typically trigger upload logic.
        Returns: JSON string with keys: 'status' ('ok'/'error'). On error also
        'error', 'tool', 'type', 'message', 'suggestion' (all str).
        """
        try:
            backend, sid = await session_manager.acquire_backend(
                input.session_id,
                backend=input.backend,
                headless=input.headless,
            )
            try:
                if input.url:
                    wait = session_manager.make_wait(timeout=input.wait_timeout)
                    validate_url(input.url)
                    await backend.navigate(input.url, wait)
                validated_files = [str(p) for p in _validate_files(input.files)]
                await backend.set_files(input.selector, validated_files)
                return format_json_response({"status": "ok"})
            finally:
                await session_manager.release_backend(backend, sid)
        except Exception as e:
            return format_error("wavexis_set_files", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=True,
            idempotentHint=False,
            openWorldHint=True,
        )
    )
    async def wavexis_drop(input: DropInput) -> str:
        """Drop files or MIME-typed data onto an element via drag events.

        Use wavexis_set_files for standard ``<input type="file">`` uploads or
        wavexis_drag for dragging an existing DOM element to another element.

        Side effects: Dispatches dragEnter, dragOver, and drop events with the
        supplied data and files onto the target element's coordinates.
        Returns: JSON string with keys: 'status' ('ok'/'error'), 'selector'
        (str), 'x' (float), 'y' (float), 'data_types' (list[str]), 'files'
        (list[str]). On error also 'error', 'tool', 'type', 'message',
        'suggestion' (all str).
        """
        try:
            backend, sid = await session_manager.acquire_backend(
                input.session_id,
                backend=input.backend,
                headless=input.headless,
            )
            try:
                if input.url:
                    wait = session_manager.make_wait(timeout=input.wait_timeout)
                    validate_url(input.url)
                    await backend.navigate(input.url, wait)

                escaped = json.dumps(input.selector)
                js = (
                    f"(function(){{"
                    f"var el=document.querySelector({escaped});"
                    f"if(!el) return null;"
                    f"var r=el.getBoundingClientRect();"
                    f"return {{x:r.left+r.width/2,y:r.top+r.height/2}};"
                    f"}})()"
                )
                coords = await backend.eval(js)
                if not coords:
                    raise RuntimeError(f"Element not found for selector: {input.selector}")

                x, y = float(coords["x"]), float(coords["y"])

                items = [{"mimeType": mime, "data": data} for mime, data in input.data.items()]
                validated_paths = [str(p) for p in _validate_files(input.paths)]
                drag_data: dict[str, Any] = {
                    "dragOperationsMask": 7,
                    "items": items,
                    "files": validated_paths,
                }

                for event in ("dragEnter", "dragOver", "drop"):
                    await backend.input_dispatch_drag_event(event, x, y, drag_data)

                return format_json_response(
                    {
                        "status": "ok",
                        "selector": input.selector,
                        "x": x,
                        "y": y,
                        "data_types": list(input.data.keys()),
                        "files": validated_paths,
                    }
                )
            finally:
                await session_manager.release_backend(backend, sid)
        except Exception as e:
            return format_error("wavexis_drop", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=True,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def wavexis_check(input: CheckInput) -> str:
        """Check a checkbox or radio button matching a CSS selector.

        Use wavexis_uncheck to uncheck a checkbox or wavexis_click for generic
        element activation.

        Side effects: Clicks the target checkbox/radio, toggling its checked
        state and firing change events.
        Returns: JSON string with keys: 'status' ('ok'/'error'), 'checked'
        (bool, the element's checked state after the action). On error also
        'error', 'tool', 'type', 'message', 'suggestion' (all str).
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.click(input.selector)
            checked = await session.backend.eval(
                f"document.querySelector({json.dumps(input.selector)})?.checked"
            )
            return format_json_response({"status": "ok", "checked": bool(checked)})
        except Exception as e:
            return format_error("wavexis_check", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=True,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def wavexis_uncheck(input: CheckInput) -> str:
        """Uncheck a checkbox matching a CSS selector by clicking it.

        Use wavexis_check to check a checkbox or wavexis_click for generic
        element activation.

        Side effects: Clicks the target checkbox to toggle it to unchecked,
        firing change events.
        Returns: JSON string with keys: 'status' ('ok'/'error'). On error also
        'error', 'tool', 'type', 'message', 'suggestion' (all str).
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.click(input.selector)
            return format_json_response({"status": "ok"})
        except Exception as e:
            return format_error("wavexis_uncheck", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=True,
        )
    )
    async def wavexis_find_by_text(input: FindByTextInput) -> str:
        """Find element selector(s) by visible text content without interacting.

        Use this to locate elements before calling wavexis_click or wavexis_fill
        when you know the visible text but not the CSS selector.

        Side effects: None — this is a read-only lookup that does not modify the
        page or interact with any element.
        Returns: JSON string with keys: 'selector' (str, first match) when
        all=False, or 'selectors' (list[str]) and 'count' (int) when all=True.
        On error also 'error', 'tool', 'type', 'message', 'suggestion' (all str).
        """
        try:
            session = session_manager.get(input.session_id)
            result = await session.backend.find_by_text(input.query, all=input.all)
            if isinstance(result, list):
                return format_json_response({"selectors": result, "count": len(result)})
            return format_json_response({"selector": result})
        except Exception as e:
            return format_error("wavexis_find_by_text", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=True,
            idempotentHint=False,
            openWorldHint=True,
        )
    )
    async def wavexis_nl_click(input: NLClickInput) -> str:
        """Click an element described in natural language.

        Use wavexis_click when you already know the CSS selector, or
        wavexis_nl_fill to fill a field described in natural language.

        Side effects: Locates the best-matching element via text/semantic
        matching and triggers a click event on it.
        Returns: JSON string with keys: 'status' ('ok'/'error'). On error also
        'error', 'tool', 'type', 'message', 'suggestion' (all str).
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.nl_click(input.query, auto_wait=input.auto_wait)
            return format_json_response({"status": "ok"})
        except Exception as e:
            return format_error("wavexis_nl_click", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=True,
            idempotentHint=False,
            openWorldHint=True,
        )
    )
    async def wavexis_nl_fill(input: NLFillInput) -> str:
        """Fill an element described in natural language with a value.

        Use wavexis_fill when you already know the CSS selector, or
        wavexis_nl_click to click an element described in natural language.

        Side effects: Locates the best-matching element via text/semantic
        matching, clears it, and sets its value to the provided string.
        Returns: JSON string with keys: 'status' ('ok'/'error'). On error also
        'error', 'tool', 'type', 'message', 'suggestion' (all str).
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.nl_fill(input.query, input.value, auto_wait=input.auto_wait)
            return format_json_response({"status": "ok"})
        except Exception as e:
            return format_error("wavexis_nl_fill", e)
