"""WaveXisMCP server — FastMCP entry point.

This module creates and configures the FastMCP server instance,
registers tool modules based on enabled capability tiers, and
provides the ``main`` CLI entry point with support for both
stdio and HTTP transports.
"""

from __future__ import annotations

import argparse
import atexit
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from wavexis_mcp.caps import ALL_TIERS, CapsManager
from wavexis_mcp.formatter import format_error, format_json_response
from wavexis_mcp.models import ActInput
from wavexis_mcp.rate_limiter import RateLimiter
from wavexis_mcp.session import SessionManager

_session_manager = SessionManager()
_caps_manager = CapsManager("core")
_rate_limiter = RateLimiter()


@asynccontextmanager
async def lifespan(_app: FastMCP) -> AsyncIterator[None]:
    """Manage server lifecycle — cleanup sessions on shutdown.

    Args:
        _app: The FastMCP application instance (unused).

    Yields:
        ``None`` — control returns to the server after cleanup.
    """
    yield
    await _session_manager.cleanup_all()


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
) -> FastMCP:
    """Create and configure the FastMCP server with the given capability tiers.

    Core tools are always registered.  Additional tiers are registered
    only when enabled via the *caps* string.  M1-M4 features (act,
    resources, prompts, rate limiting) are also registered here.

    Args:
        caps: Comma-separated tier names or ``"all"``.
        rate_limit: Maximum tool calls per second per session.
        rate_burst: Maximum burst size for rate limiting.

    Returns:
        A configured ``FastMCP`` instance with all enabled tools registered.
    """
    global _caps_manager, _rate_limiter
    _caps_manager = CapsManager(caps)
    _rate_limiter = RateLimiter(rate=rate_limit, burst=rate_burst)

    mcp = FastMCP(
        "wavexis-mcp",
        lifespan=lifespan,
        instructions=(
            "WaveXisMCP — browser automation via wavexis. "
            f"Enabled tiers: {', '.join(sorted(_caps_manager.enabled_tiers()))}. "
            "Use wavexis_session_open for multi-step workflows, "
            "or pass 'url' for stateless one-shot calls. "
            "Use wavexis_act for natural language interaction."
        ),
    )

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

    session.register(mcp, _session_manager)
    navigation.register(mcp, _session_manager)
    capture.register(mcp, _session_manager)
    javascript.register(mcp, _session_manager)
    dom.register(mcp, _session_manager)
    input.register(mcp, _session_manager)
    cookies.register(mcp, _session_manager)
    tabs.register(mcp, _session_manager)
    utility.register(mcp, _session_manager)
    playwright_parity.register(mcp, _session_manager)

    if _caps_manager.is_enabled("network"):
        network.register(mcp, _session_manager)
    if _caps_manager.is_enabled("storage"):
        storage.register(mcp, _session_manager)
    if _caps_manager.is_enabled("emulation"):
        emulation.register(mcp, _session_manager)
    if _caps_manager.is_enabled("a11y"):
        a11y.register(mcp, _session_manager)
    if _caps_manager.is_enabled("interactions"):
        interactions.register(mcp, _session_manager)
    if _caps_manager.is_enabled("devtools"):
        devtools.register(mcp, _session_manager)
    if _caps_manager.is_enabled("vision"):
        vision.register(mcp, _session_manager)
    if _caps_manager.is_enabled("video"):
        video.register(mcp, _session_manager)
    if _caps_manager.is_enabled("testing"):
        testing.register(mcp, _session_manager)
    if _caps_manager.is_enabled("workflows"):
        workflows.register(mcp, _session_manager)
    if _caps_manager.is_enabled("data"):
        data.register(mcp, _session_manager)
    if _caps_manager.is_enabled("experimental"):
        experimental.register(mcp, _session_manager)

    # M1: wavexis_act — natural language interaction
    _register_act_tool(mcp, _session_manager)

    # M3: MCP resources and prompts
    from wavexis_mcp.prompts import register as register_prompts
    from wavexis_mcp.resources import register as register_resources

    register_resources(mcp, _session_manager)
    register_prompts(mcp)

    _print_startup_info(_caps_manager)

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
            )
            return format_json_response(result)
        except Exception as e:
            return format_error("wavexis_act", e)


def _atexit_cleanup() -> None:
    """Kill any orphaned browser processes on exit."""
    import asyncio

    try:
        loop = asyncio.new_event_loop()
        loop.run_until_complete(_session_manager.cleanup_all())
        loop.close()
    except Exception:
        pass


atexit.register(_atexit_cleanup)


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


mcp = create_server(parse_caps())


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

    global mcp
    mcp = create_server(
        caps=args.caps,
        rate_limit=args.rate_limit,
        rate_burst=args.rate_burst,
    )

    if args.transport == "http":
        host = "0.0.0.0" if args.allow_remote else args.host
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
