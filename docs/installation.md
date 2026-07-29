# Installation

WaveXisMCP requires Python 3.11+ and an existing Chrome/Edge or Firefox installation.

## Install from PyPI

```bash
pip install wavexis-mcp
```

Or with [`uv`](https://docs.astral.sh/uv/):

```bash
uv pip install wavexis-mcp
```

## Run with uvx (no install)

```bash
uvx wavexis-mcp
```

## Verify the installation

```bash
wavexis-mcp --help
```

You should see the CLI help with available flags.

## System requirements

| Requirement | Details |
| --- | --- |
| Python | 3.11 or higher |
| Browser | Chrome 116+, Edge 116+, or Firefox 120+ |
| OS | Windows, macOS, or Linux |
| Node.js | **Not required** — 100% Python |

## MCP client configuration

### Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "wavexis": {
      "command": "uvx",
      "args": ["wavexis-mcp", "--caps", "all"]
    }
  }
}
```

### Cursor

Add to `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "wavexis": {
      "command": "uvx",
      "args": ["wavexis-mcp", "--caps", "all"]
    }
  }
}
```

### Windsurf

Add to your Windsurf MCP config:

```json
{
  "mcpServers": {
    "wavexis": {
      "command": "uvx",
      "args": ["wavexis-mcp", "--caps", "core,network,storage"]
    }
  }
}
```

### VS Code

Add to `.vscode/mcp.json`:

```json
{
  "servers": {
    "wavexis": {
      "command": "uvx",
      "args": ["wavexis-mcp", "--caps", "all"]
    }
  }
}
```

## Capability tiers

The `--caps` flag controls which tools are registered. See [Capability Tiers](capability-tiers.md) for the full list.

```bash
# All 220 tools (default)
uvx wavexis-mcp --caps all

# Only core tools (minimal, fastest startup)
uvx wavexis-mcp --caps core

# Pick specific tiers
uvx wavexis-mcp --caps core,network,storage,a11y
```

## Next steps

- [Quick Start](quickstart.md) — your first browser automation task
- [Configuration](configuration.md) — all CLI flags and env vars
- [Capability Tiers](capability-tiers.md) — choose the right tools for your use case
