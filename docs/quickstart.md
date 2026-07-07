# Quick Start

This guide walks you through installing WaveXisMCP, configuring it in your LLM client, and making your first browser automation tool call.

## Prerequisites

- **Python 3.11+** — WaveXisMCP requires Python 3.11 or newer
- **Chrome or Edge** — a Chromium-based browser installed on your machine (Chrome, Edge, Brave, Chromium). WaveXisMCP launches your existing browser — no separate Chromium download.
- **An MCP-compatible LLM client** — Claude Desktop, Cursor, Windsurf, VS Code with MCP support, or any client that speaks the Model Context Protocol

!!! note "No Node.js required"
    Unlike Playwright MCP, WaveXisMCP is 100% Python. You do not need Node.js, npm, or any JavaScript runtime.

## Install

### Option A: pip (recommended for development)

```bash
pip install wavexis-mcp
```

With CDP backend (Chromium-native, no driver needed):

```bash
pip install "wavexis-mcp[cdp]"
```

With BiDi backend (W3C cross-browser, needs ChromeDriver/EdgeDriver):

```bash
pip install "wavexis-mcp[bidi]"
```

With both backends:

```bash
pip install "wavexis-mcp[cdp,bidi]"
```

### Option B: uvx (zero install, recommended for end users)

```bash
uvx wavexis-mcp
```

`uvx` downloads WaveXisMCP into an isolated environment and runs it. No virtualenv needed. This is the easiest way to use WaveXisMCP — just point your MCP client at `uvx wavexis-mcp`.

### Verify installation

```bash
wavexis-mcp --help
```

You should see output listing available CLI flags, capability tiers, and transport options.

## Configure your MCP client

WaveXisMCP runs as a **stdio MCP server** by default. Your LLM client launches it as a subprocess and communicates over stdin/stdout.

### Claude Desktop

Add to `claude_desktop_config.json` (typically at `~/Library/Application Support/Claude/claude_desktop_config.json` on macOS or `%APPDATA%\Claude\claude_desktop_config.json` on Windows):

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

Add to your MCP settings:

=== "uvx"

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

=== "pip installed"

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

### Capability tiers

The `--caps` flag controls which tools are exposed to the LLM. With 172 tools total, exposing all of them can overwhelm smaller LLMs with long tool lists. Choose a tier that matches your use case:

| Flag | Tools | Use case |
|------|-------|----------|
| `--caps core` | 42 | Default. Session, navigation, screenshot, DOM, input. Good for simple tasks. |
| `--caps core,network,storage` | 65 | Add network control and storage access. Good for scraping. |
| `--caps core,a11y,interactions,devtools` | 74 | Add accessibility, dialogs, and DevTools. Good for testing. |
| `--caps all` | 172 | Everything. Good for power users and automation. |

See [Configuration](configuration.md) for the full list of tiers.

## First tool call

Once configured, restart your LLM client and ask it to use a tool:

> Take a screenshot of https://example.com

The LLM will:

1. Call `wavexis_screenshot(url="https://example.com")`
2. WaveXisMCP launches Chrome/Edge in headless mode
3. Navigates to `https://example.com`
4. Captures a screenshot
5. Returns it as base64-encoded PNG
6. Closes the browser
7. The LLM receives the screenshot and shows it to you

This is **stateless mode** — the browser launches, executes one action, and closes automatically. No session management needed.

## Session-based workflow

For multi-step tasks (navigate → click → fill → screenshot), use sessions. A session keeps the browser open across multiple tool calls:

```text
# 1. Open a session — launches Chrome/Edge and keeps it running
wavexis_session_open(backend="cdp", headless=false)
→ {"session_id": "abc-123"}

# 2. Navigate to a page
wavexis_navigate(session_id="abc-123", url="https://example.com")

# 3. Click a button
wavexis_click(session_id="abc-123", selector="#login")

# 4. Fill a form field
wavexis_fill(session_id="abc-123", selector="#email", value="user@example.com")

# 5. Take a screenshot to verify
wavexis_screenshot(session_id="abc-123")

# 6. Close the session — kills the browser process
wavexis_session_close(session_id="abc-123")
```

### Why sessions?

| Stateless | Session |
|-----------|---------|
| Browser launches per call | Browser launches once |
| Browser closes after call | Browser stays open |
| No state between calls | Full state (cookies, localStorage, page context) |
| Good for one-shot tasks | Good for multi-step workflows |
| Pass `url=` parameter | Pass `session_id=` parameter |

### Backend selection

When opening a session, choose your backend:

```text
# CDP — Chromium-native, no driver needed (default)
wavexis_session_open(backend="cdp")

# BiDi — W3C cross-browser, needs ChromeDriver/EdgeDriver
wavexis_session_open(backend="bidi")
```

CDP is recommended for Chrome/Edge only. BiDi enables Firefox support but requires a driver binary.

## Natural language interaction

The `wavexis_act` tool (requires `--caps=a11y`) lets the LLM interact with pages using natural language instead of CSS selectors:

```text
wavexis_session_open(backend="cdp")
wavexis_navigate(session_id="abc-123", url="https://example.com")

# The LLM can say "click the login button" instead of knowing the selector
wavexis_act(session_id="abc-123", instruction="click the login button")
→ {"action": "click", "element": {"ref": "el-3", "role": "button", "name": "Login"}, "status": "ok"}

wavexis_session_close(session_id="abc-123")
```

`wavexis_act` takes an accessibility snapshot, matches the instruction to an element using keyword scoring, and executes the detected action. No external LLM calls — pure heuristic matching.

## Next steps

- [Configuration](configuration.md) — learn about all 13 capability tiers and CLI flags
- [Architecture](architecture.md) — understand the system design and data flow
- [Tools reference](tools/core.md) — browse all 172 tools by tier
- [Examples](examples/screenshot.md) — real-world usage patterns
