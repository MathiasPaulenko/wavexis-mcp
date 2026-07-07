# Testing Examples

WaveXisMCP can verify page state through assertion tools and run Lighthouse audits for performance, accessibility, and SEO scoring.

## Assert element is visible

Verify that an element appears on the page after navigation:

```text
wavexis_session_open(backend="cdp")
→ {"session_id": "abc-123"}

wavexis_navigate(session_id="abc-123", url="https://example.com")

wavexis_assert_visible(session_id="abc-123", selector="#hero", timeout=5000)
→ {"passed": true}

wavexis_assert_text_visible(session_id="abc-123", text="Welcome")
→ {"passed": true}

wavexis_assert_url(session_id="abc-123", url="https://example.com")
→ {"passed": true}

wavexis_session_close(session_id="abc-123")
```

Requires `--caps=testing`.

**When to use**: Verifying that navigation succeeded, content rendered, or redirects worked correctly.

## Full login flow test

A complete end-to-end test of a login flow with assertions at each step:

```text
wavexis_session_open(backend="cdp")
→ {"session_id": "abc-123"}

# 1. Navigate to login page
wavexis_navigate(session_id="abc-123", url="https://app.example.com/login")
wavexis_assert_visible(session_id="abc-123", selector="#login-form", timeout=5000)
→ {"passed": true}

# 2. Fill credentials
wavexis_fill_form(
    session_id="abc-123",
    fields=[
        {"selector": "#email", "value": "user@example.com"},
        {"selector": "#password", "value": "secret123"}
    ]
)

# 3. Submit
wavexis_click(session_id="abc-123", selector="#submit")

# 4. Verify redirect to dashboard
wavexis_assert_url(
    session_id="abc-123",
    url="https://app.example.com/dashboard",
    match_type="startswith"
)
→ {"passed": true}

# 5. Verify welcome message
wavexis_assert_text_visible(session_id="abc-123", text="Welcome back")
→ {"passed": true}

wavexis_session_close(session_id="abc-123")
```

**When to use**: End-to-end testing of critical user flows (login, signup, checkout, etc.).

## Generate robust locator

Generate multiple CSS selector options for an element, ordered by robustness:

```text
wavexis_session_open(backend="cdp")
→ {"session_id": "abc-123"}

wavexis_navigate(session_id="abc-123", url="https://example.com")

wavexis_generate_locator(
    session_id="abc-123",
    selector=".btn-primary",
    all=true
)
→ {"locators": [
    "#submit-btn",
    "[data-testid='submit']",
    "button.btn-primary",
    "form > button:nth-child(3)"
]}

wavexis_session_close(session_id="abc-123")
```

**When to use**: When writing tests and you need a selector that won't break when classes change. The tool tries ID first, then data-testid, then class combinations, then structural selectors.

## Lighthouse audit

Run a full Lighthouse audit for performance, accessibility, and SEO:

```text
wavexis_session_open(backend="cdp")
→ {"session_id": "abc-123"}

wavexis_lighthouse(
    session_id="abc-123",
    url="https://example.com",
    categories=["performance", "accessibility", "seo", "best-practices"]
)
→ {
    "scores": {
        "performance": 95,
        "accessibility": 100,
        "seo": 92,
        "best-practices": 100
    },
    "metrics": {
        "lcp": 1200,
        "fcp": 800,
        "cls": 0.05,
        "tbt": 50,
        "ttfb": 200
    }
}

wavexis_session_close(session_id="abc-123")
```

Requires `--caps=data`.

**When to use**: Performance auditing, CI/CD quality gates, tracking metrics over time. Scores are 0-100 (higher is better). Key metrics: LCP (Largest Contentful Paint, <2500ms is good), CLS (Cumulative Layout Shift, <0.1 is good), TBT (Total Blocking Time, <200ms is good).
