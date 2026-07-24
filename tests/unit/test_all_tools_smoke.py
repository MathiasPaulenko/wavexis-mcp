"""Generic smoke tests for every registered tool.

The goal is to exercise the happy path of every tool with a cooperative
mock backend and plausible default inputs. Tools that cannot succeed with
pure mocks (e.g. they require a real browser event) are exercised up to the
point where the mock returns a safe value, which still contributes to line
coverage and catches import/registration errors.
"""

from __future__ import annotations

import inspect
from typing import Any, Literal, Union, get_args, get_origin
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import BaseModel

import wavexis_mcp.server as _server_module
from wavexis_mcp.server import create_server
from wavexis_mcp.session import SessionManager


class _MockBackend:
    """Backend whose every method returns a safe default coroutine."""

    _backend_name = "cdp"

    def _default(self, name: str, *args: Any, **kwargs: Any) -> Any:
        n = name.lower()
        if "screenshot" in n or "pdf" in n or "download" in n or "video" in n:
            return b""
        if "har" in n or "image" in n or "bytes" in n or "blob" in n:
            return b""
        if n.startswith("eval"):
            return "{}"
        if "find_by_text" in n:
            return "button:has-text('Submit')"
        if "generate_locator" in n:
            return "css=button"
        if "get_url" in n or "current_url" in n:
            return "https://example.com"
        if "get_title" in n:
            return "Example"
        if "outer_html" in n:
            return "<div></div>"
        if "inner_text" in n:
            return "text"
        if "get_attribute" in n and "attributes" not in n:
            return "value"
        if "list_" in n or "get_cookies" in n or "get_tabs" in n or "get_targets" in n:
            return []
        if (
            "tree" in n
            or "snapshot" in n
            or "state" in n
            or "metrics" in n
            or "info" in n
            or "version" in n
            or "bounds" in n
            or "box" in n
        ):
            return {}
        if "console" in n and "messages" in n:
            return []
        if "storage" in n:
            return {}
        if "start_combined_trace" in n:
            return "trace-id"
        if "stop_combined_trace" in n:
            return {"trace": b"", "screenshots": [], "network": []}
        if "perf_trace" in n:
            return b""
        if "tracing" in n and "start" in n:
            return None
        if "tracing" in n and "end" in n:
            return {}
        if n in {"find", "find_all", "query_selector_all"}:
            return []
        if n in {"query_selector"}:
            return None
        if "raw" in n or "invoke" in n:
            return {}
        if "network_get_request_post_data" in n:
            return ""
        if "get_response_body" in n:
            return ""
        if "network_requests" in n:
            return "[]"
        return None

    def __getattr__(self, name: str) -> Any:
        async def _method(*args: Any, **kwargs: Any) -> Any:
            return self._default(name, *args, **kwargs)

        return _method

    def _require_session(self) -> Any:
        from unittest.mock import MagicMock

        sess = MagicMock()
        sess.on = MagicMock()
        sess.off = MagicMock()
        sess.send = AsyncMock()
        return sess


class _AsyncIterator:
    def __init__(self, iterable: list[Any]) -> None:
        self._it = iter(iterable)

    def __aiter__(self) -> Any:
        return self

    async def __anext__(self) -> Any:
        try:
            return next(self._it)
        except StopIteration:
            raise StopAsyncIteration from None


def _is_optional(annotation: Any) -> bool:
    origin = get_origin(annotation)
    return origin is Union and type(None) in get_args(annotation)


def _first_literal_value(annotation: Any) -> Any:
    args = get_args(annotation)
    if args:
        return args[0]
    return None


def _min_len(info: Any) -> int | None:
    for meta in info.metadata:
        if hasattr(meta, "min_length"):
            return int(meta.min_length)
    return None


def _pattern(info: Any) -> str | None:
    for meta in info.metadata:
        if hasattr(meta, "pattern"):
            return str(meta.pattern)
    return None


def _pattern_example(pattern: str) -> str:
    if pattern == r"^(online|offline)$":
        return "online"
    if pattern.startswith("^") and pattern.endswith("$"):
        # Very rough fallback: use the first alternative literal if available.
        inner = pattern[1:-1].strip("()")
        if "|" in inner:
            return inner.split("|")[0].strip("'\"") or "test"
    return "test"


def _default_for_field(name: str, info: Any, session_id: str | None) -> Any:
    """Return a value that satisfies a Pydantic field."""
    from pydantic.fields import FieldInfo
    from pydantic_core import PydanticUndefined

    if not isinstance(info, FieldInfo):
        return None

    if name == "session_id":
        return session_id

    # If the field has an explicit default, use it.
    if info.default not in (PydanticUndefined, ..., None) or (
        info.default is None and not info.is_required()
    ):
        return info.default

    ann = info.annotation
    if ann is None:
        return None

    if _is_optional(ann):
        # For optional fields we try a concrete value first, except url/stateless toggles.
        if name in {"url"}:
            return None
        inner = next((a for a in get_args(ann) if a is not type(None)), str)
        return _default_for_annotation(inner)

    return _default_for_annotation(ann)


def _default_for_annotation(ann: Any) -> Any:
    origin = get_origin(ann)
    args = get_args(ann)

    if origin is list or ann is list:
        return []
    if origin is dict or ann is dict:
        return {}
    if origin is Literal:
        return _first_literal_value(ann)
    if ann is str:
        return "test"
    if ann is int:
        return 0
    if ann is float:
        return 0.0
    if ann is bool:
        return False
    if origin is Union:
        for candidate in args:
            if candidate is type(None):
                continue
            return _default_for_annotation(candidate)
    if isinstance(ann, type) and issubclass(ann, BaseModel):
        return _build_model_instance(ann, None)
    return None


def _numeric_bounds(info: Any) -> tuple[float | None, float | None]:
    """Return (ge, le) numeric bounds from field metadata."""
    ge = le = None
    for meta in info.metadata:
        if hasattr(meta, "ge"):
            ge = meta.ge
        if hasattr(meta, "le"):
            le = meta.le
    return ge, le


def _clamp_numeric(value: Any, info: Any) -> Any:
    ge, le = _numeric_bounds(info)
    if isinstance(value, (int, float)):
        if ge is not None:
            value = max(value, ge)
        if le is not None:
            value = min(value, le)
    return value


def _build_model_instance(model_cls: type[BaseModel], session_id: str | None) -> BaseModel:
    from pydantic.fields import FieldInfo

    values: dict[str, Any] = {}
    for name, info in model_cls.model_fields.items():
        if not isinstance(info, FieldInfo):
            values[name] = None
            continue

        value = _default_for_field(name, info, session_id)

        # String constraints.
        if get_origin(info.annotation) in (str, None) and info.annotation is str:
            pat = _pattern(info)
            if pat:
                value = _pattern_example(pat)
            min_len = _min_len(info)
            if min_len and isinstance(value, str) and len(value) < min_len:
                value = value * (min_len // len(value) + 1)

        # Numeric constraints.
        value = _clamp_numeric(value, info)

        # List constraints.
        origin = get_origin(info.annotation)
        if origin is list:
            min_len = _min_len(info)
            if min_len and isinstance(value, list) and len(value) < min_len:
                item_type = next((a for a in get_args(info.annotation) if a is not type(None)), str)
                value = [_default_for_annotation(item_type) for _ in range(min_len)]

        values[name] = value
    return model_cls.model_validate(values)


def _input_model_for_tool(tool: Any) -> type[BaseModel] | None:
    sig = inspect.signature(tool.fn)
    params = list(sig.parameters.values())
    if not params:
        return None
    param = params[0]
    ann = param.annotation
    if isinstance(ann, str):
        ann = tool.fn.__globals__.get(ann)
    if isinstance(ann, type) and issubclass(ann, BaseModel):
        return ann
    raise ValueError(f"Cannot resolve input model for {tool.name}")


def _build_input(tool: Any, session_id: str) -> BaseModel | None:
    model_cls = _input_model_for_tool(tool)
    if model_cls is None:
        return None
    return _build_model_instance(model_cls, session_id)


@pytest.mark.unit
async def test_all_tools_smoke(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    """Call every registered tool with safe defaults and a mock backend."""
    _server_module._session_manager = session_manager_with_mock

    # Prevent real browser launches from stateful/session tools.
    session_manager_with_mock.open = AsyncMock(return_value="new-session")
    session_manager_with_mock.close = AsyncMock()

    with patch("wavexis.backend.manager.BackendManager") as mock_mgr_cls:
        mock_mgr = MagicMock()
        mock_mgr.list_available = MagicMock(return_value=["cdp"])
        mock_mgr.install_check = MagicMock(return_value={"cdp": "1.0.0"})
        mock_mgr_cls.return_value = mock_mgr

        mcp = create_server(caps="all")
        backend = _MockBackend()

        # Replace the backend of the mock session with our generic one.
        session = session_manager_with_mock.get(mock_session_id)
        session.backend = backend

        failures: list[tuple[str, str]] = []
        tool_names = sorted(mcp._tool_manager._tools.keys())

        for name in tool_names:
            tool = mcp._tool_manager.get_tool(name)
            try:
                inp = _build_input(tool, mock_session_id)
            except Exception as exc:  # pragma: no cover - defensive
                failures.append((name, f"input build: {exc}"))
                continue

            try:
                if inp is None:
                    result = await tool.fn()
                else:
                    result = await tool.fn(inp)
            except Exception as exc:
                failures.append((name, f"{type(exc).__name__}: {exc}"))
                continue

            if not isinstance(result, str):
                failures.append((name, f"non-string result: {type(result)}"))

    if failures:
        msg = "\n".join(f"  {n}: {e}" for n, e in failures[:20])
        pytest.fail(f"{len(failures)} tools failed smoke test:\n{msg}")


class _FailingBackend:
    """Backend whose every method raises, to exercise tool except blocks."""

    _backend_name = "cdp"

    def __getattr__(self, name: str) -> Any:
        async def _failing(*args: Any, **kwargs: Any) -> Any:
            raise RuntimeError("mock backend failure")

        return _failing


@pytest.mark.unit
async def test_all_tools_error_smoke(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    """Call every tool with a failing backend to cover error branches."""
    _server_module._session_manager = session_manager_with_mock
    session_manager_with_mock.open = AsyncMock(return_value="new-session")
    session_manager_with_mock.close = AsyncMock()

    with patch("wavexis.backend.manager.BackendManager") as mock_mgr_cls:
        mock_mgr = MagicMock()
        mock_mgr.list_available = MagicMock(return_value=["cdp"])
        mock_mgr.install_check = MagicMock(return_value={"cdp": "1.0.0"})
        mock_mgr_cls.return_value = mock_mgr

        mcp = create_server(caps="all")
        session = session_manager_with_mock.get(mock_session_id)
        session.backend = _FailingBackend()

        failures: list[tuple[str, str]] = []
        for name in sorted(mcp._tool_manager._tools.keys()):
            tool = mcp._tool_manager.get_tool(name)
            try:
                inp = _build_input(tool, mock_session_id)
                if inp is None:
                    result = await tool.fn()
                else:
                    result = await tool.fn(inp)
            except Exception as exc:
                failures.append((name, f"unhandled {type(exc).__name__}: {exc}"))
                continue
            if not isinstance(result, str):
                failures.append((name, f"non-string result: {type(result)}"))

        if failures:
            msg = "\n".join(f"  {n}: {e}" for n, e in failures[:20])
            pytest.fail(f"{len(failures)} tools failed error smoke test:\n{msg}")


@pytest.mark.unit
async def test_all_tools_output_path_smoke(
    session_manager_with_mock: SessionManager, mock_session_id: str, tmp_path: Any
) -> None:
    """Call every tool with output_path set where available to exercise save-to-file branches."""
    _server_module._session_manager = session_manager_with_mock
    session_manager_with_mock.open = AsyncMock(return_value="new-session")
    session_manager_with_mock.close = AsyncMock()

    with patch("wavexis.backend.manager.BackendManager") as mock_mgr_cls:
        mock_mgr = MagicMock()
        mock_mgr.list_available = MagicMock(return_value=["cdp"])
        mock_mgr.install_check = MagicMock(return_value={"cdp": "1.0.0"})
        mock_mgr_cls.return_value = mock_mgr

        mcp = create_server(caps="all")
        backend = _MockBackend()

        session = session_manager_with_mock.get(mock_session_id)
        session.backend = backend

        output_path = str(tmp_path / "out")
        failures: list[tuple[str, str]] = []
        for name in sorted(mcp._tool_manager._tools.keys()):
            tool = mcp._tool_manager.get_tool(name)
            try:
                inp = _build_input(tool, mock_session_id)
                if inp is not None and "output_path" in inp.model_fields:
                    inp = inp.model_copy(update={"output_path": output_path})
            except Exception as exc:
                failures.append((name, f"input build: {exc}"))
                continue

            try:
                if inp is None:
                    result = await tool.fn()
                else:
                    result = await tool.fn(inp)
            except Exception as exc:
                failures.append((name, f"{type(exc).__name__}: {exc}"))
                continue

            if not isinstance(result, str):
                failures.append((name, f"non-string result: {type(result)}"))

        if failures:
            msg = "\n".join(f"  {n}: {e}" for n, e in failures[:20])
            pytest.fail(f"{len(failures)} tools failed output-path smoke test:\n{msg}")
