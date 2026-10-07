# Changelog

For the full changelog, see [CHANGELOG.md](https://github.com/MathiasPaulenko/wavexis-mcp/blob/main/CHANGELOG.md) in the repository root.

## Recent releases

### v1.7.0

- Fixed `--storage-state` restore to use the current wavexis API (`network_set_cookies`); localStorage/sessionStorage now restored via preload script so origin-scoped storage persists
- Fixed `wavexis_invoke` for backend methods with dataclass `params` (`screenshot`, `pdf`, `throttle_network`, `capture_har`, `set_sensors`, `set_cookie`, `screencast`, ...)
- `wavexis_lighthouse` now computes real scores from DOM and performance checks (no more hardcoded values)
- `wavexis_websocket_intercept` now captures real WebSocket frames via CDP (capture-only; `mock_responses` is rejected explicitly)
- `wavexis_bluetooth_device_list` returns devices emulated via `wavexis_bluetooth_device_connect`
- Video: screencast frames are acked (Chrome keeps streaming), `wavexis_video_stop` accepts `recording_id` and reports `format: "mjpeg"` plus `chapters`, `wavexis_video_action_overlay` injects a real on-page overlay
- `--rate-limit 0` now disables limiting; stateless calls share a global bucket
- SSRF: trailing-dot hostnames (e.g. `localhost.`) normalized before checks
- Packaging: `wavexis[cdp]` is a base dependency — `uvx wavexis-mcp` works out of the box
- Docker: health check uses `/sse`, entrypoint uses `--allow-remote`, `CDPWAVE_BROWSER_PATH` env var
- `--help` shows the extended tier-aware help; non-loopback `--host` warns without `--allow-remote`
- `wavexis_video_record` errors explicitly when the backend cannot deliver screencast frames (no CDP event subscription) instead of silently recording zero frames
- `secure_output_path` rejects Windows directory junctions, not just symlinks
- `connect_existing` uses a dynamically allocated debug port when 9223 is taken
- `wavexis_subscribe_events` actually buffers events; `wavexis_unsubscribe_events` returns them
- mypy now type-checks wavexis imports (`follow_imports` no longer skipped)
- Removed the dead `StreamingHandler` module
- Docs: corrected tier tool counts, env variables, tool names, Docker build steps, HTTP/SSE transport notes

### v1.6.24

- Published to Smithery.ai registry
- Published to MCP Registry (`io.github.MathiasPaulenko/wavexis-mcp`)
- Published to Glama.ai
- Improved parameter descriptions for all 220 tools (100% coverage)
- Added Smithery badge to docs

### v1.6.21

- Added `connect_existing` for reusing existing Chrome instances
- Added `browser` field for browser selection
- Firefox BiDi support via wavexis 2.18.0

### v1.6.6

- 220 tools across 13 capability tiers
- Stealth mode
- Multi-action YAML batching
- Lighthouse audits
- Structured errors with LLM-actionable suggestions
