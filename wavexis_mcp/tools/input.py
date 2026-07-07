"""Input interaction tools for WaveXisMCP.

Provides click, type, fill, fill_form, select_option, hover,
key_press, drag, tap, set_files, check, and uncheck tools.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from wavexis_mcp.convenience import fill_form_composite
from wavexis_mcp.formatter import format_error, format_json_response
from wavexis_mcp.models import (
    CheckInput,
    ClickInput,
    DragInput,
    FillFormInput,
    FillInput,
    HoverInput,
    KeyPressInput,
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

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=True,
        idempotentHint=False,
        openWorldHint=True,
    ))
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

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=True,
        idempotentHint=False,
        openWorldHint=True,
    ))
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

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=True,
        idempotentHint=False,
        openWorldHint=True,
    ))
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

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=True,
        idempotentHint=False,
        openWorldHint=True,
    ))
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

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=True,
        idempotentHint=False,
        openWorldHint=True,
    ))
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

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=False,
        openWorldHint=True,
    ))
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

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=False,
        openWorldHint=False,
    ))
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

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=True,
        idempotentHint=False,
        openWorldHint=True,
    ))
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

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=False,
        openWorldHint=True,
    ))
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

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=True,
        idempotentHint=False,
        openWorldHint=True,
    ))
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

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=True,
        idempotentHint=True,
        openWorldHint=False,
    ))
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

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=True,
        idempotentHint=True,
        openWorldHint=False,
    ))
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
