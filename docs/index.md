# WaveXisMCP

MCP server that exposes the [wavexis](https://github.com/MathiasPaulenko/wavexis) browser automation library to LLMs.

**149 tools** across **13 capability tiers**. 100% Python, no Node.js, no Chromium download — uses your existing Chrome/Edge.

## Key features

- **Zero install** — uses your local Chrome/Edge, no 200MB Chromium download (~5MB package)
- **149 tools** — the most comprehensive browser automation MCP
- **Dual backend** — CDP (Chromium-native) + BiDi (W3C cross-browser) with per-session selection
- **13 capability tiers** — enable only what you need via `--caps`
- **Python-native** — no Node.js runtime required
- **Dual mode** — stateless one-shot calls or persistent sessions
- **Structured errors** — every error includes an actionable suggestion

## Quick links

- [Quick Start](quickstart.md)
- [Configuration](configuration.md)
- [Tool Reference](tools/core.md)
- [Examples](examples/screenshot.md)

## Ecosystem

```text
WaveXisMCP (MCP server, 149 tools)
└─ wraps → wavexis (browser automation library)
               ├─ cdpwave (CDP backend, Chromium-native)
               └─ bidiwave (BiDi backend, W3C cross-browser)
```

## License

MIT © Mathias Paulenko
