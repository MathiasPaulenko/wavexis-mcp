"""Network control tools for WaveXisMCP.

Provides tools for setting headers, user agent, blocking requests,
throttling network, disabling cache, capturing HAR, intercepting
requests, mocking responses, and listing network requests.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from wavexis.config import HarParams, ThrottleParams

from wavexis_mcp.formatter import format_error, format_json_response
from wavexis_mcp.models import (
    BlockRequestsInput,
    CaptureHARInput,
    GetRequestBodyInput,
    GetResponseBodyInput,
    InterceptRequestsInput,
    MockResponseInput,
    ModifyRequestInput,
    ModifyResponseInput,
    NetworkRequestsInput,
    ReplayHARInput,
    SetCacheDisabledInput,
    SetHeadersInput,
    SetUserAgentInput,
    ThrottleNetworkInput,
)
from wavexis_mcp.session import SessionManager

_THROTTLE_PRESETS: dict[str, dict[str, int | bool]] = {
    "none": {"offline": False, "latency_ms": 0, "download_bps": -1, "upload_bps": -1},
    "2g": {"offline": False, "latency_ms": 300, "download_bps": 28000, "upload_bps": 25600},
    "3g": {"offline": False, "latency_ms": 100, "download_bps": 160000, "upload_bps": 75000},
    "4g": {"offline": False, "latency_ms": 20, "download_bps": 4000000, "upload_bps": 3000000},
    "offline": {"offline": True, "latency_ms": 0, "download_bps": -1, "upload_bps": -1},
}


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
            await session.backend.set_headers(input.headers)
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
            session = session_manager.get(input.session_id)
            await session.backend.set_user_agent(input.user_agent)
            return format_json_response({"status": "ok"})
        except Exception as e:
            return format_error("wavexis_set_user_agent", e)

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
            backend, sid = await session_manager.acquire_backend(
                input.session_id,
                backend=input.backend,
                headless=input.headless,
            )
            try:
                params = HarParams(
                    url=input.url,
                    wait=input.wait_ms,
                    filter=input.filter,
                    timeout=input.timeout,
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
            input: Request listing parameters (filter, pagination).

        Returns:
            JSON string with paginated ``requests``, ``count``, and ``total``.
        """
        try:
            session = session_manager.get(input.session_id)
            raw = await session.backend.eval(
                "JSON.stringify(performance.getEntriesByType('resource').map(e => "
                "({url: e.name, method: 'GET', type: e.initiatorType, "
                "duration: e.duration, size: e.transferSize})))",
                await_promise=True,
            )
            import json

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
                    await backend.navigate(input.url)
                await backend.replay_har(input.har_path, input.url_filter)
                return format_json_response({"status": "ok", "har_path": input.har_path})
            finally:
                await session_manager.release_backend(backend, sid)
        except Exception as e:
            return format_error("wavexis_replay_har", e)
