# Testing Tools (6)

Enable with `--caps=testing`.

These 6 tools are added when the `testing` capability tier is enabled.

## Testing

| Tool | Parameters | Description |
| --- | --- | --- |
| `wavexis_assert_list` | `session_id, selector, items, timeout?` | Assert that all expected text items are visible inside a list element. |
| `wavexis_assert_text_visible` | `session_id, text, timeout?` | Assert that specific text is visible on the page. |
| `wavexis_assert_url` | `session_id, url_pattern` | Assert the current URL matches a pattern. |
| `wavexis_assert_value` | `session_id, selector, value, timeout?` | Assert that a form element has the expected value. |
| `wavexis_assert_visible` | `session_id, selector, timeout?` | Assert that an element is visible on the page. |
| `wavexis_generate_locator` | `session_id, selector, description?` | Generate a robust CSS selector for an element. |
