"""Utility tools for WaveXisMCP.

Provides ``wavexis_browser_version``, ``wavexis_backends`` and
``wavexis_invoke`` for querying browser information and invoking
arbitrary backend methods.
"""

from __future__ import annotations

import base64
import inspect
import os
from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from wavexis_mcp.formatter import encode_base64, format_error, format_json_response, save_to_file
from wavexis_mcp.models import BrowserVersionInput, InvokeInput
from wavexis_mcp.session import SessionManager


def register(mcp: FastMCP, session_manager: SessionManager) -> None:
    """Register all utility tools on the FastMCP server.

    Args:
        mcp: The FastMCP server instance.
        session_manager: The shared session manager.
    """

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def wavexis_browser_version(input: BrowserVersionInput) -> str:
        """Get the browser version string.

        Args:
            input: Browser version parameters.

        Returns:
            JSON string with ``version`` and ``backend``.
        """
        try:
            backend, sid = await session_manager.acquire_backend(
                input.session_id,
                backend=input.backend,
            )
            try:
                version = await backend.browser_version()
                return format_json_response({"version": version, "backend": input.backend})
            finally:
                await session_manager.release_backend(backend, sid)
        except Exception as e:
            return format_error("wavexis_browser_version", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def wavexis_backends() -> str:
        """List available browser backends and their versions.

        Returns:
            JSON string with ``backends`` and ``available`` lists.
        """
        try:
            from wavexis.backend.manager import BackendManager

            mgr = BackendManager()
            available = mgr.list_available()
            versions = mgr.install_check()
            return format_json_response({"backends": versions, "available": available})
        except Exception as e:
            return format_error("wavexis_backends", e)

    def _build_result(result: Any, output_path: str | None) -> dict[str, Any] | str:
        if isinstance(result, bytes):
            if output_path:
                meta = save_to_file(result, output_path)
                return {"status": "ok", "type": "bytes", **meta}
            return {
                "status": "ok",
                "type": "bytes",
                "base64": encode_base64(result),
                "size_bytes": len(result),
            }
        if isinstance(result, list) and result and isinstance(result[0], bytes):
            if output_path and (
                output_path.endswith(("/", "\\")) or os.path.splitext(output_path)[1] == ""
            ):
                os.makedirs(output_path, exist_ok=True)
                frames = []
                for i, frame in enumerate(result):
                    frame_path = os.path.join(output_path, f"frame_{i:04d}.bin")
                    frame_meta = save_to_file(frame, frame_path)
                    frames.append(frame_meta)
                return {
                    "status": "ok",
                    "type": "bytes_list",
                    "dir": output_path,
                    "count": len(frames),
                    "frames": frames,
                }
            return {
                "status": "ok",
                "type": "bytes_list",
                "count": len(result),
                "base64": [base64.b64encode(f).decode("ascii") for f in result],
            }
        return {"status": "ok", "type": type(result).__name__, "result": result}

    async def _call_backend_method(backend: Any, method_name: str, params: dict[str, Any]) -> Any:
        method = getattr(backend, method_name, None)
        if method is None or not callable(method):
            raise AttributeError(f"Backend has no method '{method_name}'")
        if method_name.startswith("_"):
            raise ValueError(f"Cannot invoke private method '{method_name}'")

        sig = inspect.signature(method, eval_str=True)
        sig_params = list(sig.parameters.items())

        # If the first parameter is named 'params' and annotated with a class,
        # treat the provided JSON dict as the dataclass constructor kwargs.
        if sig_params and sig_params[0][0] == "params":
            annotation = sig_params[0][1].annotation
            if inspect.isclass(annotation) and annotation is not inspect.Parameter.empty:
                param_obj = annotation(**params)
                return await method(param_obj)

        return await method(**params)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=True,
            idempotentHint=False,
            openWorldHint=True,
        )
    )
    async def wavexis_invoke(input: InvokeInput) -> str:
        """Invoke any wavexis backend method by name.

        This is the ultimate escape hatch: it exposes the full ``AbstractBackend``
        API (e.g. ``page_print_to_pdf``, ``perf_trace``, ``runtime_evaluate``,
        ``pwa_install``, etc.) without needing a dedicated MCP tool per method.

        Args:
            input: Method name, keyword arguments, and optional session/launch options.

        Returns:
            JSON string with the method result (base64 for binary outputs).
        """
        ephemeral_sid: str | None = None
        try:
            if input.session_id:
                session = session_manager.get(input.session_id)
                backend = session.backend
            else:
                backend, ephemeral_sid = await session_manager.acquire_backend(
                    None,
                    backend=input.backend,
                    headless=input.headless,
                    width=input.width,
                    height=input.height,
                    user_agent=input.user_agent,
                    extra_headers=input.extra_headers,
                    proxy=input.proxy,
                    timeout=input.timeout,
                    user_data_dir=input.user_data_dir,
                    connect_endpoint=input.browser_url,
                    remote_url=input.remote_url,
                    stealth=input.stealth,
                )

            if input.url:
                wait = session_manager.make_wait(
                    strategy=input.wait_strategy,
                    selector=input.wait_selector,
                    timeout=input.wait_timeout,
                )
                await backend.navigate(input.url, wait)

            result = await _call_backend_method(backend, input.method, input.params)
            payload = _build_result(result, input.output_path)
            return format_json_response(payload)
        except Exception as e:
            return format_error("wavexis_invoke", e)
        finally:
            if input.session_id is None and "backend" in locals():
                await session_manager.release_backend(backend, ephemeral_sid)
