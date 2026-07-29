"""Generate MCPB manifest for Smithery with flattened JSON schemas.

Resolves $ref references so Smithery's scanner can see all parameter
descriptions at the top level of each tool's inputSchema.

Usage:
    python scripts/generate_smithery_manifest.py

Output:
    mcpb-build/manifest.json  — manifest with flattened schemas
    mcpb-build/icon.png       — generated icon
    wavexis-mcp.mcpb          — bundle ready for ``smithery mcp publish``
"""

from __future__ import annotations

import asyncio
import json
import math
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw

from wavexis_mcp.server import create_server


def resolve_ref(ref: str, defs: dict) -> dict:
    """Resolve a $ref pointer like '#/$defs/SessionOpenInput'."""
    parts = ref.lstrip("#/").split("/")
    obj: dict | list = {"$defs": defs}
    for part in parts:
        obj = obj[part]  # type: ignore[assignment]
    return obj  # type: ignore[return-value]


def flatten_schema(schema: dict) -> dict:
    """Flatten a JSON schema by resolving $ref and inlining $defs properties.

    Smithery's scanner doesn't resolve $ref, so we inline the referenced
    model's properties at the top level.
    """
    defs = schema.get("$defs", {})
    props = schema.get("properties", {})

    flattened_props: dict = {}
    required: list[str] = []

    for prop_name, prop_schema in props.items():
        if isinstance(prop_schema, dict) and "$ref" in prop_schema:
            resolved = resolve_ref(prop_schema["$ref"], defs)
            inner_props = resolved.get("properties", {})
            inner_required = resolved.get("required", [])
            for inner_name, inner_schema in inner_props.items():
                flattened_props[inner_name] = inner_schema
            required.extend(inner_required)
        else:
            flattened_props[prop_name] = prop_schema
            if prop_name in schema.get("required", []):
                required.append(prop_name)

    result: dict = {
        "type": "object",
        "properties": flattened_props,
    }
    if required:
        result["required"] = list(set(required))
    return result


def generate_icon(path: Path) -> None:
    """Generate a 256x256 PNG icon for the MCPB bundle."""
    size = 256
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    for y in range(size):
        t = y / size
        r = int(63 + (26 - 63) * t)
        g = int(81 + (35 - 81) * t)
        b = int(181 + (126 - 181) * t)
        draw.line([(16, y), (size - 16, y)], fill=(r, g, b, 255))

    mask = Image.new("L", (size, size), 0)
    mdraw = ImageDraw.Draw(mask)
    mdraw.rounded_rectangle([16, 16, size - 16, size - 16], radius=48, fill=255)
    img.putalpha(mask)

    def draw_wave(draw: ImageDraw.ImageDraw, y_mid: int, amplitude: int, color: tuple, width: int, opacity: int) -> None:
        points = []
        for x in range(56, 200):
            t = (x - 56) / 144
            y = y_mid + amplitude * math.sin(t * math.pi * 3)
            points.append((x, y))
        if len(points) > 1:
            draw.line(points, fill=color + (opacity,), width=width)

    draw_wave(draw, 120, 15, (255, 255, 255), 4, 100)
    draw_wave(draw, 150, 20, (255, 255, 255), 6, 255)

    for cx in [80, 128, 176]:
        draw.ellipse([cx - 7, 190 - 7, cx + 7, 190 + 7], fill=(255, 255, 255, 230))
    draw.line([87, 190, 121, 190], fill=(255, 255, 255, 130), width=2)
    draw.line([135, 190, 169, 190], fill=(255, 255, 255, 130), width=2)

    img.save(path)


async def main() -> None:
    mcp = create_server(caps="all")
    tools = await mcp.list_tools()

    build_dir = Path(__file__).parent.parent / "mcpb-build"
    build_dir.mkdir(exist_ok=True)
    manifest_path = build_dir / "manifest.json"
    icon_path = build_dir / "icon.png"

    tools_data = []
    for t in tools:
        flat_schema = flatten_schema(t.inputSchema or {})
        tools_data.append({
            "name": t.name,
            "description": (t.description or "").split("\n")[0][:200],
            "inputSchema": flat_schema,
        })

    manifest = {
        "manifest_version": "0.4",
        "name": "wavexis-mcp",
        "display_name": "WaveXisMCP",
        "version": "1.6.24",
        "description": (
            "220 browser automation tools for Chrome, Edge, and Firefox via "
            "CDP + BiDi. 100% Python, no Node.js, no Chromium download — "
            "uses your existing browser. 13 capability tiers, stealth mode, "
            "Lighthouse audits, multi-action YAML, structured errors with "
            "LLM-actionable suggestions."
        ),
        "long_description": (
            "WaveXisMCP is a Python-based MCP server providing 220 browser "
            "automation tools for LLMs across 13 capability tiers. Control "
            "Chrome/Edge via CDP or Firefox via BiDi without Node.js or "
            "Chromium downloads. Features include stealth mode, Lighthouse "
            "audits, multi-action YAML batching, structured errors with "
            "LLM-actionable suggestions, and natural language interaction."
        ),
        "author": {
            "name": "Mathias Paulenko",
            "url": "https://github.com/MathiasPaulenko",
        },
        "repository": {
            "type": "git",
            "url": "https://github.com/MathiasPaulenko/wavexis-mcp",
        },
        "homepage": "https://mathiaspaulenko.github.io/wavexis-mcp/",
        "documentation": "https://mathiaspaulenko.github.io/wavexis-mcp/",
        "support": "https://github.com/MathiasPaulenko/wavexis-mcp/issues",
        "icon": "icon.png",
        "server": {
            "type": "node",
            "entry_point": "server.py",
            "mcp_config": {
                "command": "uvx",
                "args": ["wavexis-mcp", "--caps", "${user_config.caps}"],
            },
        },
        "compatibility": {
            "platforms": ["darwin", "linux", "win32"],
            "runtimes": {"python": ">=3.11"},
        },
        "keywords": [
            "browser-automation",
            "cdp",
            "bidi",
            "chrome",
            "firefox",
            "scraping",
            "testing",
            "stealth",
            "lighthouse",
            "playwright-alternative",
            "selenium-alternative",
            "mcp",
        ],
        "license": "MIT",
        "tools": tools_data,
        "tools_generated": True,
        "user_config": {
            "caps": {
                "type": "string",
                "title": "Capability Tiers",
                "description": (
                    "Comma-separated capability tiers to enable "
                    "(e.g. 'core', 'all', 'core,network,storage')"
                ),
                "default": "all",
                "required": False,
            }
        },
    }

    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Wrote manifest with {len(tools_data)} tools (flattened schemas)")

    total_params = 0
    params_with_desc = 0
    for t in tools_data:
        props = t["inputSchema"].get("properties", {})
        for pname, pschema in props.items():
            total_params += 1
            if isinstance(pschema, dict) and pschema.get("description"):
                params_with_desc += 1

    print(f"Parameter descriptions: {params_with_desc}/{total_params} "
          f"= {params_with_desc / total_params * 100:.1f}%")

    generate_icon(icon_path)
    print(f"Generated {icon_path}")

    mcpb_path = build_dir.parent / "wavexis-mcp.mcpb"
    with zipfile.ZipFile(mcpb_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(manifest_path, "manifest.json")
        zf.write(icon_path, "icon.png")

    print(f"Created {mcpb_path} ({mcpb_path.stat().st_size} bytes)")
    print()
    print("Publish with:")
    print("  smithery mcp publish wavexis-mcp.mcpb -n mathias-paulenko/wavexis-mcp")


if __name__ == "__main__":
    asyncio.run(main())
