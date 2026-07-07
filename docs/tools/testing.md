# Testing Tools (4)

Enable with `--caps=testing`.

Testing tools provide assertion-based verification. Assert element visibility, text presence, and URL matching. Generate robust CSS selectors for elements. These tools return pass/fail results as JSON, making them ideal for automated test pipelines and for the LLM to verify that its actions had the expected effect.

| Tool | Parameters | Description |
| --- | --- | --- |
| `wavexis_assert_visible` | `session_id`, `selector`, `timeout` | Assert that an element is visible on the page. Waits up to `timeout` ms (default 5000). Returns `{"passed": true}` or `{"passed": false, "reason": "..."}`. |
| `wavexis_assert_text_visible` | `session_id`, `text`, `selector`, `timeout` | Assert that specific text is visible. Optionally scope to a `selector`. Waits up to `timeout` ms. |
| `wavexis_assert_url` | `session_id`, `url`, `match_type` | Assert the current URL matches. `match_type`: `exact` (default), `contains`, `startswith`, `regex`. |
| `wavexis_generate_locator` | `session_id`, `selector`, `all` | Generate a robust CSS selector for an element. Tries ID, data-testid, class combinations, and nth-child. `all=true` returns multiple locator options. |

!!! example "Test a login flow"
    ```text
    wavexis_session_open(backend="cdp")
    wavexis_navigate(session_id="abc-123", url="https://app.example.com/login")

    # Assert the login form is visible
    wavexis_assert_visible(session_id="abc-123", selector="#login-form", timeout=5000)
    → {"passed": true}

    # Fill and submit
    wavexis_fill(session_id="abc-123", selector="#email", value="user@example.com")
    wavexis_fill(session_id="abc-123", selector="#password", value="secret")
    wavexis_click(session_id="abc-123", selector="#submit")

    # Assert we redirected to dashboard
    wavexis_assert_url(session_id="abc-123", url="https://app.example.com/dashboard", match_type="startswith")
    → {"passed": true}

    # Assert welcome text is visible
    wavexis_assert_text_visible(session_id="abc-123", text="Welcome back")
    → {"passed": true}

    wavexis_session_close(session_id="abc-123")
    ```

!!! example "Generate a robust locator"
    ```text
    wavexis_generate_locator(session_id="abc-123", selector=".btn-primary", all=true)
    → {"locators": ["#submit-btn", "[data-testid='submit']", "button.btn-primary", "form > button:nth-child(3)"]}
    ```

    The generated locators are ordered by robustness — ID-based selectors first, then data-testid, then class-based, then structural.
