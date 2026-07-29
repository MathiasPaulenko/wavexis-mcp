"""DOM manipulation tools for WaveXisMCP.

Provides tools for getting/setting HTML, querying elements,
managing attributes, focusing, scrolling, and capturing
DOM snapshots.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from wavexis_mcp.formatter import format_error, format_json_response, validate_url
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
    IframeClickInput,
    IframeEvalInput,
    IframeFillInput,
    ShadowClickInput,
    ShadowEvalInput,
    ShadowFillInput,
)
from wavexis_mcp.session import SessionManager


def register(mcp: FastMCP, session_manager: SessionManager) -> None:
    """Register all DOM tools on the FastMCP server.

    Args:
        mcp: The FastMCP server instance.
        session_manager: The shared session manager.
    """

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=True,
        )
    )
    async def wavexis_dom_get(input: DOMGetInput) -> str:
        """Retrieve the HTML of an element matching a CSS selector.

        Use wavexis_dom_query instead when you need element metadata rather than raw HTML.

        Side effects: None; read-only. May navigate to ``url`` if provided.
        Returns: JSON string with keys: 'status' ('ok'/'error'), 'html' (str), 'selector' (str).
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
                html = await backend.dom_get(input.selector, outer=input.outer)
                return format_json_response({"html": html, "selector": input.selector})
            finally:
                await session_manager.release_backend(backend, sid)
        except Exception as e:
            return format_error("wavexis_dom_get", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=True,
        )
    )
    async def wavexis_dom_query(input: DOMQueryInput) -> str:
        """Query elements by CSS selector and return paginated metadata.

        Use wavexis_dom_get instead when you only need the raw HTML of a single element.

        Side effects: None; read-only. May navigate to ``url`` if provided.
        Returns: JSON string with keys: 'status' ('ok'/'error'), 'elements' (list[dict]),
            'count' (int), 'total' (int).
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
                raw = await backend.dom_query(input.selector, all=input.all)
                elements = raw if isinstance(raw, list) else [raw]
                paginated = elements[input.offset : input.offset + input.limit]
                return format_json_response(
                    {
                        "elements": paginated,
                        "count": len(paginated),
                        "total": len(elements),
                    }
                )
            finally:
                await session_manager.release_backend(backend, sid)
        except Exception as e:
            return format_error("wavexis_dom_query", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def wavexis_dom_set_attr(input: DOMSetAttrInput) -> str:
        """Set an attribute on an element matching a CSS selector.

        Use wavexis_dom_get_attr to read the current value before setting.

        Side effects: Mutates the DOM by writing the attribute on the matched element.
        Returns: JSON string with keys: 'status' ('ok'/'error').
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.dom_set_attr(input.selector, input.name, input.value)
            return format_json_response({"status": "ok"})
        except Exception as e:
            return format_error("wavexis_dom_set_attr", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def wavexis_dom_get_attr(input: DOMGetAttrInput) -> str:
        """Read an attribute value from an element matching a CSS selector.

        Use wavexis_dom_set_attr to write an attribute value.

        Side effects: None; read-only.
        Returns: JSON string with keys: 'status' ('ok'/'error'), 'value' (str|None),
            'selector' (str), 'name' (str).
        """
        try:
            session = session_manager.get(input.session_id)
            value = await session.backend.dom_get_attr(input.selector, input.name)
            return format_json_response(
                {
                    "value": value,
                    "selector": input.selector,
                    "name": input.name,
                }
            )
        except Exception as e:
            return format_error("wavexis_dom_get_attr", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=True,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def wavexis_dom_remove_attr(input: DOMRemoveAttrInput) -> str:
        """Remove an attribute from an element matching a CSS selector.

        Use wavexis_dom_set_attr to restore or change an attribute instead of removing it.

        Side effects: Mutates the DOM by deleting the attribute from the matched element.
        Returns: JSON string with keys: 'status' ('ok'/'error').
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.dom_remove_attr(input.selector, input.name)
            return format_json_response({"status": "ok"})
        except Exception as e:
            return format_error("wavexis_dom_remove_attr", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=True,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def wavexis_dom_remove(input: DOMRemoveInput) -> str:
        """Remove an element matching a CSS selector from the DOM.

        Use wavexis_dom_set_attr to hide an element (e.g. ``display:none``) instead of deleting it.

        Side effects: Destructive; permanently removes the matched element from the live DOM.
        Returns: JSON string with keys: 'status' ('ok'/'error').
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.dom_remove(input.selector)
            return format_json_response({"status": "ok"})
        except Exception as e:
            return format_error("wavexis_dom_remove", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def wavexis_dom_focus(input: DOMFocusInput) -> str:
        """Focus an element matching a CSS selector.

        Use wavexis_dom_click instead when the intent is to activate a control rather than focus it.

        Side effects: Mutates DOM focus state; may trigger focus event handlers on the element.
        Returns: JSON string with keys: 'status' ('ok'/'error').
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.dom_focus(input.selector)
            return format_json_response({"status": "ok"})
        except Exception as e:
            return format_error("wavexis_dom_focus", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def wavexis_dom_scroll(input: DOMScrollInput) -> str:
        """Scroll to an element or by a pixel offset.

        Use wavexis_dom_get to inspect an element's position before scrolling by offset.

        Side effects: Changes the page scroll position; may trigger scroll event listeners.
        Returns: JSON string with keys: 'status' ('ok'/'error').
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.dom_scroll(selector=input.selector, x=input.x, y=input.y)
            return format_json_response({"status": "ok"})
        except Exception as e:
            return format_error("wavexis_dom_scroll", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def wavexis_dom_snapshot(input: DOMSnapshotInput) -> str:
        """Capture a full DOM snapshot of the page including iframes and shadow roots.

        Use wavexis_dom_query for lightweight element metadata instead of a full snapshot.

        Side effects: None; read-only.
        Returns: JSON string with keys: 'status' ('ok'/'error'), 'snapshot' (dict),
            'documents' (int).
        """
        try:
            session = session_manager.get(input.session_id)
            snapshot = await session.backend.dom_snapshot()
            docs = len(snapshot.get("documents", [])) if isinstance(snapshot, dict) else 0
            return format_json_response({"snapshot": snapshot, "documents": docs})
        except Exception as e:
            return format_error("wavexis_dom_snapshot", e)

    # ── iframe ──────────────────────────────────────────────

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=True,
        )
    )
    async def wavexis_iframe_eval(input: IframeEvalInput) -> str:
        """Evaluate a JavaScript expression inside an iframe.

        Use wavexis_iframe_click or wavexis_iframe_fill for standard interactions instead of raw JS.

        Side effects: Arbitrary; executes user-supplied JavaScript within the iframe context.
        Returns: JSON string with keys: 'status' ('ok'/'error'), 'result' (any).
        """
        try:
            session = session_manager.get(input.session_id)
            result = await session.backend.iframe_eval(
                input.iframe_selector,
                input.expression,
                await_promise=input.await_promise,
            )
            return format_json_response({"result": result})
        except Exception as e:
            return format_error("wavexis_iframe_eval", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=True,
            idempotentHint=False,
            openWorldHint=True,
        )
    )
    async def wavexis_iframe_click(input: IframeClickInput) -> str:
        """Click an element inside an iframe.

        Use wavexis_iframe_eval only for custom JS that click/fill cannot express.

        Side effects: Triggers click handlers and may navigate or mutate the iframe DOM.
        Returns: JSON string with keys: 'status' ('ok'/'error').
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.iframe_click(
                input.iframe_selector,
                input.selector,
            )
            return format_json_response({"status": "ok"})
        except Exception as e:
            return format_error("wavexis_iframe_click", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=True,
            idempotentHint=False,
            openWorldHint=True,
        )
    )
    async def wavexis_iframe_fill(input: IframeFillInput) -> str:
        """Fill an input element inside an iframe with a value.

        Use wavexis_iframe_click to submit or activate the field after filling.

        Side effects: Mutates the input value within the iframe; may trigger input/change events.
        Returns: JSON string with keys: 'status' ('ok'/'error').
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.iframe_fill(
                input.iframe_selector,
                input.selector,
                input.value,
            )
            return format_json_response({"status": "ok"})
        except Exception as e:
            return format_error("wavexis_iframe_fill", e)

    # ── Shadow DOM ──────────────────────────────────────────

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=True,
        )
    )
    async def wavexis_shadow_eval(input: ShadowEvalInput) -> str:
        """Evaluate a JavaScript expression inside a shadow DOM tree.

        Pierces shadow boundaries using the provided selector chain: ``selectors[0]`` is in the
        main document, ``selectors[1]`` in ``selectors[0].shadowRoot``, and so on.
        Use wavexis_shadow_click or wavexis_shadow_fill for standard interactions instead of raw JS.

        Side effects: Arbitrary; executes user-supplied JavaScript within the shadow DOM context.
        Returns: JSON string with keys: 'status' ('ok'/'error'), 'result' (any).
        """
        try:
            session = session_manager.get(input.session_id)
            result = await session.backend.shadow_eval(
                input.selectors,
                input.expression,
                await_promise=input.await_promise,
            )
            return format_json_response({"result": result})
        except Exception as e:
            return format_error("wavexis_shadow_eval", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=True,
            idempotentHint=False,
            openWorldHint=True,
        )
    )
    async def wavexis_shadow_click(input: ShadowClickInput) -> str:
        """Click an element inside a shadow DOM tree.

        Pierces shadow boundaries using the provided selector chain.
        Use wavexis_shadow_eval only for custom JS that click/fill cannot express.

        Side effects: Triggers click handlers and may navigate or mutate the shadow DOM.
        Returns: JSON string with keys: 'status' ('ok'/'error').
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.shadow_click(input.selectors)
            return format_json_response({"status": "ok"})
        except Exception as e:
            return format_error("wavexis_shadow_click", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=True,
            idempotentHint=False,
            openWorldHint=True,
        )
    )
    async def wavexis_shadow_fill(input: ShadowFillInput) -> str:
        """Fill an input element inside a shadow DOM tree with a value.

        Pierces shadow boundaries using the provided selector chain.
        Use wavexis_shadow_click to submit or activate the field after filling.

        Side effects: Mutates the input value within the shadow DOM; may trigger
        input/change events.
        Returns: JSON string with keys: 'status' ('ok'/'error').
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.shadow_fill(input.selectors, input.value)
            return format_json_response({"status": "ok"})
        except Exception as e:
            return format_error("wavexis_shadow_fill", e)
