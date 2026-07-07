"""DevTools tools for WaveXisMCP.

Provides tools for Performance (metrics, trace, profile, heap
snapshot, coverage), CSS inspection, debugging (breakpoints,
stepping, pause/resume, event listeners), overlay highlighting,
console & browser logs, security state, and window bounds.
"""

from __future__ import annotations

import asyncio
import json

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from wavexis_mcp.formatter import format_error, format_json_response
from wavexis_mcp.models import (
    BrowserLogsInput,
    ConsoleMessagesInput,
    CSSGetComputedInput,
    CSSGetRulesInput,
    CSSGetStylesheetsInput,
    CSSGetStylesInput,
    DebugGetListenersInput,
    DebugPauseInput,
    DebugRemoveBreakpointInput,
    DebugSetBreakpointFunctionInput,
    DebugSetBreakpointInput,
    DebugStepInput,
    GetSecurityStateInput,
    GetWindowBoundsInput,
    IgnoreCertErrorsInput,
    OverlayClearInput,
    OverlayHighlightInput,
    PerfCoverageInput,
    PerfCSSCoverageInput,
    PerfHeapSnapshotInput,
    PerfMetricsInput,
    PerfProfileInput,
    PerfTraceInput,
    SetWindowBoundsInput,
    StartCombinedTraceInput,
    StopCombinedTraceInput,
    SubscribeEventsInput,
    UnsubscribeEventsInput,
)
from wavexis_mcp.session import SessionManager

_LEVEL_ORDER = {"error": 0, "warning": 1, "info": 2, "debug": 3}


def _write_json(path: str, data: object) -> None:
    """Write JSON data to a file (used via ``asyncio.to_thread``).

    Args:
        path: Destination file path.
        data: JSON-serializable object to write.
    """
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f)


def register(mcp: FastMCP, session_manager: SessionManager) -> None:
    """Register all DevTools tools on the FastMCP server.

    Args:
        mcp: The FastMCP server instance.
        session_manager: The shared session manager.
    """

    # ── Performance (6) ──

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    ))
    async def wavexis_perf_metrics(input: PerfMetricsInput) -> str:
        """Get performance metrics (LCP, FCP, CLS, TTFB, DOMNodes, etc.).

        Args:
            input: Session reference parameters.

        Returns:
            JSON string with ``metrics`` dict.
        """
        try:
            session = session_manager.get(input.session_id)
            metrics = await session.backend.perf_metrics()
            return format_json_response({"metrics": metrics})
        except Exception as e:
            return format_error("wavexis_perf_metrics", e)

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    ))
    async def wavexis_perf_trace(input: PerfTraceInput) -> str:
        """Capture a performance trace.

        Args:
            input: Trace parameters (duration_ms, output_path).

        Returns:
            JSON string with ``trace`` data or file ``path``.
        """
        try:
            session = session_manager.get(input.session_id)
            trace = await session.backend.perf_trace(input.duration_ms)
            if input.output_path:
                await asyncio.to_thread(_write_json, input.output_path, trace)
                return format_json_response({"path": input.output_path})
            return format_json_response({"trace": trace})
        except Exception as e:
            return format_error("wavexis_perf_trace", e)

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    ))
    async def wavexis_perf_profile(input: PerfProfileInput) -> str:
        """Capture a CPU profile.

        Args:
            input: Profile parameters (duration_ms, output_path).

        Returns:
            JSON string with ``profile`` data or file ``path``.
        """
        try:
            session = session_manager.get(input.session_id)
            profile = await session.backend.perf_profile(input.duration_ms)
            if input.output_path:
                await asyncio.to_thread(_write_json, input.output_path, profile)
                return format_json_response({"path": input.output_path})
            return format_json_response({"profile": profile})
        except Exception as e:
            return format_error("wavexis_perf_profile", e)

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    ))
    async def wavexis_perf_heap_snapshot(input: PerfHeapSnapshotInput) -> str:
        """Capture a heap snapshot.

        Args:
            input: Heap snapshot parameters (output_path).

        Returns:
            JSON string with ``snapshot`` data or file ``path``.
        """
        try:
            session = session_manager.get(input.session_id)
            snapshot = await session.backend.perf_heap_snapshot()
            if input.output_path:
                await asyncio.to_thread(_write_json, input.output_path, snapshot)
                return format_json_response({"path": input.output_path})
            return format_json_response({"snapshot": snapshot})
        except Exception as e:
            return format_error("wavexis_perf_heap_snapshot", e)

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    ))
    async def wavexis_perf_coverage(input: PerfCoverageInput) -> str:
        """Get JavaScript code coverage.

        Args:
            input: Session reference parameters.

        Returns:
            JSON string with ``coverage`` data and ``scripts`` count.
        """
        try:
            session = session_manager.get(input.session_id)
            coverage = await session.backend.perf_coverage()
            if isinstance(coverage, list):
                scripts = len(coverage)
            else:
                scripts = len(coverage.get("result", []))
            return format_json_response({"coverage": coverage, "scripts": scripts})
        except Exception as e:
            return format_error("wavexis_perf_coverage", e)

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    ))
    async def wavexis_perf_css_coverage(input: PerfCSSCoverageInput) -> str:
        """Get CSS code coverage.

        Args:
            input: Session reference parameters.

        Returns:
            JSON string with ``coverage`` data.
        """
        try:
            session = session_manager.get(input.session_id)
            coverage = await session.backend.perf_css_coverage()
            return format_json_response({"coverage": coverage})
        except Exception as e:
            return format_error("wavexis_perf_css_coverage", e)

    # ── CSS (4) ──

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ))
    async def wavexis_css_get_styles(input: CSSGetStylesInput) -> str:
        """Get inline and matched CSS styles for an element.

        Args:
            input: CSS styles parameters (selector).

        Returns:
            JSON string with ``styles`` data.
        """
        try:
            session = session_manager.get(input.session_id)
            styles = await session.backend.css_get_styles(input.selector)
            return format_json_response({"styles": styles})
        except Exception as e:
            return format_error("wavexis_css_get_styles", e)

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ))
    async def wavexis_css_get_stylesheets(input: CSSGetStylesheetsInput) -> str:
        """List all stylesheets loaded by the page.

        Args:
            input: Session reference parameters.

        Returns:
            JSON string with ``stylesheets`` list and ``count``.
        """
        try:
            session = session_manager.get(input.session_id)
            stylesheets = await session.backend.css_get_stylesheets()
            return format_json_response({
                "stylesheets": stylesheets,
                "count": len(stylesheets),
            })
        except Exception as e:
            return format_error("wavexis_css_get_stylesheets", e)

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ))
    async def wavexis_css_get_rules(input: CSSGetRulesInput) -> str:
        """Get CSS rules from a specific stylesheet.

        Args:
            input: CSS rules parameters (stylesheet_id).

        Returns:
            JSON string with ``stylesheet_id``, ``rules``, and ``count``.
        """
        try:
            session = session_manager.get(input.session_id)
            rules = await session.backend.css_get_rules(input.stylesheet_id)
            return format_json_response({
                "stylesheet_id": input.stylesheet_id,
                "rules": rules,
                "count": len(rules),
            })
        except Exception as e:
            return format_error("wavexis_css_get_rules", e)

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    ))
    async def wavexis_css_get_computed(input: CSSGetComputedInput) -> str:
        """Get computed styles for an element.

        Args:
            input: Computed styles parameters (selector).

        Returns:
            JSON string with ``computed`` styles.
        """
        try:
            session = session_manager.get(input.session_id)
            computed = await session.backend.css_get_computed(input.selector)
            return format_json_response({"computed": computed})
        except Exception as e:
            return format_error("wavexis_css_get_computed", e)

    # ── Debugging (9) ──

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=False,
        openWorldHint=False,
    ))
    async def wavexis_debug_set_breakpoint(input: DebugSetBreakpointInput) -> str:
        """Set a breakpoint by URL and line number.

        Args:
            input: Breakpoint parameters (url, line, condition).

        Returns:
            JSON string with ``breakpoint_id``.
        """
        try:
            session = session_manager.get(input.session_id)
            bp_id = await session.backend.debug_set_breakpoint(
                input.url, input.line, input.condition
            )
            return format_json_response({"breakpoint_id": bp_id})
        except Exception as e:
            return format_error("wavexis_debug_set_breakpoint", e)

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=False,
        openWorldHint=False,
    ))
    async def wavexis_debug_set_breakpoint_function(
        input: DebugSetBreakpointFunctionInput,
    ) -> str:
        """Set a breakpoint by function name.

        Args:
            input: Breakpoint parameters (function_name).

        Returns:
            JSON string with ``breakpoint_id``.
        """
        try:
            session = session_manager.get(input.session_id)
            bp_id = await session.backend.debug_set_breakpoint_function(
                input.function_name
            )
            return format_json_response({"breakpoint_id": bp_id})
        except Exception as e:
            return format_error("wavexis_debug_set_breakpoint_function", e)

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=True,
        idempotentHint=True,
        openWorldHint=False,
    ))
    async def wavexis_debug_remove_breakpoint(input: DebugRemoveBreakpointInput) -> str:
        """Remove a breakpoint by ID.

        Args:
            input: Breakpoint removal parameters (breakpoint_id).

        Returns:
            JSON string with status ``"ok"``.
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.debug_remove_breakpoint(input.breakpoint_id)
            return format_json_response({"status": "ok"})
        except Exception as e:
            return format_error("wavexis_debug_remove_breakpoint", e)

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ))
    async def wavexis_debug_step_over(input: DebugStepInput) -> str:
        """Step over in the debugger.

        Args:
            input: Session reference parameters.

        Returns:
            JSON string with status ``"ok"``.
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.debug_step_over()
            return format_json_response({"status": "ok"})
        except Exception as e:
            return format_error("wavexis_debug_step_over", e)

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ))
    async def wavexis_debug_step_into(input: DebugStepInput) -> str:
        """Step into in the debugger.

        Args:
            input: Session reference parameters.

        Returns:
            JSON string with status ``"ok"``.
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.debug_step_into()
            return format_json_response({"status": "ok"})
        except Exception as e:
            return format_error("wavexis_debug_step_into", e)

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ))
    async def wavexis_debug_step_out(input: DebugStepInput) -> str:
        """Step out in the debugger.

        Args:
            input: Session reference parameters.

        Returns:
            JSON string with status ``"ok"``.
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.debug_step_out()
            return format_json_response({"status": "ok"})
        except Exception as e:
            return format_error("wavexis_debug_step_out", e)

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ))
    async def wavexis_debug_pause(input: DebugPauseInput) -> str:
        """Pause script execution.

        Args:
            input: Session reference parameters.

        Returns:
            JSON string with status ``"ok"``.
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.debug_pause()
            return format_json_response({"status": "ok"})
        except Exception as e:
            return format_error("wavexis_debug_pause", e)

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ))
    async def wavexis_debug_resume(input: DebugPauseInput) -> str:
        """Resume script execution.

        Args:
            input: Session reference parameters.

        Returns:
            JSON string with status ``"ok"``.
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.debug_resume()
            return format_json_response({"status": "ok"})
        except Exception as e:
            return format_error("wavexis_debug_resume", e)

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    ))
    async def wavexis_debug_get_listeners(input: DebugGetListenersInput) -> str:
        """Get event listeners attached to an element.

        Args:
            input: Event listener parameters (selector).

        Returns:
            JSON string with ``listeners`` list and ``count``.
        """
        try:
            session = session_manager.get(input.session_id)
            listeners = await session.backend.debug_get_listeners(input.selector)
            return format_json_response({"listeners": listeners, "count": len(listeners)})
        except Exception as e:
            return format_error("wavexis_debug_get_listeners", e)

    # ── Overlay (2) ──

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ))
    async def wavexis_overlay_highlight(input: OverlayHighlightInput) -> str:
        """Highlight an element with a colored overlay.

        Args:
            input: Highlight parameters (selector, color).

        Returns:
            JSON string with status ``"ok"`` and ``selector``.
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.overlay_highlight(input.selector, input.color)
            return format_json_response({"status": "ok", "selector": input.selector})
        except Exception as e:
            return format_error("wavexis_overlay_highlight", e)

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=True,
        idempotentHint=True,
        openWorldHint=False,
    ))
    async def wavexis_overlay_clear(input: OverlayClearInput) -> str:
        """Clear all overlay highlights.

        Args:
            input: Session reference parameters.

        Returns:
            JSON string with status ``"ok"``.
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.overlay_clear()
            return format_json_response({"status": "ok"})
        except Exception as e:
            return format_error("wavexis_overlay_clear", e)

    # ── Console & Logs (2) ──

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    ))
    async def wavexis_console_messages(input: ConsoleMessagesInput) -> str:
        """Get console messages with pagination.

        Args:
            input: Console messages parameters (level, pagination).

        Returns:
            JSON string with paginated ``messages``, ``count``, and ``total``.
        """
        try:
            session = session_manager.get(input.session_id)
            messages = await session.backend.capture_console(level=input.level)
            if not input.all:
                messages = messages[-50:]
            total = len(messages)
            paginated = messages[input.offset : input.offset + input.limit]
            return format_json_response({
                "messages": paginated,
                "count": len(paginated),
                "total": total,
            })
        except Exception as e:
            return format_error("wavexis_console_messages", e)

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ))
    async def wavexis_browser_logs(input: BrowserLogsInput) -> str:
        """Get browser-level log entries.

        Args:
            input: Session reference parameters.

        Returns:
            JSON string with ``logs`` list and ``count``.
        """
        try:
            session = session_manager.get(input.session_id)
            logs = await session.backend.capture_logs()
            return format_json_response({"logs": logs, "count": len(logs)})
        except Exception as e:
            return format_error("wavexis_browser_logs", e)

    # ── Security (2) ──

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    ))
    async def wavexis_get_security_state(input: GetSecurityStateInput) -> str:
        """Get the page security state.

        Args:
            input: Session reference parameters.

        Returns:
            JSON string with ``state`` data.
        """
        try:
            session = session_manager.get(input.session_id)
            state = await session.backend.get_security_state()
            return format_json_response({"state": state})
        except Exception as e:
            return format_error("wavexis_get_security_state", e)

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=True,
        idempotentHint=True,
        openWorldHint=False,
    ))
    async def wavexis_ignore_cert_errors(input: IgnoreCertErrorsInput) -> str:
        """Enable or disable certificate error ignoring.

        Args:
            input: Certificate error parameters (ignore).

        Returns:
            JSON string with status ``"ok"`` and ``ignore``.
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.ignore_cert_errors(input.ignore)
            return format_json_response({"status": "ok", "ignore": input.ignore})
        except Exception as e:
            return format_error("wavexis_ignore_cert_errors", e)

    # ── Window (2) ──

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ))
    async def wavexis_get_window_bounds(input: GetWindowBoundsInput) -> str:
        """Get the browser window bounds.

        Args:
            input: Session reference parameters.

        Returns:
            JSON string with window bounds (width, height, x, y).
        """
        try:
            session = session_manager.get(input.session_id)
            bounds = await session.backend.get_window_bounds()
            return format_json_response(bounds)
        except Exception as e:
            return format_error("wavexis_get_window_bounds", e)

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ))
    async def wavexis_set_window_bounds(input: SetWindowBoundsInput) -> str:
        """Set the browser window bounds.

        Args:
            input: Window bounds parameters (width, height, x, y).

        Returns:
            JSON string with status ``"ok"`` and bounds values.
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.set_window_bounds(
                input.width, input.height, input.x, input.y
            )
            return format_json_response({
                "status": "ok",
                "width": input.width,
                "height": input.height,
                "x": input.x,
                "y": input.y,
            })
        except Exception as e:
            return format_error("wavexis_set_window_bounds", e)

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=False,
        openWorldHint=True,
    ))
    async def wavexis_start_combined_trace(input: StartCombinedTraceInput) -> str:
        """Start a combined trace capturing screenshots, network, and console (W8).

        Args:
            input: Combined trace start parameters.

        Returns:
            JSON string with ``trace_id``.
        """
        try:
            session = session_manager.get(input.session_id)
            trace_id = await session.backend.start_combined_trace(
                capture_screenshots=input.capture_screenshots,
                capture_network=input.capture_network,
                capture_console=input.capture_console,
            )
            return format_json_response({"trace_id": trace_id, "status": "started"})
        except Exception as e:
            return format_error("wavexis_start_combined_trace", e)

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    ))
    async def wavexis_stop_combined_trace(input: StopCombinedTraceInput) -> str:
        """Stop a combined trace and return collected data (W8).

        Args:
            input: Combined trace stop parameters (trace_id).

        Returns:
            JSON string with ``trace`` data including events, screenshots, network, console.
        """
        try:
            session = session_manager.get(input.session_id)
            trace = await session.backend.stop_combined_trace(input.trace_id)
            return format_json_response({"trace": trace, "status": "stopped"})
        except Exception as e:
            return format_error("wavexis_stop_combined_trace", e)

    # ── Event subscription (W10) ──

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=False,
        openWorldHint=False,
    ))
    async def wavexis_subscribe_events(input: SubscribeEventsInput) -> str:
        """Subscribe to real-time browser events (W10).

        Event types: console, network_request, network_response,
        dom_mutation, dialog, navigation.  Events are collected
        internally and can be retrieved via console_messages or
        network_requests tools while the subscription is active.

        Args:
            input: Subscription parameters (event_types).

        Returns:
            JSON string with ``subscription_id``.
        """
        try:
            session = session_manager.get(input.session_id)
            sub_id = await session.backend.subscribe_events(
                input.event_types,
                callback=None,
            )
            return format_json_response({
                "subscription_id": sub_id,
                "event_types": input.event_types,
                "status": "subscribed",
            })
        except Exception as e:
            return format_error("wavexis_subscribe_events", e)

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ))
    async def wavexis_unsubscribe_events(input: UnsubscribeEventsInput) -> str:
        """Unsubscribe from browser events by subscription ID (W10).

        Args:
            input: Unsubscribe parameters (subscription_id).

        Returns:
            JSON string with status ``"ok"``.
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.unsubscribe_events(input.subscription_id)
            return format_json_response({"status": "ok"})
        except Exception as e:
            return format_error("wavexis_unsubscribe_events", e)
