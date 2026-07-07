# Screenshot Example

## Stateless (one-shot)

```python
wavexis_screenshot(url="https://example.com", full_page=true)
```

Returns base64-encoded PNG. The browser launches, captures, and closes automatically.

## Session-based

```python
wavexis_session_open(backend="cdp", headless=false)
# → {"session_id": "abc-123"}

wavexis_navigate(session_id="abc-123", url="https://example.com")
wavexis_screenshot(
    session_id="abc-123",
    selector="#hero",
    output_path="./screenshots/hero.png"
)
wavexis_session_close(session_id="abc-123")
```

## Full page with device emulation

```python
wavexis_session_open(backend="cdp")
# → {"session_id": "abc-123"}

wavexis_emulate_device(session_id="abc-123", device="iPhone 15")
wavexis_navigate(session_id="abc-123", url="https://example.com")
wavexis_screenshot(session_id="abc-123", full_page=true)
wavexis_session_close(session_id="abc-123")
```

Requires `--caps=emulation`.
