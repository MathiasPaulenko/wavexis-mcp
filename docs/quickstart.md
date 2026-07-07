# Quick Start

## Install

```bash
pip install wavexis-mcp
```

With CDP backend (Chromium):

```bash
pip install "wavexis-mcp[cdp]"
```

Or run without installing:

```bash
uvx wavexis-mcp
```

## Configure your MCP client

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

### Cursor / Windsurf / VS Code

```json
{
  "mcpServers": {
    "wavexis": {
      "command": "wavexis-mcp",
      "args": ["--caps", "all"]
    }
  }
}
```

## First tool call

Once configured, ask your LLM to use a tool:

> Take a screenshot of <https://example.com>

The LLM will call `wavexis_screenshot(url="https://example.com")`, launch Chrome/Edge, capture the screenshot, and return it as base64.

## Session-based workflow

For multi-step workflows, open a session first:

```text
wavexis_session_open(backend="cdp", headless=false)
→ {"session_id": "abc-123"}

wavexis_navigate(session_id="abc-123", url="https://example.com")
wavexis_click(session_id="abc-123", selector="#login")
wavexis_screenshot(session_id="abc-123")
wavexis_session_close(session_id="abc-123")
```

## Verify installation

```bash
wavexis-mcp --help
```

Output shows available tiers and configuration.
