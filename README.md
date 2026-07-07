<p align="center">
  <img src="docs/assets/images/logo-wide.svg" alt="WaveXisMCP" width="400">
</p>

MCP server that exposes the [wavexis](https://github.com/MathiasPaulenko/wavexis) browser automation library to LLMs. **149 tools** across **13 capability tiers**. 100% Python, no Node.js, no Chromium download — uses your existing Chrome/Edge.

## Why WaveXisMCP?

- **Zero install** — uses your local Chrome/Edge, no 200MB Chromium download (~5MB package)
- **149 tools** — the most comprehensive browser automation MCP (vs ~70 for Playwright MCP)
- **Dual backend** — CDP (Chromium-native) + BiDi (W3C cross-browser) with per-session selection
- **13 capability tiers** — enable only what you need via `--caps`
- **Python-native** — no Node.js runtime required
- **Dual mode** — stateless one-shot calls or persistent sessions
- **Structured errors** — every error includes an actionable suggestion

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

## Quick Start

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

## Capability Tiers

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
| **Total** | `--caps=all` | **149** | |

**Default**: `--caps=core` (42 tools). Enable all: `--caps=all`. Enable specific: `--caps=network,storage,emulation`.

## vs Playwright MCP

| Feature | Playwright MCP | **WaveXisMCP** |
|---------|---------------|----------------|
| Language | TypeScript | **Python** |
| Node.js required | Yes | **No** |
| Downloads Chromium | Yes (~200MB) | **No (uses existing Chrome/Edge)** |
| Install size | ~200MB+ | **~5MB** |
| Total tools | ~70 | **149** |
| Capability tiers | Yes (`--caps`) | **Yes (13 tiers)** |
| Dual protocol | No | **CDP + BiDi** |
| Backend selection | No | **Yes (per session)** |
| Raw CDP/BiDi access | No | **Yes (escape hatch)** |
| Multi-action YAML | No | **Yes** |
| Video recording | No | **Yes** |
| Lighthouse audit | No | **Yes** |
| WebAuthn/Bluetooth | No | **Yes** |

## Configuration

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

### Backend selection

- **CDP** (default): Direct WebSocket to Chrome/Edge. No driver needed. 57 CDP domains.
- **BiDi**: W3C standard. Cross-browser (Firefox, Chrome). Needs ChromeDriver/EdgeDriver.

```bash
pip install "wavexis-mcp[cdp]"   # CDP backend (Chromium)
pip install "wavexis-mcp[bidi]"  # BiDi backend (cross-browser)
```

## Ecosystem

```text
WaveXisMCP (MCP server, 149 tools)
└─ wraps → wavexis (browser automation library)
               ├─ cdpwave (CDP backend, Chromium-native)
               └─ bidiwave (BiDi backend, W3C cross-browser)
```

## Documentation

- [Architecture](https://github.com/MathiasPaulenko/wavexis-mcp/blob/main/docs/index.md)
- [Quick Start](https://github.com/MathiasPaulenko/wavexis-mcp/blob/main/docs/quickstart.md)
- [Configuration](https://github.com/MathiasPaulenko/wavexis-mcp/blob/main/docs/configuration.md)
- [HTTP Transport](https://github.com/MathiasPaulenko/wavexis-mcp/blob/main/docs/http-transport.md)
- [Docker Deployment](https://github.com/MathiasPaulenko/wavexis-mcp/blob/main/docs/docker.md)
- [Resources & Prompts](https://github.com/MathiasPaulenko/wavexis-mcp/blob/main/docs/resources-prompts.md)
- [Rate Limiting](https://github.com/MathiasPaulenko/wavexis-mcp/blob/main/docs/rate-limiting.md)
- [Tool Reference](https://github.com/MathiasPaulenko/wavexis-mcp/blob/main/docs/tools/core.md)

## HTTP Transport (v0.2.0)

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

See [Docker docs](docs/docker.md) for details.

## Natural Language Interaction (M1)

Use `wavexis_act` to interact with pages using natural language:

```text
wavexis_session_open(backend="cdp")
→ {"session_id": "abc-123"}

wavexis_navigate(session_id="abc-123", url="https://example.com")

wavexis_act(session_id="abc-123", instruction="click the login button")
→ {"action": "click", "element": {"ref": "el-3", "role": "button", "name": "Login"}, "status": "ok"}
```

The `wavexis_act` tool takes an a11y snapshot, matches the instruction to an element using keyword scoring, and executes the detected action (click, type, fill, hover). No external LLM calls — pure heuristic matching.

## MCP Resources & Prompts (M3)

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

## Rate Limiting (M4)

Per-session token bucket rate limiting:

```bash
# 10 calls/sec, burst of 5
wavexis-mcp --rate-limit 10 --rate-burst 5
```

When exceeded, returns `{"error": "rate_limited", "retry_after_ms": N}`.

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

MIT © Mathias Paulenko