# Architecture

This document describes the system design, data flow, and key architectural decisions behind WaveXisMCP.

## System overview

```text
┌─────────────────────────────────────────────────────────┐
│                    LLM Client                            │
│  (Claude Desktop, Cursor, Windsurf, VS Code)            │
└──────────────────────┬──────────────────────────────────┘
                       │ MCP protocol (stdio / HTTP+SSE)
                       ▼
┌─────────────────────────────────────────────────────────┐
│                  WaveXisMCP Server                       │
│                                                         │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │  FastMCP    │  │  Pydantic v2 │  │  Capability   │  │
│  │  Server     │  │  Validation  │  │  Tier Filter  │  │
│  └──────┬──────┘  └──────┬───────┘  └───────┬───────┘  │
│         │                │                  │          │
│  ┌──────▼────────────────▼──────────────────▼───────┐  │
│  │              Tool Functions                      │  │
│  │  (163 @mcp.tool async functions across 13 mods)  │  │
│  └──────────────────────┬───────────────────────────┘  │
│                         │                              │
│  ┌──────────────────────▼───────────────────────────┐  │
│  │           Session Manager                        │  │
│  │  (persistent browser sessions, backend acquire)  │  │
│  └──────────────────────┬───────────────────────────┘  │
└─────────────────────────┼───────────────────────────────┘
                          │ Python async calls
                          ▼
┌─────────────────────────────────────────────────────────┐
│                   wavexis Library                        │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │            AbstractBackend                       │   │
│  │  (unified interface: navigate, click, eval, ...) │   │
│  └──────────┬──────────────────────┬────────────────┘   │
│             │                      │                    │
│  ┌──────────▼─────────┐  ┌────────▼─────────────┐      │
│  │   CDP Backend      │  │   BiDi Backend       │      │
│  │   (cdpwave)        │  │   (bidiwave)         │      │
│  │   WebSocket →      │  │   WebDriver →        │      │
│  │   Chrome/Edge      │  │   Chrome/Firefox     │      │
│  └────────────────────┘  └──────────────────────┘      │
└─────────────────────────────────────────────────────────┘
```

## Layers

### Layer 1: LLM Client

The LLM client (Claude Desktop, Cursor, Windsurf, VS Code) speaks the [Model Context Protocol](https://modelcontextprotocol.io/). It discovers WaveXisMCP's tools via the MCP `tools/list` method and calls them via `tools/call`. The client manages the LLM conversation and decides which tools to call based on the user's natural language request.

### Layer 2: WaveXisMCP Server

The MCP server layer. Built on [FastMCP](https://github.com/jlowin/fastmcp) (Python MCP SDK). Responsibilities:

- **Tool registration** — Each tool is an `async` function decorated with `@mcp.tool`. The function's docstring becomes the tool description visible to the LLM. Parameters are typed with Pydantic v2 models.
- **Input validation** — Pydantic v2 models validate every tool call. Invalid parameters return a structured error before the browser is touched.
- **Capability tier filtering** — The `--caps` flag controls which tool modules are registered. If a tier is disabled, its tools don't exist — they're not even visible to the LLM.
- **Session management** — `SessionManager` maintains a dict of `session_id → BrowserSession`. Each session holds a wavexis backend instance (CDP or BiDi) and metadata (created_at, backend type, headless flag).
- **Response formatting** — All tools return JSON strings. Binary outputs (screenshots, PDFs, videos) are base64-encoded or written to `output_path`. Errors include a `suggestion` field.
- **Rate limiting** — Per-session token bucket. Each tool call consumes one token. Tokens refill at `--rate-limit` per second up to `--rate-burst` capacity.

### Layer 3: wavexis Library

The browser automation library. Provides a unified `AbstractBackend` interface with ~80 async methods covering all browser capabilities. Two concrete implementations:

- **CDPBackend** (cdpwave) — Connects to Chrome/Edge via Chrome DevTools Protocol over WebSocket. No driver binary needed. Covers 57 CDP domains. Default backend.
- **BiDiBackend** (bidiwave) — Connects via WebDriver BiDi protocol. W3C standard, works with Firefox, Chrome, and Edge. Requires ChromeDriver/EdgeDriver.

### Layer 4: Browser

The actual browser process (Chrome, Edge, Brave, Chromium, Firefox). Launched by wavexis with `--remote-debugging-port` (CDP) or via WebDriver (BiDi). WaveXisMCP uses your existing browser installation — no bundled Chromium.

## Data flow

### Stateless tool call

```text
LLM calls wavexis_screenshot(url="https://example.com")
  → FastMCP receives tool call
    → Pydantic validates input (url: str, full_page: bool, ...)
    → Tool function runs:
      1. SessionManager creates ephemeral session (backend=cdp, headless=true)
      2. backend.navigate(url="https://example.com")
      3. backend.screenshot(full_page=true) → bytes
      4. SessionManager closes ephemeral session (kills browser)
      5. bytes → base64 → JSON response
    → JSON returned to LLM
```

### Session-based tool call

```text
LLM calls wavexis_navigate(session_id="abc-123", url="https://example.com")
  → FastMCP receives tool call
    → Pydantic validates input
    → Tool function runs:
      1. SessionManager.get("abc-123") → BrowserSession
      2. session.backend.navigate(url="https://example.com")
      3. → JSON response
    → JSON returned to LLM
  (browser stays open for next call)
```

### Error flow

```text
LLM calls wavexis_navigate(session_id="nonexistent")
  → FastMCP receives tool call
    → Pydantic validates input (valid string, but session doesn't exist)
    → Tool function runs:
      1. SessionManager.get("nonexistent") → raises SessionNotFoundError
      2. Exception caught by try/except
      3. format_error("wavexis_navigate", e) → JSON with suggestion
    → Error JSON returned to LLM
  LLM reads suggestion: "Call wavexis_session_open first to create a browser session."
  LLM calls wavexis_session_open(...)
```

## Package structure

```text
wavexis_mcp/
├── __init__.py          # Package metadata
├── server.py            # FastMCP server, CLI parsing, tool registration
├── session.py           # SessionManager, BrowserSession
├── caps.py              # Capability tier definitions and filtering
├── models.py            # Pydantic v2 input models for all tools
├── formatter.py         # JSON response formatting (format_json_response, format_error)
├── convenience.py       # wavexis_act (natural language interaction)
├── errors.py            # Custom exception types with suggestions
├── act.py               # Heuristic element matching for wavexis_act
└── tools/
    ├── __init__.py      # Tool registration entry point
    ├── session.py       # Session management tools (5)
    ├── navigation.py    # Navigation tools (6)
    ├── capture.py       # Screenshot, PDF, scrape, screencast (5)
    ├── javascript.py    # JavaScript evaluation (1)
    ├── dom.py           # DOM manipulation (12)
    ├── input.py         # User input (12)
    ├── cookies.py       # Cookie management (4)
    ├── tabs.py          # Tab management (4)
    ├── utility.py       # Browser info (2)
    ├── network.py       # Network control (9)
    ├── storage.py       # Storage access (13)
    ├── emulation.py     # Device/environment emulation (9)
    ├── a11y.py          # Accessibility tree (3)
    ├── interactions.py  # Dialogs, downloads, permissions (5)
    ├── devtools.py      # DevTools protocol (23)
    ├── vision.py        # Coordinate-based mouse (6)
    ├── video.py         # Video recording (4)
    ├── testing.py       # Assertions, locators (4)
    ├── workflows.py     # Multi-action, raw CDP/BiDi (5)
    ├── data.py          # Codegen, Lighthouse, crawl (6)
    └── experimental.py  # SW, animations, WebAuthn, etc. (20)
```

## Key design decisions

### ADR-1: Pydantic v2 for input validation

All tool inputs are Pydantic v2 `BaseModel` subclasses. This gives us:

- **Type safety** — Parameters are validated before the browser is touched
- **LLM discoverability** — The MCP `tools/list` response includes full JSON Schema for each tool, derived from the Pydantic model
- **Documentation** — Field descriptions in the model become parameter descriptions in the tool schema

### ADR-2: JSON string responses

All tools return `str` (JSON-encoded), not raw Python objects. This ensures:

- **Transport agnostic** — Works over stdio (text) and HTTP (text)
- **LLM-friendly** — The LLM receives structured data it can parse and reason about
- **Consistent error format** — Errors and successes have the same shape

### ADR-3: Capability tier filtering at registration time

Tiers are filtered at tool registration time, not at call time. If `--caps=core` is set, non-core tool functions are never registered with FastMCP. This means:

- **Smaller tool list** — The LLM sees fewer tools, reducing context window usage
- **No runtime overhead** — No per-call tier check
- **Clean errors** — Calling a non-registered tool returns a standard MCP error

### ADR-4: Dual backend with per-session selection

Each session selects its backend at creation time (`wavexis_session_open(backend="cdp")` or `backend="bidi")`). This allows:

- **Mixed usage** — Run CDP and BiDi sessions simultaneously
- **Graceful fallback** — If BiDi driver isn't available, CDP sessions still work
- **Feature parity** — Both backends implement the same `AbstractBackend` interface

### ADR-5: Stateless mode via ephemeral sessions

Stateless tool calls (with `url=` parameter) create an ephemeral session internally, execute the action, and clean up. This avoids requiring the LLM to manage session lifecycle for simple one-shot tasks while reusing the same code path as session-based calls.

### ADR-6: Structured errors with suggestions

Every error response includes a `suggestion` field that tells the LLM what to do next. For example, if a session doesn't exist, the suggestion says "Call wavexis_session_open first." This dramatically improves the LLM's ability to self-correct without human intervention.

### ADR-7: Token bucket rate limiting per session

Rate limiting uses a token bucket algorithm scoped per session. This prevents a runaway LLM from overwhelming the browser with rapid tool calls while allowing legitimate burst traffic. Each session has its own independent bucket.

## Transports

### stdio (primary)

```text
LLM Client ←→ stdin/stdout ←→ WaveXisMCP
```

The LLM client launches WaveXisMCP as a subprocess. Communication happens over stdin (requests) and stdout (responses). This is the standard MCP transport and works with all MCP clients. No network port needed.

### HTTP + SSE (secondary)

```text
LLM Client ←→ HTTP POST + SSE ←→ WaveXisMCP (port 8765)
```

WaveXisMCP runs as an HTTP server. Tool calls are sent as HTTP POST requests, and responses are streamed via Server-Sent Events. Used for CI/CD pipelines, shared instances, and Docker deployment.

See [HTTP Transport](http-transport.md) for configuration details.

## Binary outputs

Tools that produce binary data (screenshots, PDFs, videos) support two output modes:

- **base64** (default) — Binary data is base64-encoded and included in the JSON response. The LLM can display it directly.
- **file** — Binary data is written to `output_path` on disk. The JSON response contains the file path. Useful for large outputs or when the LLM client supports file references.

```text
# base64 (default)
wavexis_screenshot(session_id="abc-123")
→ {"data": "iVBORw0KGgo...", "format": "png", "encoding": "base64"}

# file
wavexis_screenshot(session_id="abc-123", output_path="./shot.png")
→ {"path": "./shot.png", "format": "png", "encoding": "file"}
```
