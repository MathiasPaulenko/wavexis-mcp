# Screenshot Examples

Screenshots are the most common use case for WaveXisMCP. The `wavexis_screenshot` tool supports stateless one-shot captures, session-based multi-step workflows, element-specific screenshots, full-page captures, and device-emulated screenshots.

## Stateless (one-shot)

The simplest case. Pass a `url` — the browser launches, navigates, captures, and closes automatically. No session management needed.

```text
wavexis_screenshot(url="https://example.com", full_page=true)
```

Returns base64-encoded PNG. The browser launches, captures, and closes automatically.

**When to use**: Quick one-off captures where you don't need to interact with the page first.

## Session-based element screenshot

When you need to interact with the page before capturing (e.g., click a button, fill a form, wait for content to load), use a session:

```text
wavexis_session_open(backend="cdp", headless=false)
→ {"session_id": "abc-123"}

wavexis_navigate(session_id="abc-123", url="https://example.com")
wavexis_wait(session_id="abc-123", strategy="selector", selector="#hero")

wavexis_screenshot(
    session_id="abc-123",
    selector="#hero",
    output_path="./screenshots/hero.png"
)
→ {"path": "./screenshots/hero.png", "format": "png", "encoding": "file"}

wavexis_session_close(session_id="abc-123")
```

**When to use**: When you need to wait for dynamic content, interact with the page, or capture a specific element.

## Full page with device emulation

Test responsive design by emulating a mobile device before capturing:

```text
wavexis_session_open(backend="cdp")
→ {"session_id": "abc-123"}

wavexis_emulate_device(session_id="abc-123", device="iPhone 15")
wavexis_navigate(session_id="abc-123", url="https://example.com", wait_until="networkidle")
wavexis_screenshot(session_id="abc-123", full_page=true)
→ {"data": "iVBORw0KGgo...", "format": "png", "encoding": "base64"}

wavexis_session_close(session_id="abc-123")
```

Requires `--caps=emulation`.

**When to use**: Responsive design testing, mobile layout verification, generating screenshots for multiple device sizes.

## Screenshot after form interaction

Capture the result of a form submission:

```text
wavexis_session_open(backend="cdp")
→ {"session_id": "abc-123"}

wavexis_navigate(session_id="abc-123", url="https://app.example.com/search")
wavexis_fill(session_id="abc-123", selector="#search-box", value="wavexis mcp")
wavexis_key_press(session_id="abc-123", key="Enter")

wavexis_wait(session_id="abc-123", strategy="selector", selector=".results", timeout=10000)
wavexis_screenshot(session_id="abc-123", selector=".results")
→ {"data": "iVBORw0KGgo...", "format": "png", "encoding": "base64"}

wavexis_session_close(session_id="abc-123")
```

**When to use**: Documenting search results, form submissions, or any state change that requires user interaction first.

## Output formats

| Parameter | Behavior |
|-----------|----------|
| `format=png` (default) | Lossless, larger file size. Best for UI screenshots. |
| `format=jpeg` | Lossy, smaller file size. Best for full-page captures where file size matters. |
| `output_path="./shot.png"` | Writes to disk instead of returning base64. The JSON response contains the file path. |
| No `output_path` | Returns base64-encoded data in the JSON response. The LLM can display it directly. |
