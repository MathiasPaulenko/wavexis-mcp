---
name: Bug report
about: Report a bug in WaveXisMCP
title: "[BUG] "
labels: bug
assignees: ''
---

## Describe the bug

A clear and concise description of what the bug is.

## To reproduce

Steps to reproduce the behavior:

1. Start the server with `wavexis-mcp --caps ...`
2. Call tool `wavexis_...` with input `...`
3. See error

## Expected behavior

What you expected to happen.

## Actual behavior

What actually happened (include error output, stack trace, or screenshot).

## Environment

- OS: [e.g. Windows 11, macOS 14, Ubuntu 22.04]
- Python: [e.g. 3.12.1]
- wavexis-mcp: [e.g. 0.1.0]
- wavexis: [e.g. 2.3.0]
- Backend: [cdp / bidi]
- MCP client: [e.g. Claude Desktop, Cursor, Windsurf]

## MCP client config

```json
{
  "mcpServers": {
    "wavexis-mcp": {
      "command": "wavexis-mcp",
      "args": ["--caps", "core"]
    }
  }
}
```
