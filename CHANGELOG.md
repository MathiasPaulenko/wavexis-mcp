# Changelog

All notable changes to WaveXisMCP will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2025-07-07

### Fixed

- CI: `gpg --dearmor` failing in GitHub Actions (added `--batch --yes` flags)
- Release: missing `contents: write` permission for GitHub Release creation
- Docs: missing `pymdown-extensions` dependency for mkdocs build
- Test: `test_visual_diff_not_implemented` now handles both `not_implemented` and error responses

### Added

- Docs workflow for GitHub Pages deployment

## [1.0.0] - 2025-07-07

### Added

- **149 tools** across **13 capability tiers**:
  - Core (42): session, navigation, capture, eval, DOM, input, cookies, tabs, utility
  - Network (9): headers, UA, block, throttle, cache, HAR, intercept, mock, request list
  - Storage (13): localStorage, sessionStorage, cache storage, IndexedDB, state save/restore
  - Emulation (9): device, viewport, geolocation, timezone, dark mode, locale, CPU, touch, sensors
  - A11y (3): accessibility tree snapshot, node by ID, ancestors
  - Interactions (5): dialogs, downloads, permissions
  - DevTools (23): performance, CSS, debugging, overlay, console, security, window management
  - Vision (6): coordinate-based mouse operations
  - Video (4): recording, chapters, action overlay
  - Testing (4): assertions, locator generation
  - Workflows (5): multi-action YAML, raw CDP/BiDi, browser contexts
  - Data (6): codegen, lighthouse audit, extract, websocket intercept, crawl, visual diff
  - Experimental (20): service workers, animations, WebAuthn, WebAudio, media, cast, bluetooth
- **M1: `wavexis_act` tool** — natural language interaction with accessibility snapshot matching and action execution (click, type, fill, hover) via heuristic keyword scoring
- **M2: WebSocket event streaming** — live browser event streaming for HTTP transport with polling fallback (`streaming.py`)
- **M3: MCP resources** — read-only browser state exposed via `wavexis://session/{id}/url`, `/cookies`, `/console`, `/tabs`
- **M3: MCP prompts** — workflow templates: `scrape_page`, `audit_page`, `fill_form`, `debug_page`
- **M4: Per-session rate limiting** — token bucket algorithm with `--rate-limit` and `--rate-burst` CLI flags
- **HTTP transport** — `--transport http` mode with `--host`, `--port`, and `--allow-remote` flags
- **Docker deployment** — Dockerfile, docker-compose.yml, and GitHub Actions workflow for GHCR image publishing
- **W3: `wavexis_get_request_body`, `wavexis_get_response_body`** — request/response body capture
- **W6: `wavexis_modify_request`** — request modification (headers, method, body)
- **W7: `wavexis_replay_har`** — HAR file replay
- **W8: `wavexis_start_combined_trace`, `wavexis_stop_combined_trace`** — combined trace + performance
- **W9: `wavexis_axe_audit`** — axe-core accessibility audit
- **W12: `wavexis_visual_diff`** — visual regression diffing
- Dual backend support: CDP (cdpwave, Chromium-native) + BiDi (bidiwave, W3C cross-browser)
- Dual mode: stateless (one-shot) + session-based (persistent browser)
- Capability tier filtering via `--caps` flag
- Structured error responses with actionable suggestions
- Session cleanup via lifespan handler and atexit
- `--help` CLI support with argparse
- Pydantic v2 input validation for all tools
- Base64 and file output for binary data (screenshots, PDFs, video)
- Comprehensive unit + integration test suite (261 tests)
- MIT license
- Documentation: HTTP transport, Docker, resources/prompts, rate limiting

### Security

- HTTP transport binds to `127.0.0.1` by default (not `0.0.0.0`)
- `--allow-remote` flag required for `0.0.0.0` binding (prints warning)
- No authentication in HTTP transport for v1.0.0 (planned for v1.1.0)
- Rate limiting protects browser from excessive tool calls per session
- Capability gating for destructive/experimental tools
- No arbitrary command execution (raw CDP/BiDi sends protocol commands, not shell)
