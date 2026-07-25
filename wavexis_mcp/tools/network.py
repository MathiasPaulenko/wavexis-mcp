"""Network control tools for WaveXisMCP.

Provides tools for setting headers, user agent, blocking requests,
throttling network, disabling cache, capturing HAR, intercepting
requests, mocking responses, and listing network requests.
"""

from __future__ import annotations

import asyncio
import base64
import contextlib
import fnmatch
import functools
import json
from collections import deque
from collections.abc import Awaitable, Callable
from typing import Any, cast

import regex as _regex
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from wavexis.backend.base import AbstractBackend
from wavexis.config import HarParams, ThrottleParams

from wavexis_mcp.formatter import (
    _validate_header_value,
    format_error,
    format_json_response,
    secure_output_path,
    validate_url,
)
from wavexis_mcp.models import (
    BlockRequestsInput,
    CaptureHARInput,
    GetRequestBodyInput,
    GetResponseBodyInput,
    InterceptRequestsInput,
    MockResponseInput,
    ModifyRequestInput,
    ModifyResponseInput,
    NetworkClearInput,
    NetworkRequestInput,
    NetworkRequestsInput,
    ReplayHARInput,
    RouteInput,
    RouteListInput,
    SetCacheDisabledInput,
    SetHeadersInput,
    SetNetworkStateInput,
    SetUserAgentInput,
    ThrottleNetworkInput,
    UnrouteInput,
)
from wavexis_mcp.session import BrowserSession, SessionManager

# Headers that could be used to bypass security controls or perform
# request smuggling when set by an MCP client.
_BLOCKED_HEADERS = frozenset(
    {
        "host",
        "authorization",
        "proxy-authorization",
        "cookie",
        "set-cookie",
        "content-length",
        "transfer-encoding",
    }
)


def _backend(session: BrowserSession) -> AbstractBackend:
    """Return the session backend."""
    return session.backend


_THROTTLE_PRESETS: dict[str, dict[str, int | bool]] = {
    "none": {"offline": False, "latency_ms": 0, "download_bps": -1, "upload_bps": -1},
    "2g": {"offline": False, "latency_ms": 300, "download_bps": 28000, "upload_bps": 25600},
    "3g": {"offline": False, "latency_ms": 100, "download_bps": 160000, "upload_bps": 75000},
    "4g": {"offline": False, "latency_ms": 20, "download_bps": 4000000, "upload_bps": 3000000},
    "offline": {"offline": True, "latency_ms": 0, "download_bps": -1, "upload_bps": -1},
}


_NETWORK_LOG_MAX = 1000
_MAX_ROUTE_ENTRIES = 100
_MAX_PATTERN_LENGTH = 1000
_MAX_PATTERN_WILDCARDS = 50


@functools.lru_cache(maxsize=256)
def _glob_to_regex(pattern: str) -> Any:
    """Convert a Playwright-style glob pattern to a compiled regex."""
    if len(pattern) > _MAX_PATTERN_LENGTH:
        raise ValueError(f"Pattern exceeds {_MAX_PATTERN_LENGTH} characters")
    wildcard_count = pattern.count("*") + pattern.count("?")
    if wildcard_count > _MAX_PATTERN_WILDCARDS:
        raise ValueError(f"Pattern contains too many wildcards ({wildcard_count})")

    parts = []
    for i, segment in enumerate(pattern.split("**")):
        if i > 0:
            parts.append(".*")
        translated = (
            fnmatch.translate(segment)
            .replace(r"(?s:", "(?:")
            .replace(r"\Z", "")
            .replace(r"\z", "")
            .rstrip("$")
        )
        parts.append(translated)
    regex = "".join(parts)
    return _regex.compile(f"^{regex}$", _regex.IGNORECASE)


def _matches_pattern(pattern: str, url: str) -> bool:
    """Check if a URL matches a glob/wildcard pattern.

    Uses the ``regex`` package with a one-second timeout to avoid ReDoS
    attacks from malicious patterns.
    """
    try:
        return _glob_to_regex(pattern).match(url, timeout=1.0) is not None
    except Exception:
        return fnmatch.fnmatch(url, pattern)


# ── Network event log helpers ─────────────────────────────────────


def _init_network_log(session: BrowserSession) -> None:
    """Attach a per-session network event log to the backend if missing."""
    backend = cast(Any, _backend(session))
    if not isinstance(getattr(backend, "_network_log", None), deque):
        backend._network_log = deque(maxlen=_NETWORK_LOG_MAX)
        backend._network_log_map = {}
        backend._network_log_sub_id = None


def _on_network_event(session: BrowserSession, event: dict[str, Any]) -> None:
    """Callback for network_request / network_response events."""
    backend = cast(Any, _backend(session))
    _init_network_log(session)
    event_type = event.get("type")
    data = event.get("data", {})
    request_id = data.get("requestId")
    if not request_id:
        return

    if event_type == "network_request":
        request = data.get("request", {})
        entry = {
            "requestId": request_id,
            "url": request.get("url", ""),
            "method": request.get("method", "GET"),
            "type": data.get("resourceType", ""),
            "request_headers": request.get("headers", {}),
            "request_post_data": request.get("postData"),
            "timestamp": data.get("timestamp"),
            "response": None,
            "status": None,
            "response_headers": {},
        }
        backend._network_log.append(entry)
        backend._network_log_map[request_id] = entry
        while len(backend._network_log_map) > _NETWORK_LOG_MAX * 2 and backend._network_log_map:
            backend._network_log_map.pop(next(iter(backend._network_log_map)))
    elif event_type == "network_response":
        entry = backend._network_log_map.get(request_id)
        if entry:
            response = data.get("response", {})
            entry["response"] = response
            entry["status"] = response.get("status")
            entry["response_headers"] = response.get("headers", {})


async def _ensure_network_log(session: BrowserSession) -> list[dict[str, Any]]:
    """Ensure the backend is subscribed to network events; return the log."""
    _init_network_log(session)
    backend = cast(Any, _backend(session))
    if backend._network_log_sub_id is None:
        backend._network_log_sub_id = await asyncio.wait_for(
            backend.subscribe_events(
                ["network_request", "network_response"],
                lambda event: _on_network_event(session, event),
            ),
            timeout=10.0,
        )
        # Allow a short tick for any already-buffered events to arrive.
        await asyncio.sleep(0.01)
    return cast(list[dict[str, Any]], backend._network_log)


def _render_network_line(entry: dict[str, Any]) -> str:
    """Render a single network request line similar to Playwright MCP."""
    status = entry.get("status")
    method = entry.get("method", "GET")
    url = entry.get("url", "")
    if status:
        return f"[{method}] {url} => [{status}]"
    return f"[{method}] {url}"


def _is_fetch(entry: dict[str, Any]) -> bool:
    """Return True if the network entry is a fetch or XHR request."""
    return entry.get("type") in ("fetch", "xhr")


def _is_success(entry: dict[str, Any]) -> bool:
    """Return True if the network entry has an HTTP success status (< 400)."""
    status = entry.get("status")
    return status is not None and status < 400


# ── Route management helpers ────────────────────────────────────────


class _RouteEntry:
    """Internal representation of an active route/mock."""

    def __init__(
        self,
        pattern: str,
        status: int | None,
        body: str | None,
        content_type: str | None,
        add_headers: dict[str, str] | None,
        remove_headers: list[str] | None,
    ) -> None:
        self.pattern = pattern
        self.status = status
        self.body = body
        self.content_type = content_type
        self.add_headers = add_headers if add_headers is not None else {}
        self.remove_headers = remove_headers if remove_headers is not None else []


def _parse_header_list(headers: list[str] | None) -> dict[str, str]:
    """Parse 'Name: Value' header strings into a dict."""
    result: dict[str, str] = {}
    if not headers:
        return result
    for h in headers:
        if ":" not in h:
            continue
        k, v = h.split(":", 1)
        result[k.strip()] = v.strip()
    return result


def _init_routes(session: BrowserSession) -> None:
    """Attach per-session route state to the backend."""
    backend = cast(Any, _backend(session))
    if not isinstance(getattr(backend, "_route_entries", None), deque):
        backend._route_entries = deque(maxlen=_MAX_ROUTE_ENTRIES)
        backend._route_handler = None


def _build_route_handler(
    session: BrowserSession,
) -> Callable[[dict[str, Any]], Awaitable[None]]:
    """Build an async handler for Fetch.requestPaused events."""
    backend = cast(Any, _backend(session))

    async def handler(event_params: dict[str, Any]) -> None:
        request_id = event_params.get("requestId", "")
        request = event_params.get("request", {})
        url = request.get("url", "")
        for route in backend._route_entries:
            if not _matches_pattern(route.pattern, url):
                continue
            if route.body is not None or route.status is not None:
                body = route.body or ""
                if isinstance(body, dict | list):
                    body = json.dumps(body)
                body_b64 = base64.b64encode(body.encode("utf-8")).decode("ascii")
                response_headers = []
                if route.content_type:
                    response_headers.append({"name": "Content-Type", "value": route.content_type})
                with contextlib.suppress(Exception):
                    await backend.raw(
                        "Fetch.fulfillRequest",
                        {
                            "requestId": request_id,
                            "responseCode": route.status or 200,
                            "responseHeaders": response_headers,
                            "body": body_b64,
                        },
                    )
                return
            # Continue with header modifications.
            headers = {**request.get("headers", {})}
            for k, v in route.add_headers.items():
                headers[k] = v
            for k in route.remove_headers:
                remove_low = k.lower()
                for header_name in list(headers):
                    if header_name.lower() == remove_low:
                        headers.pop(header_name, None)
            with contextlib.suppress(Exception):
                await backend.raw(
                    "Fetch.continueRequest",
                    {
                        "requestId": request_id,
                        "headers": [{"name": k, "value": v} for k, v in headers.items()],
                    },
                )
            return
        # No match: continue unchanged.
        with contextlib.suppress(Exception):
            await backend.raw("Fetch.continueRequest", {"requestId": request_id})

    return handler


async def _refresh_routes(session: BrowserSession) -> None:
    """Re-enable Fetch interception with the current route patterns."""
    backend = cast(Any, _backend(session))
    _init_routes(session)
    # Detach previous handler if present.
    if backend._route_handler:
        with contextlib.suppress(Exception):
            cdp_session = backend._require_session()
            cdp_session.off("Fetch.requestPaused", backend._route_handler)

    if not backend._route_entries:
        with contextlib.suppress(Exception):
            await backend.raw("Fetch.disable", {})
        backend._route_handler = None
        return

    patterns = [
        {"urlPattern": route.pattern, "requestStage": "Request"} for route in backend._route_entries
    ]
    handler = _build_route_handler(session)
    backend._route_handler = handler
    with contextlib.suppress(Exception):
        cdp_session = backend._require_session()
        cdp_session.on("Fetch.requestPaused", handler)
        # Disable any previous Fetch interception before enabling with new patterns.
        await backend.raw("Fetch.disable", {})
        await backend.raw("Fetch.enable", {"patterns": patterns})


def register(mcp: FastMCP, session_manager: SessionManager) -> None:
    """Register all network tools on the FastMCP server.

    Args:
        mcp: The FastMCP server instance.
        session_manager: The shared session manager.
    """

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def wavexis_set_headers(input: SetHeadersInput) -> str:
        """Set extra HTTP headers for all subsequent requests.

        Args:
            input: Headers parameters.

        Returns:
            JSON string with status ``"ok"``.
        """
        try:
            session = session_manager.get(input.session_id)
            for name, value in input.headers.items():
                _validate_header_value(name, value)
            filtered = {k: v for k, v in input.headers.items() if k.lower() not in _BLOCKED_HEADERS}
            await session.backend.set_headers(filtered)
            return format_json_response({"status": "ok"})
        except Exception as e:
            return format_error("wavexis_set_headers", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def wavexis_set_user_agent(input: SetUserAgentInput) -> str:
        """Set a custom User-Agent string for all subsequent requests.

        Args:
            input: User agent parameters.

        Returns:
            JSON string with status ``"ok"``.
        """
        try:
            _validate_header_value("User-Agent", input.user_agent)
            session = session_manager.get(input.session_id)
            await session.backend.set_user_agent(input.user_agent)
            return format_json_response({"status": "ok"})
        except Exception as e:
            return format_error("wavexis_set_user_agent", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def wavexis_set_network_state(input: SetNetworkStateInput) -> str:
        """Override the browser network state to online or offline.

        Args:
            input: Network state parameters.

        Returns:
            JSON string with status ``"ok"`` and ``"state"``.
        """
        try:
            session = session_manager.get(input.session_id)
            state = {
                "offline": input.state == "offline",
                "latency": 0,
                "downloadThroughput": -1,
                "uploadThroughput": -1,
            }
            await session.backend.network_override_network_state(state)
            return format_json_response({"status": "ok", "state": input.state})
        except Exception as e:
            return format_error("wavexis_set_network_state", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=True,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def wavexis_block_requests(input: BlockRequestsInput) -> str:
        """Block requests matching URL patterns.

        Args:
            input: Block parameters (patterns).

        Returns:
            JSON string with status ``"ok"`` and ``blocked_patterns``.
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.block_requests(input.patterns)
            return format_json_response({"status": "ok", "patterns": input.patterns})
        except Exception as e:
            return format_error("wavexis_block_requests", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def wavexis_throttle_network(input: ThrottleNetworkInput) -> str:
        """Throttle network speed to emulate slow connections.

        Args:
            input: Throttle parameters (preset or custom values).

        Returns:
            JSON string with status ``"ok"``.
        """
        try:
            session = session_manager.get(input.session_id)
            if input.preset and input.preset in _THROTTLE_PRESETS:
                preset = _THROTTLE_PRESETS[input.preset]
                params = ThrottleParams(
                    offline=bool(preset["offline"]),
                    latency_ms=int(preset["latency_ms"]),
                    download_bps=int(preset["download_bps"]),
                    upload_bps=int(preset["upload_bps"]),
                )
            else:
                params = ThrottleParams(
                    offline=input.offline,
                    latency_ms=input.latency_ms,
                    download_bps=input.download_bps,
                    upload_bps=input.upload_bps,
                )
            await session.backend.throttle_network(params)
            return format_json_response({"status": "ok"})
        except Exception as e:
            return format_error("wavexis_throttle_network", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def wavexis_set_cache_disabled(input: SetCacheDisabledInput) -> str:
        """Enable or disable browser cache.

        Args:
            input: Cache disable parameters.

        Returns:
            JSON string with status ``"ok"`` and ``cache_disabled``.
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.set_cache_disabled(input.disabled)
            return format_json_response({"status": "ok", "cache_disabled": input.disabled})
        except Exception as e:
            return format_error("wavexis_set_cache_disabled", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=True,
        )
    )
    async def wavexis_capture_har(input: CaptureHARInput) -> str:
        """Capture HAR (HTTP Archive) data for a page load.

        Args:
            input: HAR capture parameters (URL, wait, filter).

        Returns:
            JSON string with ``har`` data and ``entries`` count.
        """
        try:
            if input.url:
                validate_url(input.url)
            backend, sid = await session_manager.acquire_backend(
                input.session_id,
                backend=input.backend,
                headless=input.headless,
            )
            try:
                params = HarParams(
                    url=input.url,
                    wait=session_manager.make_wait(strategy="load", timeout=input.timeout),
                    filter=input.filter,
                    timeout=input.wait_ms,
                )
                har = await backend.capture_har(params)
                entries = len(har.get("log", {}).get("entries", [])) if isinstance(har, dict) else 0
                return format_json_response({"har": har, "entries": entries})
            finally:
                await session_manager.release_backend(backend, sid)
        except Exception as e:
            return format_error("wavexis_capture_har", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=True,
            idempotentHint=False,
            openWorldHint=False,
        )
    )
    async def wavexis_intercept_requests(input: InterceptRequestsInput) -> str:
        """Register a request interception pattern.

        Args:
            input: Interception parameters.

        Returns:
            JSON string with status ``"ok"``.
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.intercept_requests(dict(input.pattern))
            return format_json_response({"status": "ok", "pattern": input.pattern})
        except Exception as e:
            return format_error("wavexis_intercept_requests", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=True,
            idempotentHint=False,
            openWorldHint=False,
        )
    )
    async def wavexis_mock_response(input: MockResponseInput) -> str:
        """Register a mock response for a URL pattern.

        Args:
            input: Mock response parameters.

        Returns:
            JSON string with status ``"ok"``.
        """
        try:
            session = session_manager.get(input.session_id)
            response = {
                "status": input.status,
                "contentType": input.content_type,
                "body": input.body,
                "headers": input.headers,
            }
            await session.backend.mock_response(input.url, response)
            return format_json_response({"status": "ok", "url": input.url})
        except Exception as e:
            return format_error("wavexis_mock_response", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=True,
        )
    )
    async def wavexis_network_requests(input: NetworkRequestsInput) -> str:
        """List network requests since page load with pagination.

        Args:
            input: Request listing parameters (filter, pagination, mode).

        Returns:
            JSON string with paginated ``requests``, ``count``, and ``total``.
        """
        try:
            session = session_manager.get(input.session_id)

            if input.mode == "events":
                log = await _ensure_network_log(session)
                all_requests: list[dict[str, Any]] = []
                for idx, entry in enumerate(log, start=1):
                    all_requests.append(
                        {
                            "index": idx,
                            "method": entry.get("method", "GET"),
                            "url": entry.get("url", ""),
                            "status": entry.get("status"),
                            "type": entry.get("type", ""),
                        }
                    )

                if input.filter:
                    if len(input.filter) > 1000:
                        raise ValueError("Filter pattern exceeds maximum length of 1000 characters")
                    try:
                        rx = _regex.compile(input.filter, _regex.IGNORECASE)
                        all_requests = [
                            r for r in all_requests if rx.search(r.get("url", ""), timeout=1.0)
                        ]
                    except Exception:
                        all_requests = [r for r in all_requests if input.filter in r.get("url", "")]
                if input.resource_type:
                    all_requests = [r for r in all_requests if r.get("type") == input.resource_type]

                total = len(all_requests)
                paginated = all_requests[input.offset : input.offset + input.limit]
                return format_json_response(
                    {
                        "requests": paginated,
                        "count": len(paginated),
                        "total": total,
                    }
                )

            # Legacy performance.getEntriesByType mode (default).
            raw = await session.backend.eval(
                "JSON.stringify(performance.getEntriesByType('resource').map(e => "
                "({url: e.name, method: 'GET', type: e.initiatorType, "
                "duration: e.duration, size: e.transferSize})))",
                await_promise=True,
            )
            all_requests = json.loads(raw) if isinstance(raw, str) else raw

            if input.filter:
                all_requests = [r for r in all_requests if input.filter in r.get("url", "")]
            if input.resource_type:
                all_requests = [r for r in all_requests if r.get("type") == input.resource_type]

            total = len(all_requests)
            paginated = all_requests[input.offset : input.offset + input.limit]
            return format_json_response(
                {
                    "requests": paginated,
                    "count": len(paginated),
                    "total": total,
                }
            )
        except Exception as e:
            return format_error("wavexis_network_requests", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def wavexis_get_request_body(input: GetRequestBodyInput) -> str:
        """Get the body of a network request by ID (W3).

        Args:
            input: Request body parameters (session_id, request_id).

        Returns:
            JSON string with ``body`` or ``error`` if not available.
        """
        try:
            session = session_manager.get(input.session_id)
            body = await session.backend.get_request_body(input.request_id)
            if body is None:
                return format_json_response({"body": None, "found": False})
            return format_json_response({"body": body, "found": True})
        except Exception as e:
            return format_error("wavexis_get_request_body", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def wavexis_get_response_body(input: GetResponseBodyInput) -> str:
        """Get the body of a network response by ID (W3).

        Args:
            input: Response body parameters (session_id, request_id).

        Returns:
            JSON string with ``body`` or ``error`` if not available.
        """
        try:
            session = session_manager.get(input.session_id)
            body = await session.backend.get_response_body(input.request_id)
            if body is None:
                return format_json_response({"body": None, "found": False})
            return format_json_response({"body": body, "found": True})
        except Exception as e:
            return format_error("wavexis_get_response_body", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def wavexis_network_request(input: NetworkRequestInput) -> str:
        """Return full details for a single network request by index.

        Use the index from ``wavexis_network_requests`` with ``mode="events"``.
        """
        try:
            session = session_manager.get(input.session_id)
            log = await _ensure_network_log(session)
            if input.index < 1 or input.index > len(log):
                return format_json_response({"error": f"Request #{input.index} not found"})

            entry = log[input.index - 1]
            request_id = entry.get("requestId")
            result: dict[str, Any] = {
                "index": input.index,
                "method": entry.get("method", "GET"),
                "url": entry.get("url", ""),
                "type": entry.get("type", ""),
                "status": entry.get("status"),
            }

            if input.part in (None, "request-headers"):
                result["request_headers"] = entry.get("request_headers", {})
            if input.part in (None, "response-headers"):
                result["response_headers"] = entry.get("response_headers", {})

            if input.part in (None, "request-body") and request_id:
                try:
                    result["request_body"] = await session.backend.network_get_request_post_data(
                        request_id
                    )
                except Exception:
                    result["request_body"] = None

            if input.part in (None, "response-body") and request_id:
                try:
                    result["response_body"] = await session.backend.get_response_body(request_id)
                except Exception:
                    result["response_body"] = None

            return format_json_response(result)
        except Exception as e:
            return format_error("wavexis_network_request", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=True,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def wavexis_network_clear(input: NetworkClearInput) -> str:
        """Clear the network event log."""
        try:
            session = session_manager.get(input.session_id)
            _init_network_log(session)
            backend = cast(Any, _backend(session))
            backend._network_log.clear()
            backend._network_log_map.clear()
            return format_json_response({"status": "ok"})
        except Exception as e:
            return format_error("wavexis_network_clear", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        )
    )
    async def wavexis_modify_request(input: ModifyRequestInput) -> str:
        """Intercept and modify requests matching a pattern in-flight (W6).

        Args:
            input: Modification parameters (pattern, modifications).

        Returns:
            JSON string with status ``"ok"``.
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.modify_request(input.pattern, input.modifications)
            return format_json_response({"status": "ok", "pattern": input.pattern})
        except Exception as e:
            return format_error("wavexis_modify_request", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        )
    )
    async def wavexis_modify_response(input: ModifyResponseInput) -> str:
        """Intercept and modify responses matching a pattern in-flight.

        Args:
            input: Modification parameters (pattern, modifications).

        Returns:
            JSON string with status ``"ok"``.
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.modify_response(input.pattern, input.modifications)
            return format_json_response({"status": "ok", "pattern": input.pattern})
        except Exception as e:
            return format_error("wavexis_modify_response", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=True,
        )
    )
    async def wavexis_replay_har(input: ReplayHARInput) -> str:
        """Replay network requests from a HAR file (W7).

        Args:
            input: HAR replay parameters (har_path, url_filter, url).

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
                    validate_url(input.url)
                    await backend.navigate(input.url)
                har_path = str(secure_output_path(input.har_path))
                await backend.replay_har(har_path, input.url_filter)
                return format_json_response({"status": "ok", "har_path": har_path})
            finally:
                await session_manager.release_backend(backend, sid)
        except Exception as e:
            return format_error("wavexis_replay_har", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        )
    )
    async def wavexis_route(input: RouteInput) -> str:
        """Add a network route/mock or header modification rule.

        If ``status`` or ``body`` is provided, matching requests are fulfilled
        with a mocked response. Otherwise the request is continued with the
        supplied header changes.
        """
        try:
            session = session_manager.get(input.session_id)
            _init_routes(session)
            backend = cast(Any, _backend(session))
            parsed_headers = _parse_header_list(input.headers)
            add_headers = {
                name: value
                for name, value in parsed_headers.items()
                if name.lower() not in _BLOCKED_HEADERS
            }
            for name, value in add_headers.items():
                _validate_header_value(name, value)
            remove_headers = (
                [h.strip() for h in input.remove_headers.split(",") if h.strip()]
                if input.remove_headers
                else []
            )
            route = _RouteEntry(
                pattern=input.pattern,
                status=input.status,
                body=input.body,
                content_type=input.content_type,
                add_headers=add_headers,
                remove_headers=remove_headers,
            )
            backend._route_entries.append(route)
            await _refresh_routes(session)
            return format_json_response({"status": "ok", "pattern": input.pattern})
        except Exception as e:
            return format_error("wavexis_route", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def wavexis_route_list(input: RouteListInput) -> str:
        """List all active network routes/mocks."""
        try:
            session = session_manager.get(input.session_id)
            _init_routes(session)
            backend = cast(Any, _backend(session))
            routes = [
                {
                    "pattern": r.pattern,
                    "status": r.status,
                    "body": r.body[:50] + "..." if r.body and len(r.body) > 50 else r.body,
                    "content_type": r.content_type,
                    "add_headers": r.add_headers,
                    "remove_headers": r.remove_headers,
                }
                for r in backend._route_entries
            ]
            return format_json_response({"routes": routes, "count": len(routes)})
        except Exception as e:
            return format_error("wavexis_route_list", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=True,
            idempotentHint=False,
            openWorldHint=False,
        )
    )
    async def wavexis_unroute(input: UnrouteInput) -> str:
        """Remove network routes matching a pattern, or all routes."""
        try:
            session = session_manager.get(input.session_id)
            _init_routes(session)
            backend = cast(Any, _backend(session))
            before = len(backend._route_entries)
            if input.pattern:
                backend._route_entries = deque(
                    (r for r in backend._route_entries if r.pattern != input.pattern),
                    maxlen=_MAX_ROUTE_ENTRIES,
                )
            else:
                backend._route_entries.clear()
            removed = before - len(backend._route_entries)
            await _refresh_routes(session)
            return format_json_response({"removed": removed})
        except Exception as e:
            return format_error("wavexis_unroute", e)
