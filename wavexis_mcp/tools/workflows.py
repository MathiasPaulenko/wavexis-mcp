"""Workflow tools for WaveXisMCP.

Provides multi-action YAML execution, raw CDP/BiDi escape hatches,
and browser context management.  These tools enable complex
automation workflows on a single session.
"""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from wavexis_mcp.formatter import format_error, format_json_response
from wavexis_mcp.models import (
    BrowserContextCloseInput,
    BrowserContextCreateInput,
    BrowserContextListInput,
    MultiActionInput,
    RawBiDiInput,
    RawCDPInput,
)
from wavexis_mcp.session import SessionManager


def register(mcp: FastMCP, session_manager: SessionManager) -> None:
    """Register all workflow tools on the FastMCP server.

    Args:
        mcp: The FastMCP server instance.
        session_manager: The shared session manager.
    """

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=True,
        )
    )
    async def wavexis_multi_action(input: MultiActionInput) -> str:
        """Execute multiple actions from a YAML config sequentially.

        Args:
            input: Multi-action parameters (YAML config, continue_on_error).

        Returns:
            JSON string with ``actions`` count, ``results``, and ``errors``.
        """
        try:
            import yaml

            config = yaml.safe_load(input.config)
            actions = config.get("actions", []) if config else []

            backend, sid = await session_manager.acquire_backend(
                input.session_id,
                backend=input.backend,
                headless=input.headless,
            )
            try:
                results: list[dict[str, Any]] = []
                errors: list[dict[str, Any]] = []

                for i, action in enumerate(actions):
                    try:
                        for action_type, params in action.items():
                            if action_type == "navigate":
                                wait = session_manager.make_wait(timeout=30000)
                                await backend.navigate(params.get("url", ""), wait)
                                results.append({"action": i, "type": "navigate", "status": "ok"})
                            elif action_type == "screenshot":
                                from wavexis.config import ScreenshotParams

                                p = ScreenshotParams(
                                    url="",
                                    full_page=params.get("full_page", False),
                                )
                                data = await backend.screenshot(p)
                                results.append(
                                    {
                                        "action": i,
                                        "type": "screenshot",
                                        "status": "ok",
                                        "size": len(data),
                                    }
                                )
                            elif action_type == "eval":
                                result = await backend.eval(
                                    params.get("expression", ""),
                                    await_promise=params.get("await_promise", False),
                                )
                                results.append(
                                    {
                                        "action": i,
                                        "type": "eval",
                                        "status": "ok",
                                        "result": result,
                                    }
                                )
                            elif action_type == "click":
                                await backend.click(params.get("selector", ""))
                                results.append({"action": i, "type": "click", "status": "ok"})
                            elif action_type == "type":
                                await backend.type_text(
                                    params.get("selector", ""),
                                    params.get("text", ""),
                                )
                                results.append({"action": i, "type": "type", "status": "ok"})
                            elif action_type == "fill":
                                await backend.fill(
                                    params.get("selector", ""),
                                    params.get("value", ""),
                                )
                                results.append({"action": i, "type": "fill", "status": "ok"})
                            else:
                                results.append(
                                    {
                                        "action": i,
                                        "type": action_type,
                                        "status": "unknown",
                                    }
                                )
                    except Exception as exc:
                        errors.append({"action": i, "error": str(exc)})
                        if not input.continue_on_error:
                            break
                    finally:
                        pass

                return format_json_response(
                    {
                        "status": "ok",
                        "actions": len(actions),
                        "results": results,
                        "errors": errors,
                    }
                )
            finally:
                await session_manager.release_backend(backend, sid)
        except Exception as e:
            return format_error("wavexis_multi_action", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=True,
        )
    )
    async def wavexis_raw_cdp(input: RawCDPInput) -> str:
        """Send a raw CDP command (escape hatch).

        Args:
            input: Raw CDP parameters (method, params).

        Returns:
            JSON string with raw ``result`` from the CDP command.
        """
        try:
            session = session_manager.get(input.session_id)
            result = await session.backend.raw(
                input.method,
                input.params or {},
            )
            return format_json_response({"result": result})
        except Exception as e:
            return format_error("wavexis_raw_cdp", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=True,
        )
    )
    async def wavexis_raw_bidi(input: RawBiDiInput) -> str:
        """Send a raw BiDi command (escape hatch).

        Args:
            input: Raw BiDi parameters (method, params).

        Returns:
            JSON string with raw ``result`` from the BiDi command.
        """
        try:
            session = session_manager.get(input.session_id)
            result = await session.backend.raw(
                input.method,
                input.params or {},
            )
            return format_json_response({"result": result})
        except Exception as e:
            return format_error("wavexis_raw_bidi", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=True,
        )
    )
    async def wavexis_browser_context_create(
        input: BrowserContextCreateInput,
    ) -> str:
        """Create an isolated browser context within a session.

        Args:
            input: Context creation parameters (session_id).

        Returns:
            JSON string with ``context_id``.
        """
        try:
            session = session_manager.get(input.session_id)
            context_id = await session.backend.new_context()
            return format_json_response({"context_id": context_id})
        except Exception as e:
            return format_error("wavexis_browser_context_create", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=True,
            idempotentHint=False,
            openWorldHint=True,
        )
    )
    async def wavexis_browser_context_close(
        input: BrowserContextCloseInput,
    ) -> str:
        """Close an isolated browser context.

        Args:
            input: Context close parameters (session_id, context_id).

        Returns:
            JSON string with status ``"ok"``.
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.close_context(input.context_id)
            return format_json_response({"status": "ok"})
        except Exception as e:
            return format_error("wavexis_browser_context_close", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def wavexis_browser_context_list(
        input: BrowserContextListInput,
    ) -> str:
        """List all browser contexts in a session.

        Args:
            input: List contexts parameters (session_id).

        Returns:
            JSON string with ``contexts`` list and ``count``.
        """
        try:
            session = session_manager.get(input.session_id)
            contexts = await session.backend.list_contexts()
            return format_json_response({"contexts": contexts, "count": len(contexts)})
        except Exception as e:
            return format_error("wavexis_browser_context_list", e)
