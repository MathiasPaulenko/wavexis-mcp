"""Utility tools for WaveXisMCP.

Provides ``wavexis_browser_version``, ``wavexis_backends`` and
``wavexis_invoke`` for querying browser information and invoking
arbitrary backend methods.
"""

from __future__ import annotations

import asyncio
import base64
import inspect
import logging
import os
import typing
from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from wavexis.backend.base import AbstractBackend

from wavexis_mcp.formatter import (
    encode_base64,
    format_error,
    format_json_response,
    save_to_file,
    secure_output_path,
    validate_url,
)
from wavexis_mcp.models import BrowserVersionInput, InvokeInput
from wavexis_mcp.session import SessionManager

# Methods that should never be exposed through the generic invoke tool.
_INVOKE_DENYLIST = frozenset(
    {
        "launch",
        "close",
        "eval",
        "raw",
        "execute",
        "__init__",
        "extension_install",
        "extension_uninstall",
    }
)

_logger = logging.getLogger(__name__)

# Safe builtins that may appear as string annotations for methods defined
# outside of the wavexis package (e.g. test doubles).  Arbitrary expressions
# are not evaluated.
_SAFE_TYPE_NS = {
    "dict": dict,
    "list": list,
    "str": str,
    "int": int,
    "float": float,
    "bool": bool,
    "None": type(None),
}


def _resolve_params_type(method: Any) -> Any:
    """Safely resolve the type hint of a method's ``params`` parameter.

    If the first parameter already has a real class annotation, it is used
    directly.  String annotations are only resolved via ``typing.get_type_hints``
    for methods shipped with the ``wavexis`` package, avoiding evaluation of
    arbitrary code from untrusted sources.
    """
    try:
        sig = inspect.signature(method)
        first_param = next(iter(sig.parameters.values()))
    except (ValueError, StopIteration):
        return None
    annotation = first_param.annotation
    if inspect.isclass(annotation) and annotation is not inspect.Parameter.empty:
        return annotation

    if isinstance(annotation, str):
        module = getattr(method, "__module__", "")
        if isinstance(module, str) and module.startswith("wavexis."):
            try:
                hints = typing.get_type_hints(method)
            except Exception:
                return None
            return hints.get("params")
        # For non-wavexis methods, resolve only a whitelist of safe type names
        # so that test doubles with ``from __future__ import annotations`` work
        # without evaluating arbitrary expressions.
        resolved = _SAFE_TYPE_NS.get(annotation)
        if inspect.isclass(resolved):
            return resolved

    return None


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
        """Query the active browser's version string via the selected backend.

        Use ``wavexis_backends`` instead when you need a list of all installed
        backends without launching a browser.

        Side effects: Acquires (and may launch) a browser backend, then releases it.
        Returns: JSON string with keys: 'status' ('ok'/'error'), 'version' (str), 'backend' (str).
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
        """List installed browser backends and their versions without launching a browser.

        Use ``wavexis_browser_version`` instead when you need the version of a
        specific running session's backend.

        Side effects: None; queries the local filesystem only.
        Returns: JSON string with keys: 'status' ('ok'/'error'),
        'backends' (dict), 'available' (list[str]).
        """
        try:
            from wavexis.backend.manager import BackendManager

            mgr = BackendManager()
            available = mgr.list_available()
            versions = mgr.install_check()
            return format_json_response({"backends": versions, "available": available})
        except Exception as e:
            return format_error("wavexis_backends", e)

    async def _build_result(result: object, output_path: str | None) -> dict[str, Any]:
        """Format a raw backend result into a JSON-ready payload or file path.

        Bytes are returned as base64 or written to disk; lists of bytes are
        handled as frame sequences; any other value is wrapped with its type.

        Args:
            result: Raw return value from a backend method.
            output_path: Optional destination for binary outputs.

        Returns:
            A metadata dictionary describing the result.
        """
        if isinstance(result, bytes):
            if output_path:
                meta = await save_to_file(result, output_path)
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
                validated_dir = secure_output_path(output_path)
                await asyncio.to_thread(os.makedirs, validated_dir, exist_ok=True)
                frames = []
                for i, frame in enumerate(result):
                    frame_path = os.path.join(str(validated_dir), f"frame_{i:04d}.bin")
                    frame_meta = await save_to_file(frame, frame_path)
                    frames.append(frame_meta)
                return {
                    "status": "ok",
                    "type": "bytes_list",
                    "dir": str(validated_dir),
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

    async def _call_backend_method(
        backend: AbstractBackend, method_name: str, params: dict[str, Any]
    ) -> object:
        """Invoke a backend method, automatically wrapping dataclass parameters.

        Args:
            backend: The wavexis backend instance.
            method_name: Name of the backend method to call.
            params: JSON-compatible dict of arguments.

        Returns:
            The backend method's return value.

        Raises:
            AttributeError: If the backend does not expose the requested method.
            ValueError: If the method name refers to a private or denied method.
        """
        method = getattr(backend, method_name, None)
        if method is None or not callable(method):
            raise AttributeError(f"Backend has no method '{method_name}'")
        if method_name.startswith("_") or method_name in _INVOKE_DENYLIST:
            raise ValueError(f"Cannot invoke method '{method_name}'")

        sig = inspect.signature(method)
        sig_params = list(sig.parameters.items())

        # If the first parameter is named 'params' and annotated with a class,
        # treat the provided JSON dict as the dataclass constructor kwargs.
        if sig_params and sig_params[0][0] == "params":
            annotation: Any = _resolve_params_type(method)
            if inspect.isclass(annotation) and annotation is not inspect.Parameter.empty:
                param_obj = annotation(**params)
                return await typing.cast(typing.Awaitable[Any], method(param_obj))

        return await typing.cast(typing.Awaitable[Any], method(**params))

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=True,
            idempotentHint=False,
            openWorldHint=True,
        )
    )
    async def wavexis_invoke(input: InvokeInput) -> str:
        """Invoke any wavexis backend method by name, the ultimate escape hatch.

        Use a dedicated MCP tool (e.g. ``wavexis_act``, ``wavexis_navigate``)
        instead when one exists for the desired action; this tool exposes the
        full ``AbstractBackend`` API (e.g. ``page_print_to_pdf``, ``perf_trace``,
        ``runtime_evaluate``, ``pwa_install``) for methods without a wrapper.

        Side effects: May launch an ephemeral browser, navigate to a URL, and
        execute arbitrary backend methods; potentially destructive.
        Returns: JSON string with keys: 'status' ('ok'/'error'), 'type' (str),
        and either 'result' (any), 'base64' (str), or 'path' (str) depending on output.
        """
        ephemeral_sid: str | None = None
        backend: AbstractBackend | None = None
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
                    browser=input.browser,
                )

            if input.url:
                wait = session_manager.make_wait(
                    strategy=input.wait_strategy,
                    selector=input.wait_selector,
                    timeout=input.wait_timeout,
                )
                validate_url(input.url)
                await backend.navigate(input.url, wait)

            result = await _call_backend_method(backend, input.method, input.params)
            payload = await _build_result(result, input.output_path)
            return format_json_response(payload)
        except Exception as e:
            return format_error("wavexis_invoke", e)
        finally:
            if input.session_id is None and backend is not None:
                try:
                    await session_manager.release_backend(backend, ephemeral_sid)
                except Exception:
                    _logger.exception("Failed to release ephemeral backend after invoke")
