"""Testing assertion tools for WaveXisMCP.

Provides tools for asserting element visibility, text visibility,
URL matching, and generating robust CSS locators.  All tools
require an active session and return structured pass/fail results.
"""

from __future__ import annotations

import asyncio
import time

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from wavexis_mcp.formatter import format_error, format_json_response
from wavexis_mcp.models import (
    AssertListInput,
    AssertTextVisibleInput,
    AssertURLInput,
    AssertValueInput,
    AssertVisibleInput,
    GenerateLocatorInput,
)
from wavexis_mcp.session import SessionManager


def register(mcp: FastMCP, session_manager: SessionManager) -> None:
    """Register all testing tools on the FastMCP server.

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
    async def wavexis_assert_visible(input: AssertVisibleInput) -> str:
        """Assert that an element is visible on the page.

        Args:
            input: Assertion parameters (selector, timeout).

        Returns:
            JSON string with ``passed``, ``selector``, and ``message``.
        """
        try:
            session = session_manager.get(input.session_id)
            escaped = input.selector.replace("'", "\\'")
            js = (
                f"(function(){{var el=document.querySelector('{escaped}');"
                f"if(!el)return false;"
                f"var rect=el.getBoundingClientRect();"
                f"return rect.width>0&&rect.height>0;}})()"
            )
            deadline = time.monotonic() + input.timeout / 1000
            visible = False
            while time.monotonic() < deadline:
                result = await session.backend.eval(js)
                if result is True or result == "true":
                    visible = True
                    break
                await asyncio.sleep(0.1)

            if visible:
                return format_json_response(
                    {
                        "passed": True,
                        "selector": input.selector,
                        "message": "Element is visible",
                    }
                )
            return format_json_response(
                {
                    "passed": False,
                    "selector": input.selector,
                    "message": "Element not visible within timeout",
                }
            )
        except Exception as e:
            return format_json_response(
                {
                    "passed": False,
                    "selector": input.selector,
                    "message": str(e),
                }
            )

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=True,
        )
    )
    async def wavexis_assert_text_visible(input: AssertTextVisibleInput) -> str:
        """Assert that specific text is visible on the page.

        Args:
            input: Assertion parameters (text, timeout).

        Returns:
            JSON string with ``passed``, ``text``, and ``message``.
        """
        try:
            session = session_manager.get(input.session_id)
            escaped = input.text.replace("'", "\\'").replace("\\", "\\\\")
            js = f"(function(){{return document.body.innerText.indexOf('{escaped}')!==-1;}})()"
            deadline = time.monotonic() + input.timeout / 1000
            visible = False
            while time.monotonic() < deadline:
                result = await session.backend.eval(js)
                if result is True or result == "true":
                    visible = True
                    break
                await asyncio.sleep(0.1)

            if visible:
                return format_json_response(
                    {
                        "passed": True,
                        "text": input.text,
                        "message": "Text is visible",
                    }
                )
            return format_json_response(
                {
                    "passed": False,
                    "text": input.text,
                    "message": "Text not found within timeout",
                }
            )
        except Exception as e:
            return format_json_response(
                {
                    "passed": False,
                    "text": input.text,
                    "message": str(e),
                }
            )

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=True,
        )
    )
    async def wavexis_assert_value(input: AssertValueInput) -> str:
        """Assert that a form element has the expected value.

        Args:
            input: Assertion parameters (selector, value, timeout).

        Returns:
            JSON string with ``passed``, ``value``, and ``message``.
        """
        try:
            session = session_manager.get(input.session_id)
            escaped = input.selector.replace("'", "\\'")
            escaped_val = input.value.replace("'", "\\'").replace("\\", "\\\\")
            js = (
                f"(function(){{"
                f"var el=document.querySelector('{escaped}');"
                f"if(!el) return false;"
                f"return String(el.value)==='{escaped_val}';"
                f"}})()"
            )
            deadline = time.monotonic() + input.timeout / 1000
            passed = False
            while time.monotonic() < deadline:
                result = await session.backend.eval(js)
                if result is True or result == "true":
                    passed = True
                    break
                await asyncio.sleep(0.1)

            if passed:
                return format_json_response(
                    {
                        "passed": True,
                        "selector": input.selector,
                        "value": input.value,
                        "message": "Value matches",
                    }
                )
            return format_json_response(
                {
                    "passed": False,
                    "selector": input.selector,
                    "value": input.value,
                    "message": "Value does not match within timeout",
                }
            )
        except Exception as e:
            return format_json_response(
                {
                    "passed": False,
                    "selector": input.selector,
                    "value": input.value,
                    "message": str(e),
                }
            )

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=True,
        )
    )
    async def wavexis_assert_list(input: AssertListInput) -> str:
        """Assert that all expected text items are visible inside a list element.

        Args:
            input: Assertion parameters (selector, items, timeout).

        Returns:
            JSON string with ``passed``, ``items``, ``missing``, and ``message``.
        """
        try:
            session = session_manager.get(input.session_id)
            escaped = input.selector.replace("'", "\\'")
            items_js = ",".join(repr(item) for item in input.items)
            js = (
                f"(function(){{"
                f"var list=document.querySelector('{escaped}');"
                f"if(!list) return null;"
                f"var text=list.innerText;"
                f"var items=[{items_js}];"
                f"return items.map(function(i){{return text.indexOf(i)!==-1;}});"
                f"}})()"
            )
            deadline = time.monotonic() + input.timeout / 1000
            passed = False
            while time.monotonic() < deadline:
                result = await session.backend.eval(js)
                if result and all(result):
                    passed = True
                    break
                await asyncio.sleep(0.1)

            if passed:
                return format_json_response(
                    {
                        "passed": True,
                        "selector": input.selector,
                        "items": input.items,
                        "missing": [],
                        "message": "All list items are visible",
                    }
                )
            current = result or [False] * len(input.items)
            missing = [item for item, ok in zip(input.items, current, strict=False) if not ok]
            return format_json_response(
                {
                    "passed": False,
                    "selector": input.selector,
                    "items": input.items,
                    "missing": missing,
                    "message": "Some list items are missing",
                }
            )
        except Exception as e:
            return format_json_response(
                {
                    "passed": False,
                    "selector": input.selector,
                    "items": input.items,
                    "missing": input.items,
                    "message": str(e),
                }
            )

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=True,
        )
    )
    async def wavexis_assert_url(input: AssertURLInput) -> str:
        """Assert the current URL matches a pattern.

        Args:
            input: Assertion parameters (url_pattern).

        Returns:
            JSON string with ``passed``, ``url``, and ``pattern``.
        """
        try:
            session = session_manager.get(input.session_id)
            current_url = await session.backend.eval("window.location.href")
            current_url = str(current_url) if current_url else ""
            passed = input.url_pattern.lower() in current_url.lower()

            return format_json_response(
                {
                    "passed": passed,
                    "url": current_url,
                    "pattern": input.url_pattern,
                    "message": "URL matches" if passed else "URL does not match pattern",
                }
            )
        except Exception as e:
            return format_json_response(
                {
                    "passed": False,
                    "pattern": input.url_pattern,
                    "message": str(e),
                }
            )

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=True,
        )
    )
    async def wavexis_generate_locator(input: GenerateLocatorInput) -> str:
        """Generate a robust CSS selector for an element.

        Uses the backend's ``suggest_locator`` method to produce
        optimal selectors in priority order: id > data-testid >
        aria-label > text > tag.classes > nth-of-type chain.

        Args:
            input: Locator parameters (selector, description).

        Returns:
            JSON string with ``locator`` and ``alternative``.
        """
        try:
            session = session_manager.get(input.session_id)
            locators = await session.backend.suggest_locator(input.selector, all=True)
            locators = list(locators) if locators else []

            if not locators:
                return format_json_response(
                    {
                        "locator": input.selector,
                        "alternative": None,
                    }
                )

            return format_json_response(
                {
                    "locator": locators[0],
                    "alternative": locators[1] if len(locators) > 1 else None,
                }
            )
        except Exception as e:
            return format_error("wavexis_generate_locator", e)
