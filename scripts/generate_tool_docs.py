"""Regenerate docs/tools/*.md from the actual registered MCP tools.

Produces rich documentation with:
- Tool name and full description
- Detailed parameter table (name, type, required, default, description)
- Per-section grouping
- Capability tier intro
"""

from __future__ import annotations

import sys
from pathlib import Path

# Make sure the repository root (not a possibly-installed site-package) is used.
repo_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo_root))

import wavexis_mcp.server as _server  # noqa: E402
from wavexis_mcp.server import create_server  # noqa: E402

_server._print_startup_info = lambda *args, **kwargs: None  # suppress banners while generating

TIER_ORDER = [
    "core",
    "network",
    "storage",
    "emulation",
    "a11y",
    "interactions",
    "devtools",
    "vision",
    "video",
    "testing",
    "workflows",
    "data",
    "experimental",
]

TIER_TITLE = {
    "core": "Core",
    "network": "Network",
    "storage": "Storage",
    "emulation": "Emulation",
    "a11y": "A11y",
    "interactions": "Interactions",
    "devtools": "DevTools",
    "vision": "Vision",
    "video": "Video",
    "testing": "Testing",
    "workflows": "Workflows",
    "data": "Data",
    "experimental": "Experimental",
}

TIER_DESCRIPTION = {
    "core": (
        "Always enabled — no `--caps` flag needed. "
        "Covers the essential browser automation workflow: "
        "session management, navigation, screenshots, DOM, "
        "JavaScript evaluation, tabs, cookies, and utility tools."
    ),
    "network": (
        "Network interception, request monitoring, HAR recording, "
        "and response mocking. Enable with `--caps=network`."
    ),
    "storage": (
        "localStorage, sessionStorage, IndexedDB, and cache management. "
        "Enable with `--caps=storage`."
    ),
    "emulation": (
        "Device emulation, geolocation spoofing, timezone override, "
        "and viewport manipulation. Enable with `--caps=emulation`."
    ),
    "a11y": (
        "Accessibility tree inspection, axe-core audits, and "
        "ARIA node queries. Enable with `--caps=a11y`."
    ),
    "interactions": (
        "Dialog handling, permission management, and download interception. "
        "Enable with `--caps=interactions`."
    ),
    "devtools": (
        "Console messages, performance metrics, CPU throttling, "
        "and raw CDP access. Enable with `--caps=devtools`."
    ),
    "vision": (
        "Lighthouse audits, WebAuthn, Bluetooth, and Cast. "
        "Enable with `--caps=vision`."
    ),
    "video": (
        "Video recording and playback capture. "
        "Enable with `--caps=video`."
    ),
    "testing": (
        "Visual regression, element screenshots, and test helpers. "
        "Enable with `--caps=testing`."
    ),
    "workflows": (
        "Multi-action YAML batching and natural language interaction. "
        "Enable with `--caps=workflows`."
    ),
    "data": (
        "Structured data extraction: tables, forms, metadata, OpenGraph. "
        "Enable with `--caps=data`."
    ),
    "experimental": (
        "Experimental and advanced tools — raw protocol access, "
        "CDP/BiDi escape hatch. Enable with `--caps=experimental`."
    ),
}

SECTION_MAP = {
    "wavexis_mcp.server": "Natural Language Interaction",
    "wavexis_mcp.tools.a11y": "Accessibility",
    "wavexis_mcp.tools.capture": "Screenshot / PDF / Capture",
    "wavexis_mcp.tools.cookies": "Cookies",
    "wavexis_mcp.tools.data": "Data Extraction",
    "wavexis_mcp.tools.devtools": "DevTools",
    "wavexis_mcp.tools.dom": "DOM",
    "wavexis_mcp.tools.emulation": "Emulation",
    "wavexis_mcp.tools.experimental": "Experimental",
    "wavexis_mcp.tools.input": "Input",
    "wavexis_mcp.tools.interactions": "Interactions",
    "wavexis_mcp.tools.javascript": "JavaScript",
    "wavexis_mcp.tools.navigation": "Navigation",
    "wavexis_mcp.tools.network": "Network",
    "wavexis_mcp.tools.playwright_parity": "Page Actions",
    "wavexis_mcp.tools.session": "Session Management",
    "wavexis_mcp.tools.storage": "Storage",
    "wavexis_mcp.tools.tabs": "Tabs",
    "wavexis_mcp.tools.testing": "Testing",
    "wavexis_mcp.tools.utility": "Utility",
    "wavexis_mcp.tools.vision": "Vision",
    "wavexis_mcp.tools.video": "Video",
    "wavexis_mcp.tools.workflows": "Workflows",
}


def _first_sentence(text: str) -> str:
    text = text.strip()
    if not text:
        return ""
    for i, ch in enumerate(text):
        if ch == "." and i + 1 < len(text) and text[i + 1] in (" ", "\n"):
            return text[: i + 1]
    return text + "." if not text.endswith(".") else text


def _full_description(text: str) -> str:
    """Return the full description, cleaned up."""
    return (text or "").strip()


def _resolve_input_schema(parameters: dict, defs: dict) -> dict:
    """If the tool takes a single Pydantic `input` arg, return that model schema."""
    props = parameters.get("properties", {})
    if set(props.keys()) == {"input"}:
        ref = props["input"].get("$ref")
        if ref and ref.startswith("#/$defs/"):
            name = ref.split("/")[-1]
            return defs.get(name, {})
    return parameters


def _type_str(schema: dict) -> str:
    """Render a JSON schema type as a readable string."""
    if not schema:
        return "—"
    if "$ref" in schema:
        return schema["$ref"].split("/")[-1]
    t = schema.get("type", "")
    if isinstance(t, list):
        # Filter out "null" and join the rest
        non_null = [x for x in t if x != "null"]
        if len(non_null) == 1:
            t = non_null[0]
        elif non_null:
            t = " | ".join(non_null)
        else:
            t = "null"
    if not t:
        if "enum" in schema:
            t = "enum"
        elif "anyOf" in schema:
            parts = []
            for s in schema["anyOf"]:
                p = _type_str(s)
                if p != "null":
                    parts.append(p)
            t = " | ".join(parts) if parts else "any"
        else:
            t = "any"
    if "enum" in schema:
        t += f" ({', '.join(str(v) for v in schema['enum'])})"
    return t


def _default_str(schema: dict) -> str:
    """Render the default value, or — if none."""
    if "default" in schema:
        default = schema["default"]
        if isinstance(default, str):
            return f'`"{default}"`'
        if isinstance(default, bool):
            return f"`{str(default).lower()}`"
        if default is None:
            return "`null`"
        return f"`{default}`"
    return "—"


def _params_table(tool) -> str:
    """Generate a detailed parameter table for a tool."""
    defs = tool.parameters.get("$defs", {})
    schema = _resolve_input_schema(tool.parameters, defs)
    props = schema.get("properties", {})
    required = set(schema.get("required", []))

    if not props:
        return "_This tool takes no parameters._"

    lines = [
        "| Parameter | Type | Required | Default | Description |",
        "| --- | --- | :---: | --- | --- |",
    ]

    for name, prop_schema in props.items():
        type_str = _type_str(prop_schema)
        is_required = "Yes" if name in required else "No"
        default_str = _default_str(prop_schema)
        desc = prop_schema.get("description", "—")
        # Truncate long descriptions for table readability
        if len(desc) > 120:
            desc = desc[:117] + "..."
        lines.append(f"| `{name}` | {type_str} | {is_required} | {default_str} | {desc} |")

    return "\n".join(lines)


def _params_summary(tool) -> str:
    """Generate a short parameter list for the summary table."""
    defs = tool.parameters.get("$defs", {})
    schema = _resolve_input_schema(tool.parameters, defs)
    props = schema.get("properties", {})
    required = set(schema.get("required", []))
    if not props:
        return "—"
    parts = []
    for name in props:
        if name in required:
            parts.append(name)
        else:
            parts.append(f"{name}?")
    return ", ".join(parts)


def generate(tier: str, tools: dict) -> str:
    title = TIER_TITLE[tier]
    count = len(tools)
    desc = TIER_DESCRIPTION.get(tier, "")

    lines = [f"# {title} Tools ({count})", ""]

    if tier == "core":
        lines.append("Always enabled. No `--caps` flag needed.")
    else:
        lines.append(f"Enable with `--caps={tier}`.")
    lines.append("")
    lines.append(desc)
    lines.append("")

    # Summary table
    lines.append("## Summary")
    lines.append("")
    lines.append("| Tool | Parameters | Description |")
    lines.append("| --- | --- | --- |")
    for name in sorted(tools):
        tool = tools[name]
        short_desc = _first_sentence(tool.description or "")
        params = _params_summary(tool)
        params_col = f"`{params}`" if params and params != "—" else "—"
        lines.append(f"| [`{name}`](#{name}) | {params_col} | {short_desc} |")
    lines.append("")

    # Detailed sections
    by_section: dict[str, list] = {}
    for name in sorted(tools):
        tool = tools[name]
        module = getattr(tool.fn, "__module__", "unknown")
        section = SECTION_MAP.get(
            module,
            module.replace("wavexis_mcp.tools.", "").replace("_", " ").title(),
        )
        by_section.setdefault(section, []).append(tool)

    for section_name, tool_list in by_section.items():
        lines.append(f"## {section_name}")
        lines.append("")

        for tool in tool_list:
            full_desc = _full_description(tool.description or "")
            # Tool heading
            lines.append(f"### {tool.name}")
            lines.append("")
            # Full description
            if full_desc:
                lines.append(full_desc)
                lines.append("")
            # Parameters
            lines.append("**Parameters:**")
            lines.append("")
            lines.append(_params_table(tool))
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    core_tools = create_server(caps="core")._tool_manager._tools
    core_names = set(core_tools.keys())

    out_dir = Path("docs/tools")
    out_dir.mkdir(exist_ok=True)
    for tier in TIER_ORDER:
        if tier == "core":
            tools = dict(core_tools)
        else:
            all_tools = create_server(caps=tier)._tool_manager._tools
            tools = {name: tool for name, tool in all_tools.items() if name not in core_names}
        text = generate(tier, tools)
        (out_dir / f"{tier}.md").write_text(text, encoding="utf-8")
        print(f"Wrote {tier}.md with {len(tools)} tools")


if __name__ == "__main__":
    main()
