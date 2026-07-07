"""Natural language interaction logic for wavexis_act (M1).

This module provides heuristic-based matching of natural language
instructions to accessibility tree elements.  No external LLM calls
are made — matching uses keyword extraction, role/name scoring, and
action verb detection.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

_ACTION_VERBS: dict[str, str] = {
    "click": "click",
    "tap": "click",
    "press": "click",
    "select": "click",
    "type": "type",
    "enter": "type",
    "input": "type",
    "fill": "fill",
    "write": "fill",
    "hover": "hover",
    "focus": "focus",
}

_ROLE_KEYWORDS: dict[str, set[str]] = {
    "button": {"button", "btn"},
    "link": {"link", "anchor", "a"},
    "textbox": {"input", "field", "text", "textbox", "search"},
    "searchbox": {"search", "searchbox"},
    "combobox": {"select", "dropdown", "combobox"},
    "checkbox": {"checkbox", "check"},
    "radio": {"radio", "option"},
    "heading": {"heading", "title", "h1", "h2", "h3"},
    "image": {"image", "img", "picture", "logo"},
    "navigation": {"nav", "navigation", "menu"},
    "tab": {"tab"},
    "dialog": {"dialog", "modal", "popup"},
    "alert": {"alert", "warning", "notification"},
    "form": {"form"},
    "table": {"table"},
    "list": {"list"},
    "paragraph": {"paragraph", "text", "content"},
    "banner": {"header", "banner", "top"},
    "contentinfo": {"footer", "contentinfo", "bottom"},
}


@dataclass
class MatchResult:
    """Result of matching an instruction to an a11y element.

    Attributes:
        ref: Element reference (e.g. ``"el-3"``).
        role: ARIA role of the matched element.
        name: Accessible name of the matched element.
        action: Detected action (``"click"``, ``"type"``, ``"fill"``, ``"hover"``).
        score: Match confidence score (0-100).
        selector: CSS selector derived from the element, if available.
    """

    ref: str
    role: str
    name: str
    action: str
    score: float
    selector: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)


def _extract_keywords(instruction: str) -> list[str]:
    """Extract lowercase keywords from a natural language instruction.

    Removes stop words and action verbs, returning meaningful terms.

    Args:
        instruction: Raw user instruction string.

    Returns:
        List of lowercase keyword strings.
    """
    stop_words = {
        "the", "a", "an", "on", "in", "at", "to", "of", "for",
        "and", "or", "with", "that", "this", "is", "are",
    }
    words = re.findall(r"[a-zA-Z]+", instruction.lower())
    return [w for w in words if w not in stop_words and len(w) > 1]


def _detect_action(instruction: str) -> str:
    """Detect the action verb from an instruction.

    Args:
        instruction: Raw user instruction string.

    Returns:
        Action string (``"click"``, ``"type"``, ``"fill"``, ``"hover"``).
        Defaults to ``"click"`` if no verb is recognized.
    """
    lower = instruction.lower()
    for verb, action in _ACTION_VERBS.items():
        if re.search(rf"\b{verb}\b", lower):
            return action
    return "click"


def _detect_role_keywords(keywords: list[str]) -> set[str]:
    """Detect ARIA role keywords from extracted keywords.

    Args:
        keywords: List of lowercase keywords.

    Returns:
        Set of matched role-related keyword strings.
    """
    matched: set[str] = set()
    for kw in keywords:
        for role, synonyms in _ROLE_KEYWORDS.items():
            if kw in synonyms:
                matched.add(role)
    return matched


def _flatten_tree(
    nodes: list[dict[str, Any]], parent_path: list[str] | None = None
) -> list[dict[str, Any]]:
    """Flatten a nested a11y tree into a list of nodes with paths.

    Args:
        nodes: Tree nodes (output of ``_format_a11y_tree``).
        parent_path: Path of parent refs (for ancestry tracking).

    Returns:
        List of flat node dicts with ``ref``, ``role``, ``name``, ``path``.
    """
    flat: list[dict[str, Any]] = []
    for node in nodes:
        path = (parent_path or []) + [node.get("ref", "")]
        flat.append({
            "ref": node.get("ref", ""),
            "role": node.get("role", "unknown"),
            "name": node.get("name", ""),
            "path": path,
        })
        children = node.get("children", [])
        if children:
            flat.extend(_flatten_tree(children, path))
    return flat


def _score_element(
    element: dict[str, Any],
    keywords: list[str],
    role_keywords: set[str],
) -> float:
    """Score how well an element matches the extracted keywords.

    Scoring factors:
    - Role keyword match (e.g. "button" in instruction, element role is ``button``)
    - Name keyword match (e.g. "login" in instruction and element name)
    - Partial name match (substring)
    - Role bonus for interactive elements

    Args:
        element: Flat element dict with ``ref``, ``role``, ``name``.
        keywords: Extracted instruction keywords.
        role_keywords: Detected role keywords from instruction.

    Returns:
        Match score (0-100).
    """
    score = 0.0
    role = element.get("role", "unknown").lower()
    name = element.get("name", "").lower()

    if not name and role in ("unknown", "generic", "none"):
        return 0.0

    # Role match: strong signal
    if role in role_keywords:
        score += 40

    # Also check synonyms (e.g. "btn" in instruction matches role "button")
    for role_kw in role_keywords:
        synonyms = _ROLE_KEYWORDS.get(role_kw, set())
        if role in synonyms:
            score += 20
            break

    # Exact name keyword match
    name_words = set(re.findall(r"[a-zA-Z]+", name))
    for kw in keywords:
        if kw in name_words:
            score += 25

    # Partial name match (substring)
    for kw in keywords:
        if kw in name and kw not in name_words:
            score += 15

    # Interactive element bonus
    if role in ("button", "link", "textbox", "searchbox", "checkbox", "radio", "tab"):
        score += 10

    return min(score, 100.0)


def match_instruction(
    instruction: str,
    tree: list[dict[str, Any]],
) -> MatchResult | None:
    """Match a natural language instruction to the best a11y element.

    Args:
        instruction: Natural language instruction (e.g. ``"click the login button"``).
        tree: Formatted a11y tree (output of ``_format_a11y_tree``).

    Returns:
        ``MatchResult`` for the best match, or ``None`` if no match found.
    """
    keywords = _extract_keywords(instruction)
    if not keywords:
        return None

    action = _detect_action(instruction)
    role_keywords = _detect_role_keywords(keywords)
    flat = _flatten_tree(tree)

    best: MatchResult | None = None
    best_score = 0.0

    for element in flat:
        score = _score_element(element, keywords, role_keywords)
        if score > best_score:
            best_score = score
            best = MatchResult(
                ref=element["ref"],
                role=element["role"],
                name=element["name"],
                action=action,
                score=score,
            )

    return best


async def execute_act(
    backend: Any,
    instruction: str,
    tree: list[dict[str, Any]],
    max_retries: int = 3,
) -> dict[str, Any]:
    """Execute a natural language instruction against the browser.

    Takes an a11y tree, matches the instruction to an element, and
    performs the detected action (click, type, fill, hover).

    Args:
        backend: wavexis ``AbstractBackend`` instance.
        instruction: Natural language instruction.
        tree: Formatted a11y tree.
        max_retries: Maximum retry attempts if action fails.

    Returns:
        Dict with ``action``, ``element``, ``score``, and ``status``.
    """
    match = match_instruction(instruction, tree)
    if match is None:
        return {
            "status": "no_match",
            "instruction": instruction,
            "message": "No matching element found in accessibility tree.",
        }

    # Derive a selector from the element name or role
    selector: str | None = None
    if match.name:
        # Try to use aria-label or text-based selector
        selector = f'[aria-label="{match.name}"]'

    result: dict[str, Any] = {
        "action": match.action,
        "element": {
            "ref": match.ref,
            "role": match.role,
            "name": match.name,
        },
        "score": match.score,
        "selector": selector,
    }

    for attempt in range(max_retries):
        try:
            if match.action == "click":
                await backend.click(selector or f"#{match.ref}")
            elif match.action == "type":
                await backend.type_text(selector or f"#{match.ref}", "")
            elif match.action == "fill":
                await backend.fill(selector or f"#{match.ref}", "")
            elif match.action == "hover":
                await backend.hover(selector or f"#{match.ref}")

            result["status"] = "ok"
            result["attempts"] = attempt + 1
            return result
        except Exception as e:
            if attempt == max_retries - 1:
                result["status"] = "error"
                result["error"] = str(e)
                result["attempts"] = attempt + 1
            # Retry with next strategy could go here

    return result
