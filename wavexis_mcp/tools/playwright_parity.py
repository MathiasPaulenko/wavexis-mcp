"""Playwright MCP parity tools for WaveXisMCP.

Adds low-level keyboard/mouse, cookie filtering, console clearing, page
closing, snapshot search, and configuration introspection that Playwright
MCP exposes but wavexis-mcp previously lacked.
"""

from __future__ import annotations

import asyncio
import re
from typing import Any, Literal

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import BaseModel, Field

from wavexis_mcp.formatter import format_error, format_json_response
from wavexis_mcp.session import SessionManager


def _modifiers(alt: bool, ctrl: bool, meta: bool, shift: bool) -> int:
    """Convert modifier booleans to CDP modifiers bitmask."""
    mask = 0
    if alt:
        mask |= 1
    if ctrl:
        mask |= 2
    if meta:
        mask |= 4
    if shift:
        mask |= 8
    return mask


# ── Input models ──────────────────────────────────────────────────


class KeyDownInput(BaseModel):
    """Input for dispatching a keyDown event."""

    key: str = Field(..., description="Key to press (e.g. 'Enter', 'a', 'ArrowLeft')")
    code: str = Field(default="", description="Optional physical key code")
    alt: bool = Field(default=False)
    ctrl: bool = Field(default=False)
    meta: bool = Field(default=False)
    shift: bool = Field(default=False)
    session_id: str = Field(...)


class KeyUpInput(BaseModel):
    """Input for dispatching a keyUp event."""

    key: str = Field(..., description="Key to release (e.g. 'Enter', 'a')")
    code: str = Field(default="", description="Optional physical key code")
    alt: bool = Field(default=False)
    ctrl: bool = Field(default=False)
    meta: bool = Field(default=False)
    shift: bool = Field(default=False)
    session_id: str = Field(...)


class PressKeysInput(BaseModel):
    """Input for typing a sequence of keys at the page level."""

    text: str = Field(..., description="Text/keys to type character by character")
    delay: int = Field(default=0, ge=0, description="Delay between keystrokes in milliseconds")
    session_id: str = Field(...)


class MouseDragXYInput(BaseModel):
    """Input for dragging the mouse from one screen coordinate to another."""

    start_x: float = Field(...)
    start_y: float = Field(...)
    end_x: float = Field(...)
    end_y: float = Field(...)
    button: Literal["left", "right", "middle"] = Field(default="left")
    steps: int = Field(default=5, ge=1, le=50)
    session_id: str = Field(...)


class ConsoleClearInput(BaseModel):
    """Input for clearing console messages."""

    session_id: str = Field(...)


class CookieGetInput(BaseModel):
    """Input for getting a specific cookie by name (and optional domain/path)."""

    name: str = Field(...)
    domain: str | None = Field(default=None)
    path: str | None = Field(default=None)
    session_id: str = Field(...)


class CookieListInput(BaseModel):
    """Input for listing cookies with optional filters."""

    name: str | None = Field(default=None)
    domain: str | None = Field(default=None)
    path: str | None = Field(default=None)
    limit: int = Field(default=100, ge=1, le=1000)
    session_id: str = Field(...)


class ClosePageInput(BaseModel):
    """Input for closing the current page/tab."""

    tab_id: str | None = Field(
        default=None, description="Optional tab/target id; current page is closed if omitted"
    )
    session_id: str = Field(...)


class FindInput(BaseModel):
    """Input for finding text in the ARIA/accessibility snapshot."""

    text: str = Field(..., description="Text or regex to search in the a11y snapshot")
    limit: int = Field(default=20, ge=1, le=100)
    session_id: str = Field(...)


class GetConfigInput(BaseModel):
    """Input for querying server configuration."""

    pass


# ── Helpers ───────────────────────────────────────────────────────


def _parse_targets(targets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return only attached page targets from a Target.getTargets response."""
    return [t for t in targets if t.get("type") == "page" and t.get("attached") is True]


# ── Registration ──────────────────────────────────────────────────


def register(mcp: FastMCP, session_manager: SessionManager) -> None:
    """Register Playwright parity tools on the FastMCP server."""

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        )
    )
    async def wavexis_key_down(input: KeyDownInput) -> str:
        """Dispatch a keyDown event to the page."""
        try:
            session = session_manager.get(input.session_id)
            await session.backend.input_dispatch_key_event(
                type="keyDown",
                key=input.key,
                code=input.code,
                modifiers=_modifiers(input.alt, input.ctrl, input.meta, input.shift),
            )
            return format_json_response({"status": "ok"})
        except Exception as e:
            return format_error("wavexis_key_down", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        )
    )
    async def wavexis_key_up(input: KeyUpInput) -> str:
        """Dispatch a keyUp event to the page."""
        try:
            session = session_manager.get(input.session_id)
            await session.backend.input_dispatch_key_event(
                type="keyUp",
                key=input.key,
                code=input.code,
                modifiers=_modifiers(input.alt, input.ctrl, input.meta, input.shift),
            )
            return format_json_response({"status": "ok"})
        except Exception as e:
            return format_error("wavexis_key_up", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        )
    )
    async def wavexis_press_keys(input: PressKeysInput) -> str:
        """Type a sequence of keys at the page level (no element target required)."""
        try:
            session = session_manager.get(input.session_id)
            for ch in input.text:
                await session.backend.input_dispatch_key_event(
                    type="keyDown",
                    key=ch,
                    text=ch,
                )
                await session.backend.input_dispatch_key_event(
                    type="keyUp",
                    key=ch,
                )
                if input.delay:
                    await asyncio.sleep(input.delay / 1000)
            return format_json_response({"status": "ok", "typed": input.text})
        except Exception as e:
            return format_error("wavexis_press_keys", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=True,
            idempotentHint=False,
            openWorldHint=True,
        )
    )
    async def wavexis_mouse_drag_xy(input: MouseDragXYInput) -> str:
        """Drag the mouse from one coordinate to another."""
        try:
            session = session_manager.get(input.session_id)
            await session.backend.input_dispatch_mouse_event(
                type="mouseMoved",
                x=input.start_x,
                y=input.start_y,
            )
            await session.backend.input_dispatch_mouse_event(
                type="mousePressed",
                x=input.start_x,
                y=input.start_y,
                button=input.button,
                click_count=1,
            )
            for step in range(1, input.steps + 1):
                t = step / input.steps
                x = input.start_x + (input.end_x - input.start_x) * t
                y = input.start_y + (input.end_y - input.start_y) * t
                await session.backend.input_dispatch_mouse_event(
                    type="mouseMoved",
                    x=x,
                    y=y,
                    button=input.button,
                )
            await session.backend.input_dispatch_mouse_event(
                type="mouseReleased",
                x=input.end_x,
                y=input.end_y,
                button=input.button,
                click_count=1,
            )
            return format_json_response({"status": "ok"})
        except Exception as e:
            return format_error("wavexis_mouse_drag_xy", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=True,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def wavexis_console_clear(input: ConsoleClearInput) -> str:
        """Clear all console messages."""
        try:
            session = session_manager.get(input.session_id)
            await session.backend.console_clear_messages()
            return format_json_response({"status": "ok"})
        except Exception as e:
            return format_error("wavexis_console_clear", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=True,
        )
    )
    async def wavexis_cookie_get(input: CookieGetInput) -> str:
        """Get a specific cookie by name."""
        try:
            session = session_manager.get(input.session_id)
            cookies = await session.backend.get_cookies()
            matches = [
                c
                for c in cookies
                if c.get("name") == input.name
                and (input.domain is None or c.get("domain") == input.domain)
                and (input.path is None or c.get("path") == input.path)
            ]
            return format_json_response({"cookie": matches[0] if matches else None})
        except Exception as e:
            return format_error("wavexis_cookie_get", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=True,
        )
    )
    async def wavexis_cookie_list(input: CookieListInput) -> str:
        """List cookies with optional filters."""
        try:
            session = session_manager.get(input.session_id)
            cookies = await session.backend.get_cookies()
            if input.name:
                cookies = [c for c in cookies if c.get("name") == input.name]
            if input.domain:
                cookies = [c for c in cookies if input.domain in (c.get("domain") or "")]
            if input.path:
                cookies = [c for c in cookies if input.path in (c.get("path") or "")]
            cookies = cookies[: input.limit]
            return format_json_response({"cookies": cookies, "count": len(cookies)})
        except Exception as e:
            return format_error("wavexis_cookie_list", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=True,
            idempotentHint=False,
            openWorldHint=True,
        )
    )
    async def wavexis_close_page(input: ClosePageInput) -> str:
        """Close the current page/tab."""
        try:
            session = session_manager.get(input.session_id)
            if input.tab_id:
                await session.backend.target_close_target(input.tab_id)
                return format_json_response({"status": "ok", "closed": input.tab_id})
            targets = await session.backend.target_get_targets()
            pages = _parse_targets(targets)
            if not pages:
                return format_error(
                    "wavexis_close_page", Exception("No attached page target found")
                )
            await session.backend.target_close_target(pages[0]["targetId"])
            return format_json_response({"status": "ok", "closed": pages[0]["targetId"]})
        except Exception as e:
            return format_error("wavexis_close_page", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=True,
        )
    )
    async def wavexis_find(input: FindInput) -> str:
        """Find nodes in the accessibility snapshot matching the given text/regex."""
        try:
            from wavexis_mcp.tools.a11y import _build_a11y_tree, _extract_name, _extract_role

            session = session_manager.get(input.session_id)
            raw = await session.backend.a11y_tree()
            tree = _build_a11y_tree(raw)

            pattern = re.compile(input.text, re.IGNORECASE)
            results: list[dict[str, Any]] = []

            def search(nodes: list[dict[str, Any]]) -> None:
                for node in nodes:
                    if len(results) >= input.limit:
                        return
                    name = _extract_name(node)
                    role = _extract_role(node)
                    if pattern.search(name):
                        results.append({"role": role, "name": name, "node": node})
                    search(node.get("children", []))

            search(tree)
            return format_json_response({"matches": results, "count": len(results)})
        except Exception as e:
            return format_error("wavexis_find", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def wavexis_get_config(input: GetConfigInput) -> str:
        """Return wavexis-mcp server configuration and available backends."""
        try:
            from wavexis.backend.manager import BackendManager

            mgr = BackendManager()
            available = mgr.list_available()
            versions = mgr.install_check()
            return format_json_response(
                {
                    "name": "wavexis-mcp",
                    "available_backends": available,
                    "backend_versions": versions,
                }
            )
        except Exception as e:
            return format_error("wavexis_get_config", e)
