"""MCP-layer convenience composite tools.

This module provides helper functions that combine multiple wavexis
backend calls into a single higher-level operation.  These helpers are
used by the tool modules to implement composite tools such as
``wavexis_fill_form``.
"""

from __future__ import annotations

from wavexis.backend.base import AbstractBackend

from wavexis_mcp.models import FormField


async def fill_form_composite(
    backend: AbstractBackend, fields: list[FormField]
) -> int:
    """Fill multiple form fields sequentially using ``backend.fill()``.

    Args:
        backend: A wavexis backend instance.
        fields: List of form field descriptors (selector + value).

    Returns:
        The number of fields successfully filled.
    """
    count = 0
    for field in fields:
        await backend.fill(field.selector, field.value)
        count += 1
    return count
