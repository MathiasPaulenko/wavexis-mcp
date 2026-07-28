# Tutorials

Step-by-step guides for common browser automation workflows with WaveXisMCP.

Each tutorial assumes you have WaveXisMCP configured in your LLM client (see [Quick Start](quickstart.md)). You can also run these examples programmatically via the MCP SDK.

---

## Scrape a product page

Extract the title, price, and description from an e-commerce page.

```text
wavexis_session_open(backend="cdp")
→ {"session_id": "abc-123"}

wavexis_navigate(session_id="abc-123", url="https://example-shop.com/product/42")

wavexis_scrape(session_id="abc-123", selector=".product-detail")
→ {
    "title": "Wireless Headphones",
    "price": "$79.99",
    "description": "Bluetooth 5.3, 30h battery life..."
  }

wavexis_session_close(session_id="abc-123")
```

**Tips:**

- Use `wavexis_dom_get` with a specific selector to extract structured HTML.
- Use `wavexis_extract` (requires `--caps=data`) for CSS-selector-based structured extraction with multiple fields.
- For JavaScript-rendered content, add `wait_timeout=5000` to `wavexis_navigate` to wait for the page to load.

---

## Fill and submit a login form

Automate a login flow with form filling and submission.

```text
wavexis_session_open(backend="cdp")
→ {"session_id": "abc-123"}

wavexis_navigate(session_id="abc-123", url="https://example.com/login")

wavexis_fill(session_id="abc-123", selector="#email", value="user@example.com")
wavexis_fill(session_id="abc-123", selector="#password", value="secret123")
wavexis_click(session_id="abc-123", selector="#submit")

# Verify we're logged in
wavexis_assert_visible(session_id="abc-123", selector=".dashboard")
→ {"status": "ok", "passed": true}

wavexis_session_close(session_id="abc-123")
```

**Using multi-action for fewer round-trips:**

```text
wavexis_multi_action(
    session_id="abc-123",
    config=[
        {"type": "navigate", "url": "https://example.com/login"},
        {"type": "fill", "selector": "#email", "value": "user@example.com"},
        {"type": "fill", "selector": "#password", "value": "secret123"},
        {"type": "click", "selector": "#submit"}
    ]
)
```

Requires `--caps=workflows`.

**Preserving login state across sessions:**

```bash
# Start server with --storage-state to restore a saved session
wavexis-mcp --caps=core,storage --storage-state=./auth-state.json
```

Use `wavexis_storage_state_save` to capture the state after logging in, then restart the server with `--storage-state` to skip the login flow on subsequent runs.

---

## Run an accessibility audit

Check a page for WCAG violations using axe-core.

```text
wavexis_session_open(backend="cdp")
→ {"session_id": "abc-123"}

wavexis_navigate(session_id="abc-123", url="https://example.com")

wavexis_axe_audit(session_id="abc-123")
→ {
    "violations": [
        {"id": "color-contrast", "impact": "serious", "nodes": 3},
        {"id": "image-alt", "impact": "critical", "nodes": 1}
    ],
    "passes": 47,
    "incomplete": 2
  }

wavexis_session_close(session_id="abc-123")
```

Requires `--caps=a11y`.

**Tips:**

- Use `wavexis_a11y_snapshot` to get the full accessibility tree with element references (`el-1`, `el-2`).
- Pass element references to `wavexis_a11y_get` to inspect specific nodes.
- Combine with `wavexis_act` to fix issues by interacting with elements using natural language.

---

## Debug a slow page

Capture performance metrics and a trace to diagnose slow loading.

```text
wavexis_session_open(backend="cdp")
→ {"session_id": "abc-123"}

wavexis_navigate(session_id="abc-123", url="https://example.com")

# Get performance metrics
wavexis_perf_metrics(session_id="abc-123")
→ {"LCP": 3200, "FCP": 1200, "CLS": 0.12, "TTFB": 450}

# Capture a 5-second trace
wavexis_perf_trace(session_id="abc-123", duration_ms=5000, output_path="trace.json")
→ {"path": "trace.json", "events": 1247}

# Check network requests
wavexis_request_list(session_id="abc-123")
→ {"requests": [...]}

wavexis_session_close(session_id="abc-123")
```

Requires `--caps=devtools,network`.

**Using --auto-web-vitals for continuous monitoring:**

```bash
wavexis-mcp --caps=core,devtools --auto-web-vitals
```

This injects a web-vitals collection script after every navigation. Results are stored in `window.__wavexis_vitals` and can be read with `wavexis_eval`:

```text
wavexis_eval(session_id="abc-123", expression="window.__wavexis_vitals")
→ {"lcp": 3200, "cls": 0.12, "inp": 180}
```

---

## Crawl a documentation site

Crawl multiple pages and extract content from each.

```text
wavexis_session_open(backend="cdp")
→ {"session_id": "abc-123"}

wavexis_crawl(
    session_id="abc-123",
    start_url="https://docs.example.com",
    max_pages=20,
    selector="main article",
    same_origin=true
)
→ {
    "pages_crawled": 18,
    "pages": [
        {"url": "https://docs.example.com/", "title": "Home", "content": "..."},
        {"url": "https://docs.example.com/guide", "title": "Guide", "content": "..."}
    ]
  }

wavexis_session_close(session_id="abc-123")
```

Requires `--caps=data`.

**Tips:**

- Set `same_origin=true` to restrict crawling to the same domain.
- Use `max_pages` to limit the crawl scope.
- Use `selector` to extract only the main content area, ignoring navigation and footer.

---

## Record a bug report video

Record a video of a reproduction step for a bug report.

```text
wavexis_session_open(backend="cdp")
→ {"session_id": "abc-123"}

wavexis_video_start(session_id="abc-123")
wavexis_navigate(session_id="abc-123", url="https://example.com")
wavexis_click(session_id="abc-123", selector="#broken-button")

# Add a chapter marker
wavexis_video_chapter(session_id="abc-123", title="Bug reproduces here")

wavexis_screenshot(session_id="abc-123", output_path="bug-evidence.png")
wavexis_video_stop(session_id="abc-123", output_path="bug-repro.webm")
→ {"path": "bug-repro.webm", "duration_s": 12.5, "frames": 375}

wavexis_session_close(session_id="abc-123")
```

Requires `--caps=video`.

---

## Test a multi-user scenario

Use browser contexts to test two users interacting simultaneously.

```text
wavexis_session_open(backend="cdp")
→ {"session_id": "abc-123"}

# Create two isolated contexts
wavexis_browser_context_create(session_id="abc-123")
→ {"context_id": "ctx-1"}
wavexis_browser_context_create(session_id="abc-123")
→ {"context_id": "ctx-2"}

# Context 1: User A logs in
# Context 2: User B logs in
# They don't share cookies — fully isolated

# Clean up
wavexis_browser_context_close(session_id="abc-123", context_id="ctx-1")
wavexis_browser_context_close(session_id="abc-123", context_id="ctx-2")
wavexis_session_close(session_id="abc-123")
```

Requires `--caps=workflows`.

---

## Block ads and trackers globally

Start the server with `--blocked-origins` to block ad/tracker domains on every session:

```bash
wavexis-mcp --caps=core,network --blocked-origins="*doubleclick.net,*googletagmanager.com,*ads*,*tracker*"
```

This applies the block patterns to every new session automatically, without needing to call `wavexis_block_requests` manually.

---

## Next steps

- [Troubleshooting](troubleshooting.md) — common issues and solutions
- [Benchmarks](benchmarks.md) — performance comparison vs Playwright MCP
- [Configuration](configuration.md) — all CLI flags and environment variables
- [Examples](examples/screenshot.md) — more code examples
