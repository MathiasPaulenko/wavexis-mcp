"""Natural language interaction logic for wavexis_act (M1).

This module provides heuristic-based matching of natural language
instructions to accessibility tree elements.  No external LLM calls
are made — matching uses keyword extraction, role/name scoring, and
action verb detection.
"""

from __future__ import annotations

import asyncio
import json
import re
from dataclasses import dataclass, field
from typing import Any

from wavexis.backend.base import AbstractBackend

_ACT_ACTION_TIMEOUT = 30.0

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
        node_id: Optional accessibility node ID from the backend.
        backend_node_id: Optional backend DOM node ID for precise targeting.
    """

    ref: str
    role: str
    name: str
    action: str
    score: float
    selector: str | None = None
    node_id: str | None = None
    backend_node_id: str | None = None
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
        "the",
        "a",
        "an",
        "on",
        "in",
        "at",
        "to",
        "of",
        "for",
        "and",
        "or",
        "with",
        "that",
        "this",
        "is",
        "are",
        "into",
        "from",
        "by",
        "over",
        "up",
        "down",
        "off",
        "out",
        "under",
        "above",
        "below",
        "through",
        "during",
        "before",
        "after",
        "near",
    }
    words = re.findall(r"[^\W\d_]+", instruction.lower())
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
        List of flat node dicts with ``ref``, ``role``, ``name``, ``path``,
        ``node_id`` and ``backend_node_id``.
    """
    flat: list[dict[str, Any]] = []
    for node in nodes:
        path = (parent_path or []) + [node.get("ref", "")]
        entry: dict[str, Any] = {
            "ref": node.get("ref", ""),
            "role": node.get("role", "unknown"),
            "name": node.get("name", ""),
            "path": path,
        }
        if node.get("node_id"):
            entry["node_id"] = node["node_id"]
        if node.get("backend_node_id"):
            entry["backend_node_id"] = node["backend_node_id"]
        flat.append(entry)
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


def _escape_css_attr(value: str) -> str:
    """Escape a string for safe use inside a CSS attribute selector.

    Double quotes and backslashes are escaped so the value cannot break
    out of ``[aria-label="..."]``.
    """
    return value.replace("\\", "\\\\").replace('"', '\\"')


def _role_matches(
    element_role: str,
    tag_name: str,
    dom_role: str | None,
    el_type: str | None,
) -> bool:
    """Check whether a DOM element matches an ARIA role from the a11y tree."""
    role = element_role.lower()
    tag = tag_name.lower()
    dom = (dom_role or "").lower()
    el_type = (el_type or "").lower()
    if role in ("button", "submit"):
        return (
            tag == "button" or el_type in ("button", "submit", "image", "reset") or dom == "button"
        )
    if role == "link":
        return tag == "a" or dom == "link"
    if role in ("textbox", "searchbox"):
        return (
            tag in ("input", "textarea")
            or el_type == "text"
            or dom
            in (
                "textbox",
                "searchbox",
            )
        )
    if role == "combobox":
        return tag == "select" or dom == "combobox"
    if role == "checkbox":
        return el_type == "checkbox" or dom == "checkbox"
    if role == "radio":
        return el_type == "radio" or dom == "radio"
    if role == "heading":
        return tag in ("h1", "h2", "h3", "h4", "h5", "h6") or dom == "heading"
    if role == "tab":
        return dom == "tab" or el_type == "tab"
    if role == "listbox":
        return tag == "select" or dom == "listbox"
    return True


def _build_action_script(role: str, name: str, action: str, value: str | None) -> str:
    """Build a JavaScript snippet that finds an element by role+name and acts on it.

    This is the fallback used by ``execute_act`` when the CSS selector derived from
    the accessibility tree does not match an element in the real DOM.
    """
    safe_role = json.dumps(role)
    safe_name = json.dumps(name)
    safe_action = json.dumps(action)
    safe_value = json.dumps(value or "")

    lines: list[str] = [
        "(function() {",
        f"  const role = {safe_role}.toLowerCase();",
        f"  const name = {safe_name}.toLowerCase();",
        f"  const action = {safe_action};",
        f"  const value = {safe_value};",
        "",
        "  function roleMatches(el) {",
        "    const tag = el.tagName.toLowerCase();",
        "    const domRole = (el.getAttribute('role') || '').toLowerCase();",
        "    const type = (el.type || '').toLowerCase();",
        "    if (role === 'button' || role === 'submit') {",
        "      return (",
        "        tag === 'button'",
        "        || type in {'button':1,'submit':1,'image':1,'reset':1}",
        "        || domRole === 'button'",
        "      );",
        "    }",
        "    if (role === 'link') return tag === 'a' || domRole === 'link';",
        "    if (role === 'textbox' || role === 'searchbox') {",
        "      return (",
        "        tag === 'textarea'",
        "        || tag === 'input'",
        "        || domRole === 'textbox'",
        "        || domRole === 'searchbox'",
        "      );",
        "    }",
        "    if (role === 'combobox') return tag === 'select' || domRole === 'combobox';",
        "    if (role === 'checkbox') return type === 'checkbox' || domRole === 'checkbox';",
        "    if (role === 'radio') return type === 'radio' || domRole === 'radio';",
        "    if (role === 'heading') return /^h[1-6]$/.test(tag) || domRole === 'heading';",
        "    if (role === 'tab') return domRole === 'tab' || type === 'tab';",
        "    if (role === 'listbox') return tag === 'select' || domRole === 'listbox';",
        "    return true;",
        "  }",
        "",
        "  function nameMatches(el) {",
        "    if (!name) return true;",
        "    const texts = [];",
        "    const ariaLabel = el.getAttribute('aria-label');",
        "    if (ariaLabel) texts.push(ariaLabel);",
        "    const label = el.labels && el.labels[0] ?",
        "      el.labels[0].textContent : '';",
        "    if (label) texts.push(label);",
        "    const title = el.getAttribute('title') || '';",
        "    if (title) texts.push(title);",
        "    const placeholder = el.getAttribute('placeholder') || '';",
        "    if (placeholder) texts.push(placeholder);",
        "    const elValue = el.value || '';",
        "    if (elValue && (el.tagName === 'INPUT' || el.tagName === 'SELECT')) {",
        "      texts.push(elValue);",
        "    }",
        "    if (el.alt) texts.push(el.alt);",
        "    texts.push(el.textContent || '');",
        "    const all = texts.join(' ')",
        "      .toLowerCase().replace(/\\s+/g, ' ').trim();",
        "    return all.includes(name) || name.includes(all);",
        "  }",
        "",
        "  const all = document.querySelectorAll('*');",
        "  let el = null;",
        "  for (let i = 0; i < all.length; i++) {",
        "    const candidate = all[i];",
        "    if (roleMatches(candidate) && nameMatches(candidate)) {",
        "      el = candidate;",
        "      break;",
        "    }",
        "  }",
        "",
        "  if (!el) {",
        f"    const msg = 'No DOM element matched role ' + role +       ' and name {safe_name}';",
        "    return JSON.stringify({status: 'error', error: msg});",
        "  }",
        "",
        "  el.scrollIntoView({block: 'center', behavior: 'instant'});",
        "",
        "  function dispatchMouse(type) {",
        "    const rect = el.getBoundingClientRect();",
        "    const x = rect.left + rect.width / 2;",
        "    const y = rect.top + rect.height / 2;",
        "    const opts = {bubbles: true, cancelable: true, view: window,",
        "      clientX: x, clientY: y, button: 0,",
        "      buttons: type === 'mousedown' ? 1 : 0};",
        "    el.dispatchEvent(new MouseEvent(type, opts));",
        "  }",
        "",
        "  if (action === 'click') {",
        "    dispatchMouse('mousedown');",
        "    dispatchMouse('mouseup');",
        "    dispatchMouse('click');",
        "    el.click();",
        "  } else if (action === 'focus') {",
        "    el.focus();",
        "  } else if (action === 'hover') {",
        "    const rect = el.getBoundingClientRect();",
        "    const x = rect.left + rect.width / 2;",
        "    const y = rect.top + rect.height / 2;",
        "    const hoverOpts = {bubbles: true, cancelable: true, view: window,",
        "      clientX: x, clientY: y};",
        "    el.dispatchEvent(new MouseEvent('mouseover', hoverOpts));",
        "    el.dispatchEvent(new MouseEvent('mouseenter', hoverOpts));",
        "  } else if (action === 'fill' || action === 'type') {",
        "    const editable = el.tagName === 'INPUT'",
        "      || el.tagName === 'TEXTAREA'",
        "      || el.tagName === 'SELECT'",
        "      || el.isContentEditable;",
        "    if (!editable) {",
        "      const err = 'Target element is not an editable input';",
        "      return JSON.stringify({status: 'error', error: err});",
        "    }",
        "    el.focus();",
        "    if (action === 'fill') el.value = value;",
        "    else el.value += value;",
        "    el.dispatchEvent(new Event('input', {bubbles: true}));",
        "    el.dispatchEvent(new Event('change', {bubbles: true}));",
        "    const lastKey = value.slice(-1) || 'x';",
        "    el.dispatchEvent(new KeyboardEvent('keyup',",
        "      {bubbles: true, key: lastKey}));",
        "  }",
        "",
        "  const outText = (el.textContent || '').trim().slice(0, 80);",
        "  return JSON.stringify({",
        "    status: 'ok', tag: el.tagName, id: el.id || '',",
        "    class: el.className || '', text: outText",
        "  });",
        "})()",
    ]
    return "\n".join(lines)


async def _execute_action_via_js(
    backend: AbstractBackend,
    role: str,
    name: str,
    action: str,
    value: str | None,
) -> None:
    """Execute an action on the best matching DOM element via in-page JavaScript.

    Raises:
        RuntimeError: if no matching element is found or the action cannot be performed.
    """
    import json as _json

    script = _build_action_script(role, name, action, value)
    raw = await backend.eval(script, await_promise=False)
    # backend.eval may return a string or an object depending on the protocol.
    if isinstance(raw, str):
        try:
            result = _json.loads(raw)
        except _json.JSONDecodeError:
            result = {"status": "error", "error": f"Unexpected JS result: {raw!r}"}
    elif isinstance(raw, dict):
        result = raw
    else:
        result = {
            "status": "error",
            "error": f"Unexpected JS result type: {type(raw).__name__}",
        }

    if result.get("status") != "ok":
        raise RuntimeError(result.get("error", "JavaScript action fallback failed"))


def _derive_selector(name: str | None, role: str | None, ref: str) -> str:
    """Derive a CSS selector from the a11y element data.

    Prefers ``[aria-label]`` when the accessible name is present. If the name is
    unavailable we fall back to the element ref as a selector placeholder; the
    JavaScript fallback in ``execute_act`` then resolves the element by role+name.
    """
    if name:
        escaped = _escape_css_attr(name)
        return f'[aria-label="{escaped}"]'
    return f"#{ref}"


def _semantic_keywords(
    instruction: str, action: str, keywords: list[str], role_keywords: set[str]
) -> list[str]:
    """Return the descriptive keywords an element must satisfy to be a match.

    Filters out action verbs, quoted input values, and role keywords/synonyms so
    that only words describing the target element remain. Input values are only
    stripped for ``type`` or ``fill`` actions.
    """
    value: str | None = None
    if action in ("type", "fill"):
        value = _extract_value(instruction, action)

    role_synonyms: set[str] = set()
    for rk in role_keywords:
        role_synonyms.update(_ROLE_KEYWORDS.get(rk, set()))

    action_verbs = set(_ACTION_VERBS.keys())
    result: list[str] = []
    for kw in keywords:
        if kw in (action, value) or kw in action_verbs:
            continue
        if kw in role_keywords or kw in role_synonyms:
            continue
        result.append(kw)
    return result


def _extract_value(instruction: str, action: str) -> str | None:
    """Extract the text value to type or fill from an instruction.

    Quoted strings (``type "hello"``) take precedence.  Otherwise the first
    keyword that is not the action verb or a matched role synonym is used.

    Args:
        instruction: Raw user instruction.
        action: Detected action verb (``"type"`` or ``"fill"``).

    Returns:
        The extracted value, or ``None`` if no value is present.
    """
    quoted = re.search(r'["\']([^"\']+)["\']', instruction)
    if quoted:
        return quoted.group(1)

    keywords = _extract_keywords(instruction)
    role_keywords = _detect_role_keywords(keywords)
    role_synonyms: set[str] = set()
    for rk in role_keywords:
        role_synonyms.update(_ROLE_KEYWORDS.get(rk, set()))

    for kw in keywords:
        if kw == action or kw in _ACTION_VERBS or kw in role_synonyms:
            continue
        return kw
    return None


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
    if not instruction or not instruction.strip():
        return None

    keywords = _extract_keywords(instruction)
    if not keywords:
        return None

    action = _detect_action(instruction)
    role_keywords = _detect_role_keywords(keywords)

    # Action verbs and typed values should not influence the name/role scoring.
    value = _extract_value(instruction, action) if action in ("type", "fill") else None
    scoring_keywords = [kw for kw in keywords if kw not in _ACTION_VERBS and kw != value]

    flat = _flatten_tree(tree)

    best: MatchResult | None = None
    best_score = 0.0

    for element in flat:
        score = _score_element(element, scoring_keywords, role_keywords)
        if score > best_score:
            best_score = score
            best = MatchResult(
                ref=element["ref"],
                role=element["role"],
                name=element["name"],
                action=action,
                score=score,
                node_id=element.get("node_id"),
                backend_node_id=element.get("backend_node_id"),
            )

    if best is None or best_score <= 0:
        return None

    # Require at least one descriptive keyword to be present in the element's
    # name or role, otherwise generic instructions like "click the elephant
    # button" would match any button on the page.
    semantic_keywords = _semantic_keywords(instruction, action, keywords, role_keywords)
    if semantic_keywords:
        match_text = f"{best.name} {best.role}".lower()
        if not any(kw in match_text for kw in semantic_keywords):
            return None

    return best


async def execute_act(
    backend: AbstractBackend,
    instruction: str,
    tree: list[dict[str, Any]],
    max_retries: int = 3,
    value: str | None = None,
) -> dict[str, Any]:
    """Execute a natural language instruction against the browser.

    Takes an a11y tree, matches the instruction to an element, and
    performs the detected action (click, type, fill, hover).

    Args:
        backend: wavexis ``AbstractBackend`` instance.
        instruction: Natural language instruction.
        tree: Formatted a11y tree.
        max_retries: Maximum retry attempts if action fails.
        value: Optional explicit value for ``type`` or ``fill`` actions.
            When omitted, the value is extracted from the instruction.

    Returns:
        Dict with ``action``, ``element``, ``score``, ``status`` and
        ``value`` when applicable.
    """
    match = match_instruction(instruction, tree)
    if match is None:
        return {
            "status": "no_match",
            "instruction": instruction,
            "message": "No matching element found in accessibility tree.",
        }

    selector = _derive_selector(match.name, match.role, match.ref)

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

    text_value = value if value is not None else _extract_value(instruction, match.action)
    if text_value is not None:
        result["value"] = text_value

    last_error: Exception | None = None
    for attempt in range(max_retries):
        try:
            if match.action == "click":
                await asyncio.wait_for(backend.click(selector), timeout=_ACT_ACTION_TIMEOUT)
            elif match.action == "type":
                await asyncio.wait_for(
                    backend.type_text(selector, text_value or ""),
                    timeout=_ACT_ACTION_TIMEOUT,
                )
            elif match.action == "fill":
                await asyncio.wait_for(
                    backend.fill(selector, text_value or ""),
                    timeout=_ACT_ACTION_TIMEOUT,
                )
            elif match.action == "hover":
                await asyncio.wait_for(backend.hover(selector), timeout=_ACT_ACTION_TIMEOUT)
            elif match.action == "focus":
                await asyncio.wait_for(backend.dom_focus(selector), timeout=_ACT_ACTION_TIMEOUT)

            result["status"] = "ok"
            result["attempts"] = attempt + 1
            return result
        except Exception as e:
            last_error = e
            # On the last attempt, fall back to a JavaScript search by role+name.
            if attempt == max_retries - 1:
                try:
                    await _execute_action_via_js(
                        backend,
                        match.role,
                        match.name,
                        match.action,
                        text_value,
                    )
                    result["status"] = "ok"
                    result["attempts"] = attempt + 1
                    result["fallback"] = "js"
                    return result
                except Exception as js_err:
                    result["status"] = "error"
                    result["error"] = f"{last_error}; JS fallback: {js_err}"
                    result["attempts"] = attempt + 1
            # Retry with the same selector on transient errors.

    return result
