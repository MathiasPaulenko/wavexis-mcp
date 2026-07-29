# Testing Tools (6)

Enable with `--caps=testing`.

Visual regression, element screenshots, and test helpers. Enable with `--caps=testing`.

## Summary

| Tool | Parameters | Description |
| --- | --- | --- |
| [`wavexis_assert_list`](#wavexis_assert_list) | `session_id, selector, items, timeout?` | Assert that all expected text items are visible inside a list element. |
| [`wavexis_assert_text_visible`](#wavexis_assert_text_visible) | `session_id, text, timeout?` | Assert that specific text is visible on the page. |
| [`wavexis_assert_url`](#wavexis_assert_url) | `session_id, url_pattern` | Assert the current URL matches a pattern. |
| [`wavexis_assert_value`](#wavexis_assert_value) | `session_id, selector, value, timeout?` | Assert that a form element has the expected value. |
| [`wavexis_assert_visible`](#wavexis_assert_visible) | `session_id, selector, timeout?` | Assert that an element is visible on the page. |
| [`wavexis_generate_locator`](#wavexis_generate_locator) | `session_id, selector, description?` | Generate a robust CSS selector for an element. |

## Testing

### wavexis_assert_list

Assert that all expected text items are visible inside a list element.

Args:
    input: Assertion parameters (selector, items, timeout).

Returns:
    JSON string with ``passed``, ``items``, ``missing``, and ``message``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `selector` | string | Yes | — | CSS selector for the list element |
| `items` | array | Yes | — | Expected visible text items |
| `timeout` | integer | No | `5000` | Timeout in ms |

### wavexis_assert_text_visible

Assert that specific text is visible on the page.

Args:
    input: Assertion parameters (text, timeout).

Returns:
    JSON string with ``passed``, ``text``, and ``message``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `text` | string | Yes | — | Text to search for |
| `timeout` | integer | No | `5000` | Timeout in ms |

### wavexis_assert_url

Assert the current URL matches a pattern.

Args:
    input: Assertion parameters (url_pattern).

Returns:
    JSON string with ``passed``, ``url``, and ``pattern``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `url_pattern` | string | Yes | — | URL substring or pattern to match |

### wavexis_assert_value

Assert that a form element has the expected value.

Args:
    input: Assertion parameters (selector, value, timeout).

Returns:
    JSON string with ``passed``, ``value``, and ``message``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `selector` | string | Yes | — | CSS selector for the input element |
| `value` | string | Yes | — | Expected value |
| `timeout` | integer | No | `5000` | Timeout in ms |

### wavexis_assert_visible

Assert that an element is visible on the page.

Args:
    input: Assertion parameters (selector, timeout).

Returns:
    JSON string with ``passed``, ``selector``, and ``message``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `selector` | string | Yes | — | CSS selector for the element |
| `timeout` | integer | No | `5000` | Timeout in ms |

### wavexis_generate_locator

Generate a robust CSS selector for an element.

Uses the backend's ``suggest_locator`` method to produce
optimal selectors in priority order: id > data-testid >
aria-label > text > tag.classes > nth-of-type chain.

Args:
    input: Locator parameters (selector, description).

Returns:
    JSON string with ``locator`` and ``alternative``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `selector` | string | Yes | — | Approximate CSS selector |
| `description` | string | No | `null` | Natural-language description |
