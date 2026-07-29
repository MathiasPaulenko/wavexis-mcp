# Data Tools (7)

Enable with `--caps=data`.

Structured data extraction: tables, forms, metadata, OpenGraph. Enable with `--caps=data`.

## Summary

| Tool | Parameters | Description |
| --- | --- | --- |
| [`wavexis_core_web_vitals`](#wavexis_core_web_vitals) | `url, session_id?, observe_ms?, budgets?, headless?, backend?` | Measure Core Web Vitals (LCP, CLS, INP) with ratings and score. |
| [`wavexis_crawl`](#wavexis_crawl) | `start_url, max_depth?, max_pages?, same_origin?, url_pattern?, session_id?, wait_timeout?, headless?, backend?` | Crawl a website starting from a URL. |
| [`wavexis_extract`](#wavexis_extract) | `url, schema, selector?, session_id?, wait_timeout?, headless?, backend?` | Extract structured data from a page using a CSS selector schema. |
| [`wavexis_lighthouse`](#wavexis_lighthouse) | `url, categories?, session_id?, wait_timeout?, headless?, backend?` | Run a Lighthouse-style audit on a URL. |
| [`wavexis_record`](#wavexis_record) | `session_id?, url, duration?, headless?, backend?` | Record browser interactions and generate a YAML workflow. |
| [`wavexis_visual_diff`](#wavexis_visual_diff) | `url, baseline_path, selector?, threshold?, output_path?, session_id?, wait_timeout?, headless?, backend?` | Compare a screenshot against a baseline image. |
| [`wavexis_websocket_intercept`](#wavexis_websocket_intercept) | `url, url_pattern?, duration_ms?, mock_responses?, session_id?, wait_timeout?, headless?, backend?` | Capture WebSocket frames on a page. |

## Data Extraction

### wavexis_core_web_vitals

Measure Core Web Vitals (LCP, CLS, INP) with ratings and score.

Args:
    input: CWV parameters (url, observe_ms, budgets).

Returns:
    JSON string with ``metrics``, ``ratings``, ``score``, and optional ``budgets``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `url` | string | Yes | — | URL to navigate to for measurement |
| `session_id` | string | No | `null` | Active session ID. If omitted, a stateless session is created for this call. |
| `observe_ms` | integer | No | `5000` | Observation window in milliseconds |
| `budgets` | object | No | — | Optional budgets: lcp_ms, cls, inp_ms, fcp_ms, ttfb_ms, tbt_ms, load_ms |
| `headless` | boolean | No | `true` | Run browser in headless mode |
| `backend` | string (cdp, bidi, auto) | No | `"cdp"` | Backend: 'cdp', 'bidi', or 'auto' |

### wavexis_crawl

Crawl a website starting from a URL.

Args:
    input: Crawl parameters (start_url, max_depth, max_pages).

Returns:
    JSON string with ``pages`` list and counts.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `start_url` | string | Yes | — | Starting URL for the crawl |
| `max_depth` | integer | No | `2` | Maximum crawl depth |
| `max_pages` | integer | No | `50` | Maximum pages to visit |
| `same_origin` | boolean | No | `true` | Only crawl same-origin links |
| `url_pattern` | string | No | `""` | Regex pattern to filter URLs (empty = all) |
| `session_id` | string | No | `null` | Active session ID. If omitted, a stateless session is created for this call. |
| `wait_timeout` | integer | No | `30000` | Timeout in ms for wait conditions |
| `headless` | boolean | No | `true` | Run browser in headless mode |
| `backend` | string (cdp, bidi, auto) | No | `"cdp"` | Backend: 'cdp', 'bidi', or 'auto' |

### wavexis_extract

Extract structured data from a page using a CSS selector schema.

Args:
    input: Extraction parameters (url, schema, selector).

Returns:
    JSON string with ``data`` list and ``rows`` count.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `url` | string | Yes | — | URL to navigate to |
| `schema` | object | Yes | — | Mapping of field names to CSS selectors, e.g. {"title": "h1"} |
| `selector` | string | No | `null` | Optional scoping selector for repeating elements |
| `session_id` | string | No | `null` | Active session ID. If omitted, a stateless session is created for this call. |
| `wait_timeout` | integer | No | `30000` | Timeout in ms for wait conditions |
| `headless` | boolean | No | `true` | Run browser in headless mode |
| `backend` | string (cdp, bidi, auto) | No | `"cdp"` | Backend: 'cdp', 'bidi', or 'auto' |

### wavexis_lighthouse

Run a Lighthouse-style audit on a URL.

Args:
    input: Audit parameters (url, categories).

Returns:
    JSON string with ``categories`` dict containing scores per category.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `url` | string | Yes | — | URL to audit |
| `categories` | array | No | — | Categories: 'performance', 'accessibility', 'seo', 'best-practices'. Empty = all. |
| `session_id` | string | No | `null` | Active session ID. If omitted, a stateless session is created for this call. |
| `wait_timeout` | integer | No | `30000` | Timeout in ms for wait conditions |
| `headless` | boolean | No | `true` | Run browser in headless mode |
| `backend` | string (cdp, bidi, auto) | No | `"cdp"` | Backend: 'cdp', 'bidi', or 'auto' |

### wavexis_record

Record browser interactions and generate a YAML workflow.

Delegates to ``wavexis.actions.record.record_events`` to inject a
recording script that captures user interactions (clicks, input,
navigation, scroll, keypress) and then converts the captured events
to a multi-action YAML workflow using
``wavexis.actions.record.events_to_yaml``.

Args:
    input: Recording parameters (url, duration, headless).

Returns:
    JSON string with ``yaml``, ``events_captured``, and ``duration_s``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | No | `null` | Existing session ID to reuse; a new session is created if omitted |
| `url` | string | Yes | — | URL to navigate to for recording |
| `duration` | integer | No | `60` | Recording duration in seconds |
| `headless` | boolean | No | `false` | Must be False for user interaction |
| `backend` | string (cdp, bidi, auto) | No | `"cdp"` | Backend: 'cdp', 'bidi', or 'auto' |

### wavexis_visual_diff

Compare a screenshot against a baseline image.

Args:
    input: Visual diff parameters (url, baseline_path, threshold).

Returns:
    JSON string with ``diff_percentage``, ``diff_pixels``, and ``passed``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `url` | string | Yes | — | URL to navigate to |
| `baseline_path` | string | Yes | — | Path to baseline screenshot file |
| `selector` | string | No | `null` | CSS selector — compare only this element |
| `threshold` | number | No | `0.1` | Pixel difference threshold |
| `output_path` | string | No | `null` | Save diff image to this path |
| `session_id` | string | No | `null` | Active session ID. If omitted, a stateless session is created for this call. |
| `wait_timeout` | integer | No | `30000` | Timeout in ms for wait conditions |
| `headless` | boolean | No | `true` | Run browser in headless mode |
| `backend` | string (cdp, bidi, auto) | No | `"cdp"` | Backend: 'cdp', 'bidi', or 'auto' |

### wavexis_websocket_intercept

Capture WebSocket frames on a page.

Args:
    input: WebSocket intercept parameters (url, duration_ms).

Returns:
    JSON string with ``sent``, ``received``, and frame counts.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `url` | string | Yes | — | URL to navigate to |
| `url_pattern` | string | No | `""` | Regex pattern to filter WS URLs (empty = all) |
| `duration_ms` | integer | No | `5000` | Capture duration in ms |
| `mock_responses` | object | No | — | Map request payloads to mock response payloads |
| `session_id` | string | No | `null` | Active session ID. If omitted, a stateless session is created for this call. |
| `wait_timeout` | integer | No | `30000` | Timeout in ms for wait conditions |
| `headless` | boolean | No | `true` | Run browser in headless mode |
| `backend` | string (cdp, bidi, auto) | No | `"cdp"` | Backend: 'cdp', 'bidi', or 'auto' |
