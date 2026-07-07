# Configuration

WaveXisMCP organizes 163 tools into 13 capability tiers. Core is always enabled. Additional tiers are opt-in via `--caps`.

## Capability tiers

Capability tiers are the primary way to control which tools are exposed to the LLM. Each tier groups related tools by domain. This matters because LLMs have context windows — exposing 163 tool definitions consumes tokens. For simple tasks, 42 core tools is plenty. For complex automation, enable everything with `--caps all`.

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
| **Experimental** | `--caps=experimental` | 20 | Service workers, animations, WebAuthn, WebAudio, media, cast, bluetooth, extensions, prefs |
| **Total** | `--caps=all` | **163** | |

### Tier details

#### Core (42 tools, always on)

The foundation. Covers session management, navigation, screenshots, PDF generation, page scraping, JavaScript evaluation, DOM manipulation, user input (click, type, fill, hover, drag, key press), cookies, and tab management. These tools are always available regardless of `--caps` settings.

#### Network (9 tools)

Control over HTTP traffic. Set custom headers, override User-Agent, block requests by URL pattern, throttle network speed, disable cache, capture HAR files, intercept and modify requests in-flight, mock responses, and list all network requests made by the page. Essential for testing API interactions, simulating slow connections, and debugging network issues.

#### Storage (13 tools)

Read and write browser storage. Full localStorage and sessionStorage CRUD, Cache Storage listing and deletion, and storage state save/restore (exports cookies + all storage as JSON for later restoration). Useful for preserving authentication state between sessions or testing storage-dependent features.

#### Emulation (9 tools)

Simulate devices and environments. Emulate specific devices (iPhone 15, Pixel 8, etc.) with correct viewport, user agent, and touch events. Override geolocation, timezone, dark mode, locale, CPU throttling, and sensor values (accelerometer, gyroscope). Essential for responsive testing and geo-dependent features.

#### A11y (3 tools)

Accessibility tree inspection. Capture the full accessibility tree with LLM-friendly element references (e.g., `el-1`, `el-2`) that can be passed to other tools. Get specific nodes by ID and traverse ancestors. The foundation for `wavexis_act` (natural language interaction).

#### Interactions (5 tools)

Handle browser-level interactions that aren't DOM clicks. Accept/dismiss JavaScript dialogs (alert, confirm, prompt), intercept file downloads, grant browser permissions (geolocation, notifications, camera, microphone), and reset permissions. Essential for testing pages with popups or permission flows.

#### DevTools (23 tools)

Chrome DevTools protocol exposed as tools. Performance metrics (LCP, FCP, CLS, TTFB), CPU profiling, heap snapshots, JS/CSS coverage, CSS style inspection, JavaScript debugging (breakpoints, step over/into/out, pause/resume), event listener inspection, element highlighting, console capture, security state, and window bounds control. The most powerful tier for debugging and optimization.

#### Vision (6 tools)

Pixel-precise mouse control. Move, press, release, click, and double-click at specific x,y coordinates. Unlike DOM-based clicks (which use CSS selectors), vision tools operate on raw screen coordinates. Useful when elements don't have stable selectors or when interacting with canvas/WebGL.

#### Video (4 tools)

Browser video recording. Start/stop recording, add chapter markers at specific timestamps, and overlay action labels on the video. Recordings capture the full page including animations and interactions. Useful for bug reports, demos, and regression testing.

#### Testing (4 tools)

Assertion-based testing. Assert element visibility, text presence, and URL matching. Generate robust CSS selectors for elements (tries ID, data-testid, class, nth-child). These tools return pass/fail results as JSON, making them ideal for automated test pipelines.

#### Workflows (5 tools)

Advanced automation. Execute multi-action YAML sequences in a single tool call (navigate → wait → click → fill → screenshot). Send raw CDP or BiDi commands as an escape hatch for any browser feature not covered by a dedicated tool. Create and close isolated browser contexts for parallel sessions.

#### Data (6 tools)

Data extraction and analysis. Record browser actions to YAML (codegen for test generation), run Lighthouse audits (performance, accessibility, SEO, best-practices), extract structured data via CSS selectors, intercept WebSocket messages, crawl multiple URLs with depth control, and compare screenshots for visual regression testing.

#### Experimental (20 tools)

Niche and experimental features. Service worker management (list, unregister, update), animation control (list, pause, play, seek), WebAuthn virtual authenticators, WebAudio context inspection, media player monitoring, Cast (Chromecast) control, Bluetooth emulation, browser extension management (install, uninstall, list), and browser preference get/set. These tools cover edge cases that most users won't need but are invaluable when they do.

## --caps flag

```bash
# Core only (default, 42 tools)
wavexis-mcp

# All tiers (163 tools)
wavexis-mcp --caps all

# Specific tiers
wavexis-mcp --caps network,storage,emulation

# Core + specific tiers (core is always included)
wavexis-mcp --caps core,devtools,a11y

# Equals syntax
wavexis-mcp --caps=devtools,a11y
```

!!! tip "Choosing tiers"
    Start with `--caps core` and add tiers as needed. Each tier adds tool definitions to the LLM's context, which consumes tokens. For most tasks, `core,network,storage` (64 tools) is a good balance. Use `all` only when you need maximum capability.

## CLI flags

| Flag | Default | Description |
|------|---------|-------------|
| `--transport` | `stdio` | Transport mode: `stdio` (for LLM clients) or `http` (for CI/CD, Docker) |
| `--host` | `127.0.0.1` | HTTP bind host (only used with `--transport http`) |
| `--port` | `8765` | HTTP listen port (only used with `--transport http`) |
| `--allow-remote` | `false` | Bind HTTP to `0.0.0.0` (enables remote access — use behind a reverse proxy!) |
| `--caps` | `core` | Comma-separated capability tiers to enable |
| `--rate-limit` | `60` | Max tool calls per second per session (token bucket) |
| `--rate-burst` | `10` | Max burst size for rate limiting |
| `--help` | — | Show help and exit |

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `WAVEXIS_BROWSER_PATH` | auto-detect | Path to Chrome/Edge binary. If not set, WaveXisMCP auto-detects Chrome then Edge. |
| `WAVEXIS_BACKEND` | `cdp` | Default backend: `cdp` or `bidi`. Can be overridden per session. |

### Browser auto-detection

WaveXisMCP searches for Chrome/Edge in standard install locations:

- **Windows**: `C:\Program Files\Google\Chrome\Application\chrome.exe`, `C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe`
- **macOS**: `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`, `/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge`
- **Linux**: `/usr/bin/google-chrome`, `/usr/bin/chromium`, `/usr/bin/microsoft-edge`

If your browser is in a non-standard location, set `WAVEXIS_BROWSER_PATH`:

```bash
export WAVEXIS_BROWSER_PATH=/opt/chrome/chrome
wavexis-mcp --caps all
```

## Transport modes

### stdio (default)

Used by LLM clients (Claude Desktop, Cursor, Windsurf, VS Code). The client launches WaveXisMCP as a subprocess and communicates over stdin/stdout. No network port needed.

```bash
wavexis-mcp --caps all
```

### HTTP

Used for CI/CD pipelines, shared instances, and Docker deployment. Runs as an HTTP server with SSE (Server-Sent Events) transport.

```bash
wavexis-mcp --transport http --port 8765 --caps all
```

See [HTTP Transport](http-transport.md) for details.
