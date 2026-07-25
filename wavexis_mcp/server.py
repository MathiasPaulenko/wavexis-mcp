"""WaveXisMCP server — FastMCP entry point.

This module creates and configures the FastMCP server instance,
registers tool modules based on enabled capability tiers, and
provides the ``main`` CLI entry point with support for both
stdio and HTTP transports.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import AbstractAsyncContextManager, asynccontextmanager, suppress
from typing import cast

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.tools import Tool
from mcp.types import ToolAnnotations
from pydantic import BaseModel

from wavexis_mcp.caps import ALL_TIERS, CapsManager
from wavexis_mcp.formatter import format_error, format_json_response
from wavexis_mcp.models import ActInput
from wavexis_mcp.rate_limiter import RateLimiter
from wavexis_mcp.session import SessionManager


def _make_lifespan(
    session_manager: SessionManager,
) -> Callable[[FastMCP], AbstractAsyncContextManager[None]]:
    """Create a lifespan context manager that cleans up *session_manager* on shutdown."""

    @asynccontextmanager
    async def _lifespan(_app: FastMCP) -> AsyncIterator[None]:
        """Manage server lifecycle — cleanup sessions on shutdown.

        Args:
            _app: The FastMCP application instance (unused).

        Yields:
            ``None`` — control returns to the server after cleanup.
        """
        try:
            yield
        finally:
            with suppress(Exception):
                await session_manager.cleanup_all()

    return _lifespan


def _print_startup_info(caps_manager: CapsManager) -> None:
    """Print enabled tiers and tool count to stderr.

    Args:
        caps_manager: The caps manager to query.
    """
    tiers = sorted(caps_manager.enabled_tiers())
    print(
        f"WaveXisMCP — enabled tiers: {', '.join(tiers)}",
        file=sys.stderr,
    )


def parse_caps(argv: list[str] | None = None) -> str:
    """Parse ``--caps`` from command line arguments.

    Args:
        argv: Argument list to parse.  Defaults to ``sys.argv[1:]``.

    Returns:
        The caps string value, or ``"core"`` if not specified.
    """
    args = argv if argv is not None else sys.argv[1:]
    for i, arg in enumerate(args):
        if arg == "--caps" and i + 1 < len(args):
            return args[i + 1]
        if arg.startswith("--caps="):
            return arg.split("=", 1)[1]
    return "core"


def _is_help_request(argv: list[str] | None = None) -> bool:
    """Check if --help is in the arguments.

    Args:
        argv: Argument list to check.

    Returns:
        True if --help or -h is present.
    """
    args = argv if argv is not None else sys.argv[1:]
    return "--help" in args or "-h" in args


def create_server(
    caps: str = "core",
    rate_limit: int = 60,
    rate_burst: int = 10,
    session_manager: SessionManager | None = None,
) -> FastMCP:
    """Create and configure the FastMCP server with the given capability tiers.

    Core tools are always registered.  Additional tiers are registered
    only when enabled via the *caps* string.  M1-M4 features (act,
    resources, prompts, rate limiting) are also registered here.

    Each call returns an isolated ``FastMCP`` instance with its own
    ``SessionManager`` and ``CapsManager`` so servers can be created
    repeatedly without sharing global state.

    Args:
        caps: Comma-separated tier names or ``"all"``.
        rate_limit: Maximum tool calls per second per session.
        rate_burst: Maximum burst size for rate limiting.
        session_manager: Optional existing ``SessionManager`` to use
            (primarily for testing).  If omitted, a new instance is created.

    Returns:
        A configured ``FastMCP`` instance with all enabled tools registered.
    """
    caps_manager = CapsManager(caps)
    rate_limiter = RateLimiter(rate=rate_limit, burst=rate_burst)
    session_manager = session_manager or SessionManager()
    session_manager.rate_limiter = rate_limiter

    mcp = FastMCP(
        "wavexis-mcp",
        lifespan=_make_lifespan(session_manager),
        instructions=(
            "WaveXisMCP — browser automation via wavexis. "
            f"Enabled tiers: {', '.join(sorted(caps_manager.enabled_tiers()))}. "
            "Use wavexis_session_open for multi-step workflows, "
            "or pass 'url' for stateless one-shot calls. "
            "Use wavexis_act for natural language interaction."
        ),
    )

    # Expose internals for ``main()`` and tests without module-level globals.
    mcp._wavexis_session_manager = session_manager  # type: ignore[attr-defined]
    mcp._wavexis_rate_limiter = rate_limiter  # type: ignore[attr-defined]
    mcp._wavexis_caps_manager = caps_manager  # type: ignore[attr-defined]

    from wavexis_mcp.tools import (
        a11y,
        capture,
        cookies,
        data,
        devtools,
        dom,
        emulation,
        experimental,
        input,
        interactions,
        javascript,
        navigation,
        network,
        playwright_parity,
        session,
        storage,
        tabs,
        testing,
        utility,
        video,
        vision,
        workflows,
    )

    session.register(mcp, session_manager)
    navigation.register(mcp, session_manager)
    capture.register(mcp, session_manager)
    javascript.register(mcp, session_manager)
    dom.register(mcp, session_manager)
    input.register(mcp, session_manager)
    cookies.register(mcp, session_manager)
    tabs.register(mcp, session_manager)
    utility.register(mcp, session_manager)
    playwright_parity.register(mcp, session_manager)

    if caps_manager.is_enabled("network"):
        network.register(mcp, session_manager)
    if caps_manager.is_enabled("storage"):
        storage.register(mcp, session_manager)
    if caps_manager.is_enabled("emulation"):
        emulation.register(mcp, session_manager)
    if caps_manager.is_enabled("a11y"):
        a11y.register(mcp, session_manager)
    if caps_manager.is_enabled("interactions"):
        interactions.register(mcp, session_manager)
    if caps_manager.is_enabled("devtools"):
        devtools.register(mcp, session_manager)
    if caps_manager.is_enabled("vision"):
        vision.register(mcp, session_manager)
    if caps_manager.is_enabled("video"):
        video.register(mcp, session_manager)
    if caps_manager.is_enabled("testing"):
        testing.register(mcp, session_manager)
    if caps_manager.is_enabled("workflows"):
        workflows.register(mcp, session_manager)
    if caps_manager.is_enabled("data"):
        data.register(mcp, session_manager)
    if caps_manager.is_enabled("experimental"):
        experimental.register(mcp, session_manager)

    # M1: wavexis_act — natural language interaction
    _register_act_tool(mcp, session_manager)

    # M3: MCP resources and prompts
    from wavexis_mcp.prompts import register as register_prompts
    from wavexis_mcp.resources import register as register_resources

    register_resources(mcp, session_manager)
    register_prompts(mcp)

    _print_startup_info(caps_manager)

    return mcp


def _register_act_tool(mcp: FastMCP, session_manager: SessionManager) -> None:
    """Register the wavexis_act tool for natural language interaction.

    Args:
        mcp: The FastMCP server instance.
        session_manager: The shared session manager.
    """
    from wavexis_mcp.act import execute_act, match_instruction
    from wavexis_mcp.tools.a11y import _build_a11y_tree, _format_a11y_tree

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=True,
        )
    )
    async def wavexis_act(input: ActInput) -> str:
        """Execute a natural language instruction on the current page (M1).

        Takes an a11y snapshot, matches the instruction to an element,
        and performs the detected action (click, type, fill, hover).

        Args:
            input: Act parameters (instruction, session_id, max_retries).

        Returns:
            JSON string with ``action``, ``element``, ``score``, ``status``.
        """
        try:
            if not input.session_id:
                return format_error(
                    "wavexis_act",
                    ValueError("session_id is required for wavexis_act"),
                )
            session = session_manager.get(input.session_id)
            raw = await session_manager.call_backend(session.backend.a11y_tree())
            nodes = _build_a11y_tree(raw)
            tree = _format_a11y_tree(nodes)

            match = match_instruction(input.instruction, tree)
            if match is None:
                return format_json_response(
                    {
                        "status": "no_match",
                        "instruction": input.instruction,
                        "message": "No matching element found in accessibility tree.",
                    }
                )

            result = await execute_act(
                session.backend,
                input.instruction,
                tree,
                max_retries=input.max_retries,
                value=input.value,
            )
            return format_json_response(result)
        except Exception as e:
            return format_error("wavexis_act", e)


def _print_help(caps: str = "core") -> None:
    """Print help text showing available tiers and tool counts.

    Args:
        caps: The caps string to show configuration for.
    """
    caps_mgr = CapsManager(caps)
    tiers = sorted(caps_mgr.enabled_tiers())

    print("WaveXisMCP — browser automation MCP server")
    print()
    print("Usage: wavexis-mcp [OPTIONS]")
    print()
    print("Options:")
    print("  --caps <tiers>      Comma-separated capability tiers (default: core)")
    print("  --transport <mode>  stdio (default) or http")
    print("  --host <addr>       HTTP bind host (default: 127.0.0.1)")
    print("  --port <port>       HTTP listen port (default: 8765)")
    print("  --allow-remote      Bind to 0.0.0.0 (enables remote access)")
    print("  --rate-limit <n>    Max calls/sec per session (default: 60)")
    print("  --rate-burst <n>    Max burst size (default: 10)")
    print("  --help              Show this help message")
    print()
    print("Available tiers:")
    for tier in sorted(ALL_TIERS):
        marker = " [enabled]" if tier in tiers else ""
        print(f"  {tier}{marker}")
    print()
    print("Examples:")
    print("  wavexis-mcp                                    # stdio, core only")
    print("  wavexis-mcp --caps all                         # stdio, all tiers")
    print("  wavexis-mcp --transport http --port 8765       # HTTP on localhost")
    print("  wavexis-mcp --transport http --allow-remote    # HTTP on 0.0.0.0")
    print()
    print("MCP client configuration (stdio):")
    print('  {"mcpServers": {"wavexis": {"command": "wavexis-mcp", "args": ["--caps", "all"]}}}')
    print()
    print("Documentation: https://github.com/MathiasPaulenko/wavexis-mcp")
    print("License: MIT")


def _apply_rate_limiting(mcp: FastMCP, rate_limiter: RateLimiter | None) -> None:
    """Wrap every registered tool with per-session rate limiting.

    The wrapper is applied in ``main()`` so that programmatic callers of
    ``create_server()`` (e.g. the test suite) are not rate limited by
    default.  When a tool input has a ``session_id`` the rate limiter is
    consulted before the original handler runs.
    """
    if rate_limiter is None or not isinstance(mcp, FastMCP):
        return
    for registered_tool in mcp._tool_manager._tools.values():
        original_fn = registered_tool.fn
        typed_fn: Callable[[BaseModel], Awaitable[str]] = cast(
            Callable[[BaseModel], Awaitable[str]], original_fn
        )

        async def _rate_limited_fn(
            input: BaseModel,
            *,
            _orig: Callable[[BaseModel], Awaitable[str]] = typed_fn,
            _tool: Tool = registered_tool,
        ) -> str:
            session_id = getattr(input, "session_id", None)
            if session_id:
                allowed, retry_after_ms = await rate_limiter.check(session_id)
                if not allowed:
                    return format_error(
                        _tool.name,
                        RuntimeError(f"Rate limit exceeded. Retry after {retry_after_ms}ms."),
                    )
            return await _orig(input)

        registered_tool.fn = _rate_limited_fn


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments.

    Args:
        argv: Argument list to parse.  Defaults to ``sys.argv[1:]``.

    Returns:
        Parsed arguments namespace.
    """
    parser = argparse.ArgumentParser(
        prog="wavexis-mcp",
        description="WaveXisMCP — browser automation MCP server",
    )
    parser.add_argument(
        "--caps",
        default="core",
        help="Comma-separated capability tiers (default: core)",
    )
    parser.add_argument(
        "--transport",
        choices=["stdio", "http"],
        default="stdio",
        help="Transport mode: stdio (default) or http",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="HTTP bind host (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8765,
        help="HTTP listen port (default: 8765)",
    )
    parser.add_argument(
        "--allow-remote",
        action="store_true",
        default=False,
        help="Bind HTTP to 0.0.0.0 (allows remote connections — use with caution)",
    )
    parser.add_argument(
        "--rate-limit",
        type=int,
        default=60,
        help="Max tool calls per second per session (default: 60)",
    )
    parser.add_argument(
        "--rate-burst",
        type=int,
        default=10,
        help="Max burst size for rate limiting (default: 10)",
    )
    return parser.parse_args(argv)


def main() -> None:
    """Entry point for the ``wavexis-mcp`` CLI.

    Parses CLI arguments, creates the server with the specified caps
    and rate limiting, and starts the appropriate transport (stdio or HTTP).
    """
    args = _parse_args()

    if _is_help_request():
        _print_help(args.caps)
        return

    mcp = create_server(
        caps=args.caps,
        rate_limit=args.rate_limit,
        rate_burst=args.rate_burst,
    )

    rate_limiter = getattr(mcp, "_wavexis_rate_limiter", None)

    _apply_rate_limiting(mcp, rate_limiter)

    if args.transport == "http":
        # --allow-remote intentionally binds to all interfaces.
        host = "0.0.0.0" if args.allow_remote else args.host  # nosec B104
        if args.allow_remote:
            print(
                "WARNING: --allow-remote enabled. HTTP server will bind to 0.0.0.0. "
                "Use behind a reverse proxy with authentication.",
                file=sys.stderr,
            )
        mcp.settings.host = host
        mcp.settings.port = args.port
        mcp.run(transport="sse")
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
