"""Regenerate docs/tools/*.md from the actual registered MCP tools."""

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

SECTION_MAP = {
    "wavexis_mcp.server": "Natural language interaction",
    "wavexis_mcp.tools.a11y": "Accessibility",
    "wavexis_mcp.tools.capture": "Screenshot / PDF / Capture",
    "wavexis_mcp.tools.cookies": "Cookies",
    "wavexis_mcp.tools.data": "Data extraction",
    "wavexis_mcp.tools.devtools": "DevTools",
    "wavexis_mcp.tools.dom": "DOM",
    "wavexis_mcp.tools.emulation": "Emulation",
    "wavexis_mcp.tools.experimental": "Experimental",
    "wavexis_mcp.tools.input": "Input",
    "wavexis_mcp.tools.interactions": "Interactions",
    "wavexis_mcp.tools.javascript": "JavaScript",
    "wavexis_mcp.tools.navigation": "Navigation",
    "wavexis_mcp.tools.network": "Network",
    "wavexis_mcp.tools.playwright_parity": "Page actions",
    "wavexis_mcp.tools.session": "Session management",
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


def _resolve_input_schema(parameters: dict, defs: dict) -> dict:
    """If the tool takes a single Pydantic `input` arg, return that model schema."""
    props = parameters.get("properties", {})
    if set(props.keys()) == {"input"}:
        ref = props["input"].get("$ref")
        if ref and ref.startswith("#/$defs/"):
            name = ref.split("/")[-1]
            return defs.get(name, {})
    return parameters


def _params(tool) -> str:
    defs = tool.parameters.get("$defs", {})
    schema = _resolve_input_schema(tool.parameters, defs)
    props = schema.get("properties", {})
    required = set(schema.get("required", []))
    if not props:
        return ""
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
    lines = [f"# {title} Tools ({count})"]
    if tier == "core":
        lines.append("")
        lines.append("Always enabled. No `--caps` flag needed.")
        lines.append("")
        lines.append(
            "Core tools cover the essential browser automation workflow. "
            f"These {count} tools are always registered regardless of which "
            "capability tiers you enable."
        )
    else:
        lines.append("")
        lines.append(f"Enable with `--caps={tier}`.")
        lines.append("")
        lines.append(f"These {count} tools are added when the `{tier}` capability tier is enabled.")
    lines.append("")

    by_section: dict[str, list] = {}
    for name in sorted(tools):
        tool = tools[name]
        module = getattr(tool.fn, "__module__", "unknown")
        section = SECTION_MAP.get(
            module, module.replace("wavexis_mcp.tools.", "").replace("_", " ").title()
        )
        by_section.setdefault(section, []).append(tool)

    for section_name, tool_list in by_section.items():
        lines.append(f"## {section_name}")
        lines.append("")
        lines.append("| Tool | Parameters | Description |")
        lines.append("| --- | --- | --- |")
        for tool in tool_list:
            desc = _first_sentence(tool.description or "")
            params = _params(tool)
            params_col = f"`{params}`" if params else "—"
            lines.append(f"| `{tool.name}` | {params_col} | {desc} |")
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
