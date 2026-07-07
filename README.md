<p align="center">
  <img src="docs/assets/images/logo-wide.svg" alt="WaveXisMCP" width="480">
</p>

<h3 align="center">MCP server — 158 browser automation tools for LLMs</h3>

---

[![CI](https://github.com/MathiasPaulenko/wavexis-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/MathiasPaulenko/wavexis-mcp/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/wavexis-mcp.svg)](https://pypi.org/project/wavexis-mcp/)
[![Python](https://img.shields.io/pypi/pyversions/wavexis-mcp.svg)](https://pypi.org/project/wavexis-mcp/)
[![Docker](https://img.shields.io/badge/Docker-ghcr.io-blue.svg)](https://github.com/MathiasPaulenko/wavexis-mcp/pkgs/container/wavexis-mcp)
[![License](https://img.shields.io/github/license/MathiasPaulenko/wavexis-mcp.svg)](https://github.com/MathiasPaulenko/wavexis-mcp/blob/main/LICENSE)
[![Docs](https://img.shields.io/badge/docs-mkdocs-blue.svg)](https://mathiaspaulenko.github.io/wavexis-mcp/)

> MCP server that exposes the [wavexis](https://github.com/MathiasPaulenko/wavexis) browser automation library to LLMs. 158 tools across 13 capability tiers. No Node.js, no Chromium download — uses your existing Chrome/Edge. 100% Python.

## Why WaveXisMCP?

WaveXisMCP wraps the [wavexis](https://github.com/MathiasPaulenko/wavexis) browser automation library and exposes it as an [MCP server](https://modelcontextprotocol.io/). You don't need Node.js, Playwright, or a separate Chromium download — WaveXisMCP launches your existing Chrome or Edge installation directly.

### Core concepts

- **Tool** — A single browser operation (screenshot, eval, click, etc.) exposed as an MCP tool that any LLM client can call.
- **Session** — A persistent browser instance. Open a session, chain multiple tool calls, close when done. Avoids the overhead of launching a browser per action.
- **Stateless mode** — Call any tool with a `url` parameter. The browser launches, executes, and closes automatically.
- **Capability tiers** — 13 tiers from `core` (49 tools) to `all` (158 tools). Enable only what you need via `--caps`.
- **Dual backend** — CDP (Chromium-native, via cdpwave) and BiDi (W3C cross-browser, via bidiwave) with per-session selection.

## Install

```bash
pip install wavexis-mcp
```

With CDP backend (Chromium):

```bash
pip install "wavexis-mcp[cdp]"
```

Or run without installing (recommended):

```bash
uvx wavexis-mcp
```

## Quick start

Add to your MCP client config (Claude Desktop, Cursor, Windsurf, VS Code):

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

Or with pip:

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

### Stateless mode (one-shot)

Call any tool with a `url` parameter — the browser launches, executes, and closes automatically:

```text
wavexis_screenshot(url="https://example.com", full_page=true)
```

### Session mode (multi-step)

Open a session, chain multiple actions, close when done:

```text
wavexis_session_open(backend="cdp", headless=false)
→ {"session_id": "abc-123"}

wavexis_navigate(session_id="abc-123", url="https://example.com")
wavexis_click(session_id="abc-123", selector="#login")
wavexis_screenshot(session_id="abc-123")
wavexis_session_close(session_id="abc-123")
```

### Natural language interaction (M1)

Use `wavexis_act` to interact with pages using natural language:

```text
wavexis_session_open(backend="cdp")
wavexis_navigate(session_id="abc-123", url="https://example.com")
wavexis_act(session_id="abc-123", instruction="click the login button")
→ {"action": "click", "element": {"ref": "el-3", "role": "button", "name": "Login"}, "status": "ok"}
```

The `wavexis_act` tool takes an a11y snapshot, matches the instruction to an element using keyword scoring, and executes the detected action (click, type, fill, hover). No external LLM calls — pure heuristic matching.

## Capability tiers

| Tier | Flag | Tools | Key features |
|------|------|-------|--------------|
| **Core** | always on | 42 | Session, navigation, screenshot, PDF, scrape, eval, DOM, input, cookies, tabs |
| **Network** | `--caps=network` | 9 | Headers, UA, block, throttle, cache, HAR, intercept, mock, request list |
| **Storage** | `--caps=storage` | 13 | localStorage, sessionStorage, cache storage, IndexedDB, state save/restore |
| **Emulation** | `--caps=emulation` | 9 | Device, viewport, geolocation, timezone, dark mode, locale, CPU, touch, sensors |
| **A11y** | `--caps=a11y` | 3 | Accessibility tree snapshot (LLM-friendly element refs) |
| **Interactions** | `--caps=interactions` | 5 | Dialogs, downloads, permissions |
| **DevTools** | `--caps=devtools` | 23 | Performance, CSS, debugging, overlay, console, security, window mgmt |
| **Vision** | `--caps=vision` | 6 | Coordinate-based mouse (pixel-precise) |
| **Video** | `--caps=video` | 4 | Video recording, chapters, action overlay |
| **Testing** | `--caps=testing` | 4 | Assertions, locator generation |
| **Workflows** | `--caps=workflows` | 5 | Multi-action YAML, raw CDP/BiDi, browser contexts |
| **Data** | `--caps=data` | 6 | Codegen, Lighthouse audit, extract, websocket intercept, crawl, visual diff |
| **Experimental** | `--caps=experimental` | 20 | Service workers, animations, WebAuthn, WebAudio, media, cast, bluetooth |
| **Total** | `--caps=all` | **158** | |

**Default**: `--caps=core` (49 tools). Enable all: `--caps=all`. Enable specific: `--caps=network,storage,emulation`.

## Backends

WaveXisMCP supports two backends with full feature parity:

- **CDP** (cdpwave) — default, Chrome DevTools Protocol. Direct WebSocket to Chrome/Edge. No driver needed. 57 CDP domains. `pip install "wavexis-mcp[cdp]"`
- **BiDi** (bidiwave) — WebDriver BiDi protocol, W3C cross-browser (Firefox, Chrome). Needs ChromeDriver/EdgeDriver. `pip install "wavexis-mcp[bidi]"`

Select per session:

```text
wavexis_session_open(backend="bidi")
```

## Multi-action YAML

Chain multiple actions in a single tool call:

```yaml
# workflow.yaml
actions:
  - navigate: https://example.com
  - screenshot:
      full_page: true
  - eval: document.title
  - click: "#login"
  - type:
      selector: "#username"
      text: admin@example.com
  - screenshot: {}
```

```text
wavexis_multi_action(config="@workflow.yaml", session_id="abc-123")
```

Supported action types: `navigate`, `screenshot`, `eval`, `click`, `type`, `fill`. Set `continue_on_error: true` to keep executing on failures.

## MCP resources & prompts (M3)

**Resources** (read-only browser state):

- `wavexis://session/{id}/url` — current page URL
- `wavexis://session/{id}/cookies` — cookies as JSON
- `wavexis://session/{id}/console` — console messages
- `wavexis://session/{id}/tabs` — open tabs

**Prompts** (workflow templates):

- `scrape_page(url, selector)` — scrape and extract content
- `audit_page(url)` — full a11y + performance audit
- `fill_form(url, fields)` — fill a form on a page
- `debug_page(url)` — debug console, network, performance

## HTTP transport

Run WaveXisMCP as an HTTP server for CI/CD, shared instances, or Docker:

```bash
# HTTP on localhost
wavexis-mcp --transport http --port 8765

# HTTP with all tiers
wavexis-mcp --transport http --port 8765 --caps all

# HTTP with remote access (use behind a reverse proxy!)
wavexis-mcp --transport http --allow-remote --port 8765
```

Binds to `127.0.0.1` by default. Use `--allow-remote` for `0.0.0.0`.

## Rate limiting (M4)

Per-session token bucket rate limiting:

```bash
# 10 calls/sec, burst of 5
wavexis-mcp --rate-limit 10 --rate-burst 5
```

When exceeded, returns `{"error": "rate_limited", "retry_after_ms": N}`.

## Docker

```bash
# Pull and run
docker run -p 8765:8765 ghcr.io/mathiaspaulenko/wavexis-mcp

# Or build locally
docker build -t wavexis-mcp .
docker run -p 8765:8765 wavexis-mcp

# Docker Compose
docker-compose up
```

See [Docker docs](https://mathiaspaulenko.github.io/wavexis-mcp/docker/) for details.

## Ecosystem

```text
WaveXisMCP (MCP server, 158 tools)
└─ wraps → wavexis (browser automation library)
               ├─ cdpwave (CDP backend, Chromium-native)
               └─ bidiwave (BiDi backend, W3C cross-browser)
```

## Comparison

| Feature | Playwright MCP | **WaveXisMCP** |
|---------|---------------|----------------|
| Language | TypeScript | **Python** |
| Node.js required | Yes | **No** |
| Downloads Chromium | Yes (~200MB) | **No (uses existing Chrome/Edge)** |
| Install size | ~200MB+ | **~5MB** |
| Total tools | ~70 | **158** |
| Capability tiers | Yes (`--caps`) | **Yes (13 tiers)** |
| Dual protocol | No | **CDP + BiDi** |
| Backend selection | No | **Yes (per session)** |
| Raw CDP/BiDi access | No | **Yes (escape hatch)** |
| Multi-action YAML | No | **Yes** |
| Video recording | No | **Yes** |
| Lighthouse audit | No | **Yes** |
| WebAuthn/Bluetooth | No | **Yes** |
| Natural language interaction | No | **Yes (`wavexis_act`)** |
| MCP resources & prompts | No | **Yes** |
| Rate limiting | No | **Yes** |

## Documentation

Full docs at [mathiaspaulenko.github.io/wavexis-mcp](https://mathiaspaulenko.github.io/wavexis-mcp/).

## Development

```bash
git clone https://github.com/MathiasPaulenko/wavexis-mcp.git
cd wavexis-mcp
pip install -e ".[dev]"
ruff check .
mypy wavexis_mcp/
pytest tests/ -v
```

## License

MIT