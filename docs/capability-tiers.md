# Capability Tiers

WaveXisMCP organizes its 220 tools into 13 capability tiers. You enable only what you need with the `--caps` flag, keeping startup fast and the tool list manageable for the LLM.

## How tiers work

```bash
# All 220 tools (default)
uvx wavexis-mcp --caps all

# Only core tools (38 tools — minimal footprint)
uvx wavexis-mcp --caps core

# Comma-separated combination
uvx wavexis-mcp --caps core,network,storage,a11y
```

The `core` tier is **always enabled** — it provides the essential session, navigation, DOM, and screenshot tools. All other tiers are opt-in.

## Tier reference

| Tier | Tools | Description |
| --- | --- | --- |
| `core` | 38 | Session, navigation, screenshots, DOM, JavaScript, tabs, cookies, utility |
| `network` | 12 | Request interception, HAR recording, response mocking |
| `storage` | 10 | localStorage, sessionStorage, IndexedDB, cache management |
| `emulation` | 8 | Device emulation, geolocation, timezone, viewport |
| `a11y` | 4 | Accessibility tree, axe-core audits, ARIA node queries |
| `interactions` | 5 | Dialogs, permissions, download interception |
| `devtools` | 14 | Console, performance metrics, CPU throttling, raw CDP |
| `vision` | 7 | Lighthouse, WebAuthn, Bluetooth, Cast |
| `video` | 4 | Video recording, playback capture |
| `testing` | 5 | Visual regression, element screenshots, test helpers |
| `workflows` | 6 | Multi-action YAML batching, natural language interaction |
| `data` | 8 | Tables, forms, metadata, OpenGraph extraction |
| `experimental` | 10 | Raw protocol access, CDP/BiDi escape hatch |

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
