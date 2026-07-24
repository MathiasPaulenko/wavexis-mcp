"""Input interaction tools for WaveXisMCP.

Provides click, type, fill, fill_form, select_option, hover,
key_press, drag, tap, set_files, check, and uncheck tools.
"""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from wavexis_mcp.convenience import fill_form_composite
from wavexis_mcp.formatter import format_error, format_json_response
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

        Args:
            input: Click parameters (selector, button, count).

        Returns:
            JSON string with status ``"ok"``.
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
                    await backend.navigate(input.url, wait)
                await backend.click(
                    input.selector,
                    button=input.button,
                    click_count=input.click_count,
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

        Args:
            input: Double-click parameters (selector, session, URL).

        Returns:
            JSON string with status ``"ok"``.
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
                    await backend.navigate(input.url, wait)
                await backend.double_click(input.selector, auto_wait=input.auto_wait)
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

        Args:
            input: Right-click parameters (selector, session, URL).

        Returns:
            JSON string with status ``"ok"``.
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
        """Type text into an element character by character.

        Args:
            input: Type parameters (selector, text, delay).

        Returns:
            JSON string with status ``"ok"``.
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
        """Fill an input element with a value (replaces existing content).

        Args:
            input: Fill parameters (selector, value).

        Returns:
            JSON string with status ``"ok"``.
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
                    await backend.navigate(input.url, wait)
                await backend.fill(input.selector, input.value)
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
        """Fill multiple form fields in one call (convenience tool).

        Args:
            input: Form fill parameters (fields list).

        Returns:
            JSON string with status ``"ok"`` and ``fields_filled`` count.
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

        Args:
            input: Select parameters (selector, value).

        Returns:
            JSON string with status ``"ok"``.
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
                    await backend.navigate(input.url, wait)
                await backend.select_option(input.selector, input.value)
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

        Args:
            input: Hover parameters.

        Returns:
            JSON string with status ``"ok"``.
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
                    await backend.navigate(input.url, wait)
                await backend.hover(input.selector)
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
        """Press a keyboard key.

        Args:
            input: Key press parameters.

        Returns:
            JSON string with status ``"ok"``.
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
        """Drag an element from source selector to target selector.

        Args:
            input: Drag parameters (source, target).

        Returns:
            JSON string with status ``"ok"``.
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
        """Tap an element (touch emulation click).

        Args:
            input: Tap parameters.

        Returns:
            JSON string with status ``"ok"``.
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
                    await backend.navigate(input.url, wait)
                await backend.tap(input.selector)
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
        """Upload files to a file input element.

        Args:
            input: File upload parameters (selector, file paths).

        Returns:
            JSON string with status ``"ok"``.
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
                    await backend.navigate(input.url, wait)
                await backend.set_files(input.selector, input.files)
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
        """Drop files or MIME-typed data onto an element.

        Args:
            input: Drop parameters (selector, data map, file paths).

        Returns:
            JSON string with status ``"ok"`` and drop summary.
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
                    await backend.navigate(input.url, wait)

                escaped = input.selector.replace("'", "\\'")
                js = (
                    f"(function(){{"
                    f"var el=document.querySelector('{escaped}');"
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
                drag_data: dict[str, Any] = {
                    "dragOperationsMask": 7,
                    "items": items,
                    "files": input.paths,
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
                        "files": input.paths,
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
        """Check a checkbox or radio button.

        Args:
            input: Check parameters.

        Returns:
            JSON string with status ``"ok"`` and ``checked`` boolean.
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.click(input.selector)
            checked = await session.backend.eval(
                f"document.querySelector({input.selector!r})?.checked"
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
        """Uncheck a checkbox.

        Args:
            input: Uncheck parameters.

        Returns:
            JSON string with status ``"ok"``.
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
        """Find element(s) by visible text content.

        Args:
            input: Find parameters (query, all).

        Returns:
            JSON string with ``selector`` (first match) or ``selectors`` list.
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

        Args:
            input: NL click parameters (query, auto_wait).

        Returns:
            JSON string with status ``"ok"``.
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
        """Fill an element described in natural language.

        Args:
            input: NL fill parameters (query, value, auto_wait).

        Returns:
            JSON string with status ``"ok"``.
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.nl_fill(input.query, input.value, auto_wait=input.auto_wait)
            return format_json_response({"status": "ok"})
        except Exception as e:
            return format_error("wavexis_nl_fill", e)
