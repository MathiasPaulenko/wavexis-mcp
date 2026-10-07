# Capability Tiers

WaveXisMCP organizes its 220 tools into 13 capability tiers. You enable only what you need with the `--caps` flag, keeping startup fast and the tool list manageable for the LLM.

## How tiers work

```bash
# All 220 tools
uvx wavexis-mcp --caps all

# Only core tools (72 tools — minimal footprint)
uvx wavexis-mcp --caps core

# Comma-separated combination
uvx wavexis-mcp --caps core,network,storage,a11y
```

The `core` tier is **always enabled** — it provides the essential session, navigation, DOM, and screenshot tools. All other tiers are opt-in.

## Tier reference

| Tier | Tools | Description |
| --- | --- | --- |
| `core` | 72 | Session, navigation, screenshots, PDF, scrape, eval, DOM, input, cookies, tabs, iframe, shadow DOM, events, natural language interaction |
| `network` | 20 | Headers, UA, request blocking, throttling, cache, HAR, intercept, mock, modify request/response, request body, replay HAR, request list |
| `storage` | 18 | localStorage, sessionStorage, cache storage, IndexedDB, state save/restore |
| `emulation` | 9 | Device, viewport, geolocation, timezone, dark mode, locale, CPU, touch, sensors |
| `a11y` | 4 | Accessibility tree snapshot, node traversal, axe-core audit |
| `interactions` | 5 | Dialogs, downloads, permissions |
| `devtools` | 31 | Performance, CSS, debugging, overlay, console, security, window management, combined trace, annotated screenshot |
| `vision` | 7 | Coordinate-based mouse (pixel-precise move/click/drag/wheel) |
| `video` | 4 | Screencast recording (MJPEG frames), chapters, action overlay |
| `testing` | 6 | Assertions, locator generation |
| `workflows` | 6 | Multi-action YAML, raw CDP/BiDi, browser context CRUD |
| `data` | 7 | Codegen record, Lighthouse-style audit, extract, WebSocket capture, crawl, visual diff, Core Web Vitals |
| `experimental` | 31 | Service workers, animations, WebAuthn, WebAudio, media, Cast, Bluetooth, extensions, prefs |
| **Total** | **220** | |

## Recommended combinations

### Scraping & data extraction

```bash
uvx wavexis-mcp --caps core,network,storage,data
```

### Testing & QA

```bash
uvx wavexis-mcp --caps core,a11y,testing,devtools
```

### Full automation

```bash
uvx wavexis-mcp --caps all
```

### Minimal (fastest startup)

```bash
uvx wavexis-mcp --caps core
```

## Tier details

Each tier has its own documentation page with all tools, parameters, and descriptions:

- [Core](tools/core.md)
- [Network](tools/network.md)
- [Storage](tools/storage.md)
- [Emulation](tools/emulation.md)
- [A11y](tools/a11y.md)
- [Interactions](tools/interactions.md)
- [DevTools](tools/devtools.md)
- [Vision](tools/vision.md)
- [Video](tools/video.md)
- [Testing](tools/testing.md)
- [Workflows](tools/workflows.md)
- [Data](tools/data.md)
- [Experimental](tools/experimental.md)
