# Configuration

## Capability tiers

WaveXisMCP organizes 163 tools into 13 capability tiers. Core is always enabled. Additional tiers are opt-in via `--caps`.

| Tier | Flag | Tools | Key features |
| --- | --- | --- | --- |
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

## --caps flag

```bash
# Core only (default, 42 tools)
wavexis-mcp

# All tiers (163 tools)
wavexis-mcp --caps all

# Specific tiers
wavexis-mcp --caps network,storage,emulation

# Core + specific tiers
wavexis-mcp --caps core,devtools,a11y

# Equals syntax
wavexis-mcp --caps=devtools,a11y
```

Invalid tier names produce a warning on stderr and are skipped — the server does not crash.

## Session vs stateless mode

### Stateless (one-shot)

Call any tool with a `url` parameter. The browser launches, executes one action, and closes.

```python
wavexis_screenshot(url="https://example.com", full_page=true)
```

### Session-based (multi-step)

Open a session, chain multiple actions, close when done.

```python
wavexis_session_open(backend="cdp", headless=false)
# → {"session_id": "abc-123"}

wavexis_navigate(session_id="abc-123", url="https://example.com")
wavexis_click(session_id="abc-123", selector="#login")
wavexis_screenshot(session_id="abc-123")
wavexis_session_close(session_id="abc-123")
```

## Backend selection

- **CDP** (default): Direct WebSocket to Chrome/Edge. No driver needed. 57 CDP domains.
- **BiDi**: W3C standard. Cross-browser (Firefox, Chrome). Needs ChromeDriver/EdgeDriver.

```bash
pip install "wavexis-mcp[cdp]"   # CDP backend
pip install "wavexis-mcp[bidi]"  # BiDi backend
```

## Transport

- **stdio** (v1, primary): Standard MCP transport for local development. Uses your local Chrome/Edge.
- **HTTP** (v2, planned): For CI/CD, shared instances, Docker deployment.

## Error handling

All tools return structured error JSON on failure:

```json
{
  "error": "Session 'abc-123' not found.",
  "tool": "wavexis_navigate",
  "type": "SessionNotFoundError",
  "message": "Session 'abc-123' not found.",
  "suggestion": "Call wavexis_session_open first to create a browser session."
}
```

The `suggestion` field guides the LLM toward the next action.
