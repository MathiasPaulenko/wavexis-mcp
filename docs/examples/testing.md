# Testing Example

## Assert element is visible

```python
wavexis_session_open(backend="cdp")
# → {"session_id": "abc-123"}

wavexis_navigate(session_id="abc-123", url="https://example.com")
wavexis_assert_visible(session_id="abc-123", selector="#hero")
wavexis_assert_text_visible(session_id="abc-123", text="Welcome")
wavexis_assert_url(session_id="abc-123", url="https://example.com")
wavexis_session_close(session_id="abc-123")
```

Requires `--caps=testing`.

## Generate robust locator

```python
wavexis_session_open(backend="cdp")
# → {"session_id": "abc-123"}

wavexis_navigate(session_id="abc-123", url="https://example.com")
wavexis_generate_locator(
    session_id="abc-123",
    selector=".btn-primary",
    all=true
)
# → {"locators": ["#submit-btn", "[data-testid='submit']", "button.btn-primary"]}
wavexis_session_close(session_id="abc-123")
```

## Lighthouse audit

```python
wavexis_session_open(backend="cdp")
# → {"session_id": "abc-123"}

wavexis_lighthouse(
    session_id="abc-123",
    url="https://example.com",
    categories=["performance", "accessibility", "seo"]
)
wavexis_session_close(session_id="abc-123")
```

Requires `--caps=data`.
