"""Accessibility (a11y) tools for WaveXisMCP.

Provides tools for capturing the accessibility tree, querying
individual nodes, and retrieving ancestor chains.  The snapshot
output is formatted as LLM-friendly text with element references.
"""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from wavexis_mcp.formatter import format_error, format_json_response
from wavexis_mcp.models import (
    A11yAncestorsInput,
    A11yNodeInput,
    A11ySnapshotInput,
    AxeAuditInput,
)
from wavexis_mcp.session import SessionManager

_REF_COUNTER = 0


def _extract_role(node: dict[str, Any]) -> str:
    """Extract a human-readable role string from a CDP a11y node.

    CDP nodes store role as ``{"type": "role", "value": "WebArea"}``-style
    dicts.  Some backends may already return a plain string.

    Args:
        node: Raw CDP accessibility node.

    Returns:
        The role string, or ``"unknown"`` if not found.
    """
    role = node.get("role", "unknown")
    if isinstance(role, dict):
        return str(role.get("value", "unknown"))
    return str(role)


def _extract_name(node: dict[str, Any]) -> str:
    """Extract a human-readable name string from a CDP a11y node.

    CDP nodes store name as ``{"value": "Welcome"}``-style dicts.

    Args:
        node: Raw CDP accessibility node.

    Returns:
        The name string, or empty string if not found.
    """
    name = node.get("name", "")
    if isinstance(name, dict):
        return str(name.get("value", ""))
    return str(name) if name else ""


def _build_a11y_tree(raw: dict[str, Any] | list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Convert a raw CDP accessibility tree into a nested tree structure.

    CDP's ``Accessibility.getFullAXTree`` returns a flat list of nodes
    with ``nodeId`` and ``parentId`` references.  This function rebuilds
    the parent-child hierarchy and normalises ``role``/``name`` fields
    so that ``_format_a11y_tree`` can consume them uniformly.

    Args:
        raw: The raw response from ``backend.a11y_tree()`` — either a
            dict with a ``"nodes"`` key (CDP flat list) or a pre-built
            list of tree nodes.

    Returns:
        A list of tree node dicts with ``role``, ``name``, and
        ``children`` keys.
    """
    nodes: list[dict[str, Any]]
    if isinstance(raw, dict):
        nodes = list(raw.get("nodes", []))
    elif isinstance(raw, list):
        return raw
    else:
        return []

    if not nodes:
        return []

    by_id: dict[str, dict[str, Any]] = {}
    root_ids: list[str] = []

    for node in nodes:
        node_id = str(node.get("nodeId", ""))
        if not node_id:
            continue
        by_id[node_id] = {
            "role": _extract_role(node),
            "name": _extract_name(node),
            "children": [],
            "_visited": False,
        }

    for node in nodes:
        node_id = str(node.get("nodeId", ""))
        if not node_id or node_id not in by_id:
            continue
        parent_id = node.get("parentId")
        child_ids = node.get("childIds", [])
        if child_ids:
            for cid in child_ids:
                cid_str = str(cid)
                if cid_str in by_id:
                    by_id[node_id]["children"].append(by_id[cid_str])
                    by_id[cid_str]["_visited"] = True
        elif parent_id and str(parent_id) in by_id:
            by_id[str(parent_id)]["children"].append(by_id[node_id])
            by_id[node_id]["_visited"] = True
        else:
            root_ids.append(node_id)

    if not root_ids:
        root_ids = [nid for nid, n in by_id.items() if not n.get("_visited")]

    if not root_ids and by_id:
        root_ids = [next(iter(by_id))]

    return [by_id[rid] for rid in root_ids if rid in by_id]


def _format_a11y_tree(nodes: list[dict[str, Any]], level: int = 0) -> list[dict[str, Any]]:
    """Convert raw a11y tree nodes into LLM-friendly structure with refs.

    Args:
        nodes: Raw accessibility tree nodes from the backend.
        level: Current nesting depth (0 for root).

    Returns:
        List of formatted node dicts with ``ref``, ``role``, ``name``,
        ``level``, and optional ``children``.
    """
    global _REF_COUNTER
    result: list[dict[str, Any]] = []
    for node in nodes:
        _REF_COUNTER += 1
        ref = f"el-{_REF_COUNTER}"
        entry: dict[str, Any] = {
            "ref": ref,
            "role": node.get("role", "unknown"),
            "name": node.get("name", ""),
            "level": level,
        }
        children = node.get("children", [])
        if children:
            entry["children"] = _format_a11y_tree(children, level + 1)
        result.append(entry)
    return result


def _tree_to_text(nodes: list[dict[str, Any]], indent: int = 0) -> str:
    """Render an a11y tree as indented text with element refs.

    Args:
        nodes: Formatted tree nodes (output of ``_format_a11y_tree``).
        indent: Current indentation level.

    Returns:
        A multi-line string representation of the tree.
    """
    lines: list[str] = []
    for node in nodes:
        prefix = "  " * indent
        ref = node.get("ref", "")
        role = node.get("role", "unknown")
        name = node.get("name", "")
        line = f"{prefix}[{ref}] {role}"
        if name:
            line += f": {name}"
        lines.append(line)
        children = node.get("children", [])
        if children:
            lines.append(_tree_to_text(children, indent + 1))
    return "\n".join(lines)


def _count_nodes(nodes: list[dict[str, Any]]) -> int:
    """Recursively count total nodes in a tree.

    Args:
        nodes: Tree nodes to count.

    Returns:
        Total number of nodes including all children.
    """
    count = 0
    for node in nodes:
        count += 1
        count += _count_nodes(node.get("children", []))
    return count


def register(mcp: FastMCP, session_manager: SessionManager) -> None:
    """Register all a11y tools on the FastMCP server.

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
    async def wavexis_a11y_snapshot(input: A11ySnapshotInput) -> str:
        """Get the full accessibility tree as LLM-friendly text with element refs.

        Args:
            input: Snapshot parameters including optional URL and session.

        Returns:
            JSON string with ``snapshot``, ``text``, and ``element_count``.
        """
        global _REF_COUNTER
        try:
            backend, sid = await session_manager.acquire_backend(
                input.session_id,
                backend=input.backend,
                headless=input.headless,
            )
            try:
                if input.url and not input.session_id:
                    await session_manager.call_backend(backend.navigate(input.url))
                raw = await session_manager.call_backend(backend.a11y_tree())
                _REF_COUNTER = 0
                nodes = _build_a11y_tree(raw)
                tree = _format_a11y_tree(nodes)
                text = _tree_to_text(tree)
                count = _count_nodes(tree)
                return format_json_response(
                    {
                        "snapshot": tree,
                        "text": text,
                        "element_count": count,
                    }
                )
            finally:
                await session_manager.release_backend(backend, sid)
        except Exception as e:
            return format_error("wavexis_a11y_snapshot", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def wavexis_a11y_node(input: A11yNodeInput) -> str:
        """Get a specific accessibility node by ID.

        Args:
            input: Node lookup parameters.

        Returns:
            JSON string with the node data.
        """
        try:
            session = session_manager.get(input.session_id)
            node = await session.backend.a11y_node(input.node_id)
            return format_json_response({"node": node})
        except Exception as e:
            return format_error("wavexis_a11y_node", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def wavexis_a11y_ancestors(input: A11yAncestorsInput) -> str:
        """Get the ancestor chain for a node.

        Args:
            input: Ancestor lookup parameters.

        Returns:
            JSON string with ``ancestors`` list and ``count``.
        """
        try:
            session = session_manager.get(input.session_id)
            ancestors = await session.backend.a11y_ancestors(input.node_id)
            return format_json_response({"ancestors": ancestors, "count": len(ancestors)})
        except Exception as e:
            return format_error("wavexis_a11y_ancestors", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=True,
        )
    )
    async def wavexis_axe_audit(input: AxeAuditInput) -> str:
        """Run an axe-core accessibility audit on the current page (W9).

        Injects axe-core and returns violations, passes, incomplete, and
        inapplicable results.

        Args:
            input: Audit parameters (optional URL, session_id).

        Returns:
            JSON string with ``violations``, ``passes``, ``incomplete``, ``inapplicable``.
        """
        try:
            backend, sid = await session_manager.acquire_backend(
                input.session_id,
                backend=input.backend,
                headless=input.headless,
            )
            try:
                if input.url and not input.session_id:
                    await session_manager.call_backend(backend.navigate(input.url))
                result = await session_manager.call_backend(backend.axe_audit())
                return format_json_response(result)
            finally:
                await session_manager.release_backend(backend, sid)
        except Exception as e:
            return format_error("wavexis_axe_audit", e)
