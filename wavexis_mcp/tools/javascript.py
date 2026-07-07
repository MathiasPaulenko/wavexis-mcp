"""JavaScript evaluation tool for WaveXisMCP.

Provides the ``wavexis_eval`` tool for evaluating JavaScript
expressions in the browser context.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from wavexis_mcp.formatter import format_error, format_json_response
from wavexis_mcp.models import EvalInput
from wavexis_mcp.session import SessionManager


def register(mcp: FastMCP, session_manager: SessionManager) -> None:
    """Register the JavaScript eval tool on the FastMCP server.

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
    async def wavexis_eval(input: EvalInput) -> str:
        """Evaluate a JavaScript expression and return the result.

        Args:
            input: Eval parameters (expression, await_promise).

        Returns:
            JSON string with ``result`` and ``type``.
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

                result = await backend.eval(input.expression, await_promise=input.await_promise)
                result_type = type(result).__name__ if result is not None else "undefined"
                return format_json_response(
                    {
                        "result": result,
                        "type": result_type,
                    }
                )
            finally:
                await session_manager.release_backend(backend, sid)
        except Exception as e:
            return format_error("wavexis_eval", e)
