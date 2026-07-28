# Changelog

All notable changes to WaveXisMCP will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.6.15] - 2026-07-28

### Changed

- CI no longer masks integration test failures with `continue-on-error: true`.
- Unit tests now enforce `--cov-fail-under=90` to prevent coverage regressions.
- Codecov upload now sets `fail_ci_if_error: true` to block PRs on coverage failures.
- Pre-commit config now includes `bandit` security scanning hook.

### Tests

- Added `tests/unit/test_convenience.py` with direct tests for `fill_form_composite` (all fields succeed, partial failure, empty list, all fail).
- Added `tests/unit/test_stabilization.py` with 12 tests covering error handling (session expired, launch failure, backend errors), concurrency (concurrent acquire/release, concurrent close), and edge cases (unicode expressions, empty URLs, extreme/zero viewports, extremely long URLs).

## [1.6.14] - 2026-07-28

### Security

- `SessionManager.open` and `acquire_backend` now validate `connect_endpoint` and `remote_url` WebSocket URLs via `validate_websocket_url`, rejecting non-`ws`/`wss` schemes, private IPs, localhost, and cloud metadata endpoints. Prevents SSRF and data exfiltration via attacker-controlled WebSocket endpoints.
- `format_error` now sanitizes error messages before logging and returning to clients, masking URLs with embedded credentials (`http://user:pass@host` → `http://***:***@host`) and key/value secret patterns (`token=`, `api_key=`, `authorization=`, `bearer`, `secret`, `password`).

### Added

- `validate_websocket_url` helper in `wavexis_mcp/formatter` with the same IP/scheme blocking logic as `validate_url`.

### Tests

- Added regression tests for WebSocket endpoint validation (internal IP rejection, scheme rejection, public WSS acceptance).
- Added regression tests for error message sanitization (credential URLs, token values, authorization headers, non-sensitive passthrough).

## [1.6.13] - 2026-07-27

### Fixed

- Reformatted `wavexis_mcp/tools/experimental.py` to satisfy `ruff format` in CI.

## [1.6.12] - 2026-07-27

### Fixed

- `wavexis_service_worker_emulate` now registers the service worker via an in-page JavaScript fallback, avoiding reliance on removed CDP `ServiceWorker` domain methods.
- `wavexis_media_player_play`, `wavexis_media_player_pause`, and `wavexis_media_player_seek` now control `<video>`/`<audio>` elements by element ID through JavaScript, replacing the unavailable CDP `Media.*Player` commands.

### Added

- `wavexis_capture_har` now accepts an optional `path` field in `CaptureHARInput` to persist the captured HAR JSON to a file under `WAVEXIS_MCP_OUTPUT_DIR`.

### Changed

- `.gitignore` now ignores `output/` and `scripts/test_*.py` scratch artifacts.

## [1.6.11] - 2025-07-27

### Fixed

- `wavexis_act` now falls back to an in-page JavaScript search by role and name when the CSS selector derived from the a11y tree fails, enabling reliable natural-language clicks, fills, and hovers against real pages.
- Tightened `wavexis_act` scoring to ignore action verbs and typed values, preventing generic instructions from matching unrelated headings or elements.

### Changed

- `format_json_response` normalises successful dict responses to include `status: "ok"` when no explicit `status` or `error` field is present.
- A11y snapshots now include `node_id` and `backend_node_id` and skip `InlineTextBox`/`LineBreak` nodes to reduce token bloat.

## [1.6.10] - 2025-07-27

### Fixed

- Fixed 25 ruff lint errors in E2E test files (E501 line-too-long, F401 unused imports, F841 unused variables, ASYNC240).
- Fixed `wavexis_multi_action` example in README to use inline YAML string instead of `@workflow.yaml` file path syntax.

## [1.6.9] - 2025-07-27

### Fixed

- Corrected `wavexis_scrape` examples to use `urls=` (list) instead of `url=` (string) in `docs/examples/scrape.md`.
- Fixed `wait_until=` → `wait_strategy=` in scrape and screenshot examples.
- Fixed `device="iPhone 15"` → `device="iphone-15"` (kebab-case preset) in screenshot example.
- Fixed `wavexis_assert_url` examples to use `url_pattern=` instead of `url=`; removed non-existent `match_type` parameter in `docs/examples/testing.md`.
- Removed non-existent `all=` parameter from `wavexis_generate_locator` example.
- Fixed `wavexis_multi_action` examples to use `config=` instead of `actions=` in `docs/examples/multi-action.md`.
- Fixed `wavexis_extract` parameter `schema` → `json_schema` and added missing `session_id` to `wavexis_record` in `docs/tools/data.md`.

### Added

- Documented `WAVEXIS_MCP_OUTPUT_DIR`, `WAVEXIS_MCP_ALLOW_INTERNAL_URLS`, and `WAVEXIS_MCP_ALLOW_RAW_COMMANDS` environment variables in `docs/configuration.md`.
- Added `WAVEXIS_MCP_OUTPUT_DIR` and `CI` env vars to Docker documentation table in `docs/docker.md`.

### Changed

- Updated Docker CI/CD tag example from `v1.4.0` to `v1.6.8` in `docs/docker.md`.

## [1.6.8] - 2025-07-27

### Added

- Full E2E test suite (118 tests) covering all 13 capability tiers against real Chrome browsers:
  - `test_e2e_core.py` — navigation, DOM, click, type, eval, screenshot, scrape, cookies, tabs.
  - `test_e2e_network_storage.py` — network monitoring, cookies, localStorage, sessionStorage, cache, IndexedDB.
  - `test_e2e_emulation_a11y.py` — device emulation, viewport, sensors, touch, accessibility tree, axe audit.
  - `test_e2e_devtools_vision.py` — performance traces, CSS, console, security, overlays, coordinate-based mouse, video.
  - `test_e2e_testing_workflows.py` — assertions, multi-action YAML, raw CDP, browser contexts, data extraction, act.
  - `test_e2e_full_server.py` — full workflow integration, multi-tab, stateless mode, error handling.
  - Local HTML fixture pages for all test scenarios.
- Regression tests for deep input nesting, a11y tree cycles, missing file uploads, oversized network patterns, and nested output directory creation.

### Fixed

- Corrected input parameter names across E2E tests (`url_pattern`, `json_schema`, `node_id` as str, `strategy`+`selector` for wait).
- Fixed assertion formats to match actual tool response keys (no `status` field where not returned).
- Set `WAVEXIS_MCP_ALLOW_RAW_COMMANDS=all` in E2E conftest for raw CDP tests.
- Made `wavexis_mcp/models.py` `_limit_input_size()` iterative to avoid `RecursionError` on deeply nested payloads.
- Added cycle detection and recursion guards to a11y tree formatting and counting in `wavexis_mcp/tools/a11y.py`.
- Offloaded `secure_output_path()`, parent directory creation, and file writes to a thread in `wavexis_mcp/formatter.py`.
- Ensured all blocking file-writing helpers create parent directories (`capture.py`, `devtools.py`, `interactions.py`, `storage.py`).
- Hardened `wavexis_mcp/tools/network.py` `_matches_pattern()` so safety-limit and timeout failures do not fall back to an unbounded `fnmatch`.
- Improved `wavexis_mcp/tools/input.py` file validation to report clear errors for missing or unreadable files.
- Added `min_length=1` constraints across models for text, query, cookie, URL pattern, storage key, and path fields.
- Fixed `wavexis_mcp/act.py` keyword extraction to support non-ASCII letters.
- Fixed `wavexis_mcp/server.py` `main()` to accept an optional `argv` parameter while preserving existing CLI help behavior.
- Added a 1000-session cap and improved error logging in `wavexis_mcp/session.py`.
- Added logging for crawler navigation failures in `wavexis_mcp/tools/data.py`.
- Reverted `pyproject.toml` mypy target from Python 3.12 back to 3.11 to match `requires-python`.
- Replaced `eval()` usage in `tests/unit/test_security.py` with a safer annotation lookup.

### Changed

- Added `bug_hunt_report.txt` to `.gitignore`.
- Cleaned up ~120 temporary log files and temp scripts from the repository root.

## [1.6.7] - 2025-07-25

### Changed

- Renamed `TimeoutError` to `OperationTimeoutError` in `wavexis_mcp/errors.py` to avoid shadowing the built-in `TimeoutError`; kept `TimeoutError` as a backwards-compatible alias.
- Replaced `print(..., file=sys.stderr)` warnings in `wavexis_mcp/caps.py` with `warnings.warn(..., stacklevel=2)`.
- Hardened `wavexis_mcp/tools/data.py` crawler against navigation failures with a dedicated `_try_navigate` helper.
- Switched `pyproject.toml` to dynamic versioning from `wavexis_mcp/__init__.py` and updated the release workflow to validate against `__init__.py` instead of `pyproject.toml`.
- Added missing `mkdocstrings[python]`, `twine`, and `bandit` to `[project.optional-dependencies] dev`.
- Improved type coverage in `wavexis_mcp/session.py` (`RateLimiter | None`, generic `call_backend[Awaitable[T]] -> T`).
- Reduced top-level `typing.Any` annotations in `act.py`, `network.py`, `server.py`, `utility.py`, and `formatter.py`; added `ANN401` clean run.
- Added `__all__` to `wavexis_mcp/__init__.py`.
- Updated `AGENTS.md` and `CONTRIBUTING.md` with the full verification command set (ruff, format, mypy, bandit, build, twine).
- Polished README with Requirements, Contributing, Acknowledgements, and expanded Documentation links.
- Fixed documentation duplicates (`docs/tools/core.md`, `docs/tools/devtools.md`) and WebAuthn tool-name mismatch in `docs/tools/experimental.md`.
- Added `.github/dependabot.yml`, `.github/CODEOWNERS`, and `.pre-commit-config.yaml`.
- Hardened Dockerfile with non-root user, output directory, and `CI` env for containerized Chrome sandbox.
- Added `restart: unless-stopped` to `docker-compose.yml`.
- Added `twine check` to release workflow and `bandit`, `build`, `twine check` to CI workflow.
- Expanded `pyproject.toml` classifiers, URLs, and maintainers metadata.
- Regenerated `docs/tools/*.md` from the actual registered MCP tools (220 tools) and added `scripts/generate_tool_docs.py` for future doc maintenance.
- Updated all tool count references from 195 to 220 across README, docs, `pyproject.toml`, and `mkdocs.yml`.
- Expanded `wavexis_mcp/__init__.py` public API exports to include `SessionManager`, `BrowserSession`, error classes, and `get_suggestion`.
- Replaced module-level `_REF_COUNTER` global in `wavexis_mcp/tools/a11y.py` with a per-call mutable counter.
- Added logging for URL-fetch failures in `wavexis_mcp/session.py`.

### Added

- Added `validate_url()` validation before every tool-level `backend.navigate()` call, including discovered links during crawls.
- Added a read-only allowlist for `wavexis_raw_cdp` and `wavexis_raw_bidi` with `WAVEXIS_MCP_ALLOW_RAW_COMMANDS=all` escape hatch.
- Added header filtering to `wavexis_set_headers` and CRLF rejection to `wavexis_set_user_agent`.
- Added sandboxing for `user_data_dir` in `SessionManager.open()` and `acquire_backend()`.
- Added 5-second timeouts to storage `backend.eval()` calls and resource handlers.
- Added stale-bucket eviction to `RateLimiter` to prevent unbounded memory growth.
- Added `tests/unit/test_security.py` regression suite covering SSRF, raw CDP/BiDi filtering, header filtering, and user-data sandboxing.
- Added `focus` action handling to `execute_act`.
- Added CDP screencast frame listener attachment and per-recording/total frame caps to `wavexis_video_record`.
- Added bucket cap and LRU eviction to `RateLimiter`.

### Changed

- Bumped mypy target from Python 3.11 to 3.12 for compatibility with newer type stubs.
- Updated `Development Status` classifier from Production/Stable to Beta.

### Fixed

- Resolved all `bandit` security findings (B104, B110, B112) in `server.py`, `tools/data.py`, and `tools/network.py`.
- Fixed `RateLimiter` race where captured `now` was earlier than the new bucket's `last_refill`.
- Removed fragile `atexit` cleanup in `server.py` in favor of the lifespan context manager.
- Removed redundant `call_backend()` wrapper around `get_current_url()` in `tools/session.py`.
- Removed dead `finally: pass` block in `tools/workflows.py`.
- Restored `ruff format` compliance for the codebase.
- Hardened header-injection defenses in `SessionManager.open()`, `wavexis_set_headers`, `wavexis_route`, and `wavexis_service_worker_emulate`.
- Fixed `wavexis_perf_coverage` to safely handle non-list, non-dict backend results.
- Fixed `wavexis_storage_state_restore` to return a clear error for malformed JSON.
- Replaced unbounded network log and route lists with bounded `deque` containers.
- Added exponential backoff to testing assertion polling and streaming poll loops.
- Fixed `SessionManager.cleanup_all()` to log errors instead of silently suppressing them.
- Fixed Dockerfile wheel copy glob and expanded sdist includes.

## [1.6.6] - 2025-07-24

### Added

- New `wavexis_mcp/tools/playwright_parity.py` module with text-based accessibility find tools.
- Full unit + integration test coverage (`425` tests passing, `100%` coverage across `wavexis_mcp`).
- Coverage-gap tests in `tests/unit/test_coverage_gaps.py`, `test_coverage_remaining.py`, and `test_network_extended.py`.

### Changed

- Lint/format cleanup across the entire codebase (`ruff check` and `ruff format` now pass).
- Added missing `Any` imports in `wavexis_mcp/tools/input.py` and `wavexis_mcp/tools/workflows.py`.
- Repository cleanup: removed `__pycache__`, `.coverage`, `htmlcov/`, `dist/`, `site/`, `.mypy_cache`, `.pytest_cache`, `.ruff_cache`, and stray `tmp_debug.py`.

## [1.6.4] - 2025-07-08

### Changed

- Documentation: updated all tool counts from 175 to 195 across README, docs, and pyproject.toml
- Documentation: updated tier counts (core 45→56, network 10→14, storage 13→18, a11y 3→4, devtools 23→31, experimental 26→31)
- Documentation: added missing tools to tier reference tables (iframe, shadow DOM, events, IndexedDB, combined trace, annotated screenshot, axe audit, modify request/response, HAR replay, browser context list, and more)
- Documentation: fixed tab tool names in core.md to match actual registered names

## [1.6.3] - 2025-07-08

### Added

- 2 unit tests for `wavexis_annotated_screenshot` (base64 + file output modes)
- Test audit: 100% tool coverage — all 195 tools now have tests

### Changed

- Test count: 334 → 336

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
