"""DOM manipulation tools for WaveXisMCP.

Provides tools for getting/setting HTML, querying elements,
managing attributes, focusing, scrolling, and capturing
DOM snapshots.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from wavexis_mcp.formatter import format_error, format_json_response
from wavexis_mcp.models import (
    DOMFocusInput,
    DOMGetAttrInput,
    DOMGetInput,
    DOMQueryInput,
    DOMRemoveAttrInput,
    DOMRemoveInput,
    DOMScrollInput,
    DOMSetAttrInput,
    DOMSnapshotInput,
)
from wavexis_mcp.session import SessionManager


def register(mcp: FastMCP, session_manager: SessionManager) -> None:
    """Register all DOM tools on the FastMCP server.

    Args:
        mcp: The FastMCP server instance.
        session_manager: The shared session manager.
    """

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    ))
    async def wavexis_dom_get(input: DOMGetInput) -> str:
        """Get the HTML of an element matching a CSS selector.

        Args:
            input: DOM get parameters (selector, outer/inner).

        Returns:
            JSON string with ``html`` and ``selector``.
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
                html = await backend.dom_get(input.selector, outer=input.outer)
                return format_json_response({"html": html, "selector": input.selector})
            finally:
                await session_manager.release_backend(backend, sid)
        except Exception as e:
            return format_error("wavexis_dom_get", e)

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    ))
    async def wavexis_dom_query(input: DOMQueryInput) -> str:
        """Query elements by CSS selector.

        Args:
            input: Query parameters (selector, all, pagination).

        Returns:
            JSON string with paginated ``elements``, ``count``, and ``total``.
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
                raw = await backend.dom_query(input.selector, all=input.all)
                elements = raw if isinstance(raw, list) else [raw]
                paginated = elements[input.offset : input.offset + input.limit]
                return format_json_response({
                    "elements": paginated,
                    "count": len(paginated),
                    "total": len(elements),
                })
            finally:
                await session_manager.release_backend(backend, sid)
        except Exception as e:
            return format_error("wavexis_dom_query", e)

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ))
    async def wavexis_dom_set_attr(input: DOMSetAttrInput) -> str:
        """Set an attribute on an element matching a CSS selector.

        Args:
            input: Attribute parameters (selector, name, value).

        Returns:
            JSON string with status ``"ok"``.
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.dom_set_attr(input.selector, input.name, input.value)
            return format_json_response({"status": "ok"})
        except Exception as e:
            return format_error("wavexis_dom_set_attr", e)

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ))
    async def wavexis_dom_get_attr(input: DOMGetAttrInput) -> str:
        """Get an attribute value from an element matching a CSS selector.

        Args:
            input: Attribute parameters (selector, name).

        Returns:
            JSON string with ``value``, ``selector``, and ``name``.
        """
        try:
            session = session_manager.get(input.session_id)
            value = await session.backend.dom_get_attr(input.selector, input.name)
            return format_json_response({
                "value": value,
                "selector": input.selector,
                "name": input.name,
            })
        except Exception as e:
            return format_error("wavexis_dom_get_attr", e)

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=True,
        idempotentHint=True,
        openWorldHint=False,
    ))
    async def wavexis_dom_remove_attr(input: DOMRemoveAttrInput) -> str:
        """Remove an attribute from an element matching a CSS selector.

        Args:
            input: Attribute removal parameters (selector, name).

        Returns:
            JSON string with status ``"ok"``.
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.dom_remove_attr(input.selector, input.name)
            return format_json_response({"status": "ok"})
        except Exception as e:
            return format_error("wavexis_dom_remove_attr", e)

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=True,
        idempotentHint=True,
        openWorldHint=False,
    ))
    async def wavexis_dom_remove(input: DOMRemoveInput) -> str:
        """Remove an element matching a CSS selector from the DOM.

        Args:
            input: Element removal parameters.

        Returns:
            JSON string with status ``"ok"``.
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.dom_remove(input.selector)
            return format_json_response({"status": "ok"})
        except Exception as e:
            return format_error("wavexis_dom_remove", e)

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ))
    async def wavexis_dom_focus(input: DOMFocusInput) -> str:
        """Focus an element matching a CSS selector.

        Args:
            input: Focus parameters.

        Returns:
            JSON string with status ``"ok"``.
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.dom_focus(input.selector)
            return format_json_response({"status": "ok"})
        except Exception as e:
            return format_error("wavexis_dom_focus", e)

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ))
    async def wavexis_dom_scroll(input: DOMScrollInput) -> str:
        """Scroll to an element or by offset.

        Args:
            input: Scroll parameters (selector or x/y offset).

        Returns:
            JSON string with status ``"ok"``.
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.dom_scroll(
                selector=input.selector, x=input.x, y=input.y
            )
            return format_json_response({"status": "ok"})
        except Exception as e:
            return format_error("wavexis_dom_scroll", e)

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ))
    async def wavexis_dom_snapshot(input: DOMSnapshotInput) -> str:
        """Capture a full DOM snapshot of the page.

        Args:
            input: Snapshot parameters.

        Returns:
            JSON string with ``snapshot`` and ``documents`` count.
        """
        try:
            session = session_manager.get(input.session_id)
            snapshot = await session.backend.dom_snapshot()
            docs = len(snapshot.get("documents", [])) if isinstance(snapshot, dict) else 0
            return format_json_response({"snapshot": snapshot, "documents": docs})
        except Exception as e:
            return format_error("wavexis_dom_snapshot", e)
