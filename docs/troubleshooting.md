# Troubleshooting

Common issues and their solutions when using WaveXisMCP.

---

## Browser not found

**Symptom:** `BrowserError: Could not find Chrome or Edge`

**Cause:** WaveXisMCP auto-detects Chrome then Edge, but neither is installed or the path is wrong.

**Solution:**

1. Install [Google Chrome](https://www.google.com/chrome/) or [Microsoft Edge](https://www.microsoft.com/edge).
2. If Chrome is installed in a non-standard location, set the `WAVEXIS_BROWSER_PATH` environment variable:

    ```bash
    # Linux/macOS
    export WAVEXIS_BROWSER_PATH=/usr/bin/google-chrome

    # Windows (PowerShell)
    $env:WAVEXIS_BROWSER_PATH = "C:\Program Files\Google\Chrome\Application\chrome.exe"
    ```

3. Verify the path is correct by running the browser manually.

---

## Session limit reached

**Symptom:** `RuntimeError: Maximum number of sessions (1000) reached`

**Cause:** Too many concurrent sessions. The default limit is 1000.

**Solution:**

- Close unused sessions with `wavexis_session_close`.
- Use `wavexis_session_list` to see active sessions.
- Use `wavexis_cleanup_all` (or restart the server) to close all sessions.
- For long-running workflows, reuse a single session instead of opening new ones.
- Use stateless mode (pass `url` directly to tools) for one-shot operations — no session needed.

---

## Rate limit exceeded

**Symptom:** `RuntimeError: Rate limit exceeded. Retry after 500ms`

**Cause:** The token bucket rate limiter is throttling tool calls. Default: 60 calls/second with burst of 10.

**Solution:**

- Increase the rate limit: `wavexis-mcp --rate-limit=120 --rate-burst=20`
- For high-throughput CI/CD, disable rate limiting by setting a very high limit: `wavexis-mcp --rate-limit=10000`
- If using HTTP transport, consider running multiple WaveXisMCP instances behind a load balancer.

---

## URL rejected as internal/private

**Symptom:** `ValueError: URL resolves to a private/internal IP and is blocked`

**Cause:** WaveXisMCP blocks navigation to private IPs (localhost, 10.x.x, 172.16.x, 192.168.x, 169.254.x) and cloud metadata endpoints by default to prevent SSRF.

**Solution:**

- If you intentionally need to navigate to internal URLs (e.g., local development), set the environment variable:

    ```bash
    export WAVEXIS_MCP_ALLOW_INTERNAL_URLS=1
    ```

- This applies to `validate_url` and `validate_websocket_url`.
- **Warning:** Only enable this in trusted environments. Never enable in production with untrusted LLM output.

---

## WebSocket endpoint rejected

**Symptom:** `ValueError: WebSocket URL scheme 'http' is not allowed`

**Cause:** `connect_endpoint` and `remote_url` only accept `ws://` and `wss://` schemes.

**Solution:**

- Use `ws://` for unencrypted or `wss://` for encrypted WebSocket connections.
- Example: `wavexis_session_open(connect_endpoint="ws://localhost:9222")`

---

## UNC paths not allowed (Windows)

**Symptom:** `ValueError: UNC paths are not allowed: '\\server\share\file.png'`

**Cause:** WaveXisMCP rejects UNC paths (`\\server\share`) for security reasons on Windows.

**Solution:**

- Map the network share to a drive letter (e.g., `Z:`) and use the drive path instead.
- Or copy the file to a local directory and use the local path.
- Set `WAVEXIS_MCP_OUTPUT_DIR` to a local directory.

---

## Output path outside allowed directory

**Symptom:** `ValueError: Output path '...' is outside the allowed output directory`

**Cause:** All file outputs (screenshots, PDFs, traces) must be within the output directory configured by `WAVEXIS_MCP_OUTPUT_DIR` (defaults to the current working directory). Paths that escape this directory are rejected.

**Solution:**

- Set `WAVEXIS_MCP_OUTPUT_DIR` to a directory that contains all your output paths:

    ```bash
    export WAVEXIS_MCP_OUTPUT_DIR=/home/user/wavexis-output
    ```

- Use relative paths (they are resolved against the output directory).
- Symlinks that escape the output directory are also rejected.

---

## Element not found / stale element

**Symptom:** `RuntimeError: element not found` or `RuntimeError: element is stale`

**Cause:** The CSS selector doesn't match any element, or the element was removed from the DOM after the selector was resolved.

**Solution:**

- Use `wavexis_dom_get` to inspect the current DOM and verify the selector.
- Add a wait before interacting: `wavexis_navigate(url="...", wait_timeout=5000)`.
- Use `wavexis_act` for natural language interaction — it handles element matching automatically.
- WaveXisMCP auto-retries stale element errors (2 retries, 100ms delay) for `click`, `fill`, `hover`, `tap`, `select_option`, and `double_click`. If the element is persistently stale, the selector may need updating.
- Use `wavexis_find` to locate elements by text content instead of CSS selectors.

---

## Chrome crashes or hangs

**Symptom:** Browser process crashes, hangs, or becomes unresponsive.

**Solution:**

- Ensure Chrome is up to date.
- Try `headless=false` to see the browser window for debugging.
- Check available memory — Chrome uses ~200-500MB per session.
- Reduce the number of concurrent sessions.
- Use `--caps` to limit loaded tools (fewer tiers = less overhead).
- If using Docker, ensure sufficient shared memory: `docker run --shm-size=2g ...`
- Check `dmesg` for OOM killer events on Linux.

---

## HTTP transport not accessible remotely

**Symptom:** HTTP server is reachable locally but not from other machines.

**Solution:**

- By default, WaveXisMCP binds to `127.0.0.1`. Use `--allow-remote` to bind to `0.0.0.0`:

    ```bash
    wavexis-mcp --transport http --allow-remote --port=8765
    ```

- **Warning:** `--allow-remote` disables authentication. Use behind a reverse proxy with authentication (nginx, Caddy, etc.).
- Ensure firewall rules allow traffic on the configured port.

---

## BiDi backend not working with Firefox

**Symptom:** `BackendError: BiDi backend failed to launch`

**Solution:**

- Ensure Firefox is installed and up to date.
- Set `WAVEXIS_BROWSER_PATH` to the Firefox binary path.
- Use `backend="bidi"` when opening a session: `wavexis_session_open(backend="bidi")`
- BiDi support depends on the `wavexis` library version. Check [wavexis documentation](https://github.com/MathiasPaulenko/wavexis) for Firefox compatibility.

---

## Tool not found / not registered

**Symptom:** LLM tries to call a tool but gets "tool not found"

**Cause:** The tool belongs to a capability tier that is not enabled.

**Solution:**

- Check which tiers are enabled: `wavexis-mcp --help` shows the current caps.
- Enable the required tier: `wavexis-mcp --caps=core,devtools,a11y`
- Enable all tiers: `wavexis-mcp --caps=all`
- See [Configuration](configuration.md) for the full tier list.

---

## Memory leak / growing memory usage

**Symptom:** Server memory grows over time and doesn't stabilize.

**Solution:**

- Close sessions when done: `wavexis_session_close`.
- Use `wavexis_session_list` to check for leaked sessions.
- Rate limiter buckets are cleaned up on session close. If using stateless mode extensively, restart the server periodically.
- Check for orphaned Chrome processes: `ps aux | grep chrome` (Linux) or Task Manager (Windows).
- The lifespan handler cleans up all sessions on shutdown, but hard kills (SIGKILL) may leave orphaned browsers.

---

## Getting help

If none of these solutions work:

- [Open an issue on GitHub](https://github.com/MathiasPaulenko/wavexis-mcp/issues)
- Check [existing issues](https://github.com/MathiasPaulenko/wavexis-mcp/issues?q=is%3Aissue) for similar problems
- Include the WaveXisMCP version (`wavexis-mcp --help`), your OS, Chrome version, and the full error message.
