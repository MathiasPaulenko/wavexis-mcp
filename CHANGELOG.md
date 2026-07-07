# Changelog

All notable changes to WaveXisMCP will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.6.2] - 2025-07-07

### Added

- 13 new unit tests covering all tools added in v1.5.0–v1.6.1:
  - `test_browser_context_list` (workflows)
  - `test_modify_response` (network)
  - `test_animation_list`, `test_media_get_players`, `test_media_get_messages`, `test_cast_list`, `test_sw_update`, `test_webauthn_add_authenticator` (experimental)
  - `test_core_web_vitals` (data)
  - `test_find_by_text`, `test_find_by_text_all`, `test_nl_click`, `test_nl_fill` (input)

### Changed

- Test count: 321 → 334

## [1.6.1] - 2025-07-07

### Added

- 3 new optional NL interaction tools (172 → 175 total):
  - `wavexis_find_by_text` — find element(s) by visible text content (core tier)
  - `wavexis_nl_click` — click an element by natural language query (core tier)
  - `wavexis_nl_fill` — fill an element by natural language query (core tier)

### Changed

- Bumped tool count from 172 to 175 in pyproject.toml, README, and docs
- Updated core tier count: 42 → 45

## [1.6.0] - 2025-07-07

### Added

- 6 new useful tools bridging remaining backend methods (166 → 172 total):
  - `wavexis_animation_list` — list all active animations on the page (experimental tier)
  - `wavexis_media_get_players` — list all media players (experimental tier)
  - `wavexis_media_get_messages` — get messages for a specific media player (experimental tier)
  - `wavexis_cast_list` — list available cast sinks (experimental tier)
  - `wavexis_service_worker_update` — trigger an update for a service worker registration (experimental tier)
  - `wavexis_core_web_vitals` — measure Core Web Vitals (LCP, CLS, INP) with ratings and score (data tier)

### Changed

- Bumped tool count from 166 to 172 in pyproject.toml, README, and docs
- Updated tier counts: Experimental 21→26, Data 6→7

## [1.5.1] - 2025-07-07

### Fixed

- CI: ruff format check failing on `experimental.py` and `workflows.py`
- Release: Docker build failing with `lstat /dist: no such file or directory` (missing artifact download in docker job)

## [1.5.0] - 2025-07-07

### Added

- 3 new critical tools bridging missing backend methods (163 → 166 total):
  - `wavexis_browser_context_list` — list all browser contexts in a session (workflows tier)
  - `wavexis_modify_response` — intercept and modify HTTP responses in-flight (network tier)
  - `wavexis_webauthn_add_authenticator` — add a virtual WebAuthn authenticator for testing (experimental tier)

### Changed

- Bumped tool count from 163 to 166 in pyproject.toml, README, and docs
- Updated tier counts: Network 9→10, Workflows 5→6, Experimental 20→21

## [1.4.0] - 2025-07-07

### Added

- 5 new experimental/niche tools:
  - `wavexis_extension_install` — install a browser extension from .crx or unpacked directory
  - `wavexis_extension_uninstall` — uninstall a browser extension by ID
  - `wavexis_extension_list` — list installed browser extensions
  - `wavexis_get_pref` — get a browser preference value by key
  - `wavexis_set_pref` — set a browser preference value

### Changed

- Bumped tool count from 158 to 163 in project description and docs

## [1.3.0] - 2025-07-07

### Added

- 2 new event subscription tools (W10):
  - `wavexis_subscribe_events` — subscribe to real-time browser events (console, network, DOM mutations, dialogs, navigation)
  - `wavexis_unsubscribe_events` — unsubscribe by subscription ID

### Fixed

- CI: docs deploy concurrency conflict when tag and branch push happen simultaneously (`cancel-in-progress: true`)

### Changed

- Bumped tool count from 156 to 158 in project description and docs

## [1.2.0] - 2025-07-07

### Added

- 7 new tools bridging wavexis backend methods not yet exposed in MCP (149 → 156 total):
  - `wavexis_annotated_screenshot` — screenshot with numbered labels (@e1, @e2) overlaid on elements
  - `wavexis_iframe_eval` — evaluate JavaScript inside an iframe
  - `wavexis_iframe_click` — click an element inside an iframe
  - `wavexis_iframe_fill` — fill an input inside an iframe
  - `wavexis_shadow_eval` — evaluate JavaScript inside a shadow DOM tree
  - `wavexis_shadow_click` — click an element inside a shadow DOM tree
  - `wavexis_shadow_fill` — fill an input inside a shadow DOM tree

### Changed

- Bumped tool count from 149 to 156 in project description and README

## [1.1.0] - 2025-07-07

### Changed

- Project layout: moved from `src/wavexis_mcp/` to flat `wavexis_mcp/` (matches wavexis convention)
- CI: consolidated `release.yml` with Trusted Publishing (OIDC) — separate build/publish/docker/release jobs
- CI: `id-token: write` scoped to `publish-pypi` job only (least privilege)
- Docs: `mkdocs.yml` aligned with wavexis style — sidebar navigation (no top tabs), `navigation.indexes`, `navigation.expand`
- Docs: added `mkdocstrings` plugin for Python API auto-documentation
- Docs: added `pymdownx.details`, `pymdownx.inlinehilite`, `pymdownx.tasklist`, `tables` extensions
- Docker: consolidated into `release.yml` with semver tags, GHA cache, `docker/metadata-action`

### Added

- 56 new unit tests (261 → 321 total), coverage 81% → 87%
  - `test_streaming.py`: 8 tests for StreamingHandler (0% → 100%)
  - `test_javascript.py`: 6 tests for wavexis_eval (43% → 100%)
  - `test_server_cli.py`: 14 tests for CLI parsing, help, main, wavexis_act (57% → 89%)
  - `test_network.py`: +10 tests for W3/W6/W7 tools (62% → 83%)
  - `test_workflows.py`: +8 tests for multi_action, browser context (67% → 93%)
  - `test_resources.py`: +4 tests for error paths (84% → 100%)
  - `test_act.py`: +8 tests for execute_act edge cases (89% → 98%)

### Removed

- `docker.yml` workflow (consolidated into `release.yml`)

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
