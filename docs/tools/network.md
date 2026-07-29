# Network Tools (20)

Enable with `--caps=network`.

Network interception, request monitoring, HAR recording, and response mocking. Enable with `--caps=network`.

## Summary

| Tool | Parameters | Description |
| --- | --- | --- |
| [`wavexis_block_requests`](#wavexis_block_requests) | `patterns, session_id` | Block requests matching URL patterns. |
| [`wavexis_capture_har`](#wavexis_capture_har) | `url, session_id?, wait_ms?, filter?, timeout?, path?, headless?, backend?` | Capture HAR (HTTP Archive) data for a page load. |
| [`wavexis_get_request_body`](#wavexis_get_request_body) | `session_id, request_id` | Get the body of a network request by ID (W3). |
| [`wavexis_get_response_body`](#wavexis_get_response_body) | `session_id, request_id` | Get the body of a network response by ID (W3). |
| [`wavexis_intercept_requests`](#wavexis_intercept_requests) | `session_id, pattern` | Register a request interception pattern. |
| [`wavexis_mock_response`](#wavexis_mock_response) | `session_id, url, status?, content_type?, body?, headers?` | Register a mock response for a URL pattern. |
| [`wavexis_modify_request`](#wavexis_modify_request) | `session_id, pattern, modifications?` | Intercept and modify requests matching a pattern in-flight (W6). |
| [`wavexis_modify_response`](#wavexis_modify_response) | `session_id, pattern, modifications?` | Intercept and modify responses matching a pattern in-flight. |
| [`wavexis_network_clear`](#wavexis_network_clear) | `session_id` | Clear the network event log. |
| [`wavexis_network_request`](#wavexis_network_request) | `session_id, index, part?` | Return full details for a single network request by index. |
| [`wavexis_network_requests`](#wavexis_network_requests) | `session_id, filter?, resource_type?, limit?, offset?, mode?` | List network requests since page load with pagination. |
| [`wavexis_replay_har`](#wavexis_replay_har) | `har_path, url_filter?, session_id?, url?, headless?, backend?` | Replay network requests from a HAR file (W7). |
| [`wavexis_route`](#wavexis_route) | `session_id, pattern, status?, body?, content_type?, headers?, remove_headers?` | Add a network route/mock or header modification rule. |
| [`wavexis_route_list`](#wavexis_route_list) | `session_id` | List all active network routes/mocks. |
| [`wavexis_set_cache_disabled`](#wavexis_set_cache_disabled) | `session_id, disabled?` | Enable or disable browser cache. |
| [`wavexis_set_headers`](#wavexis_set_headers) | `headers, session_id` | Set extra HTTP headers for all subsequent requests. |
| [`wavexis_set_network_state`](#wavexis_set_network_state) | `session_id, state?` | Override the browser network state to online or offline. |
| [`wavexis_set_user_agent`](#wavexis_set_user_agent) | `user_agent, session_id` | Set a custom User-Agent string for all subsequent requests. |
| [`wavexis_throttle_network`](#wavexis_throttle_network) | `session_id, preset?, latency_ms?, download_bps?, upload_bps?, offline?` | Throttle network speed to emulate slow connections. |
| [`wavexis_unroute`](#wavexis_unroute) | `session_id, pattern?` | Remove network routes matching a pattern, or all routes. |

## Network

### wavexis_block_requests

Block requests matching URL patterns.

Args:
    input: Block parameters (patterns).

Returns:
    JSON string with status ``"ok"`` and ``blocked_patterns``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `patterns` | array | Yes | — | URL patterns to block (glob-style) |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |

### wavexis_capture_har

Capture HAR (HTTP Archive) data for a page load.

Args:
    input: HAR capture parameters (URL, wait, filter).

Returns:
    JSON string with ``har`` data and ``entries`` count.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `url` | string | Yes | — | URL to navigate to for HAR capture |
| `session_id` | string | No | `null` | Active session ID. If omitted, a stateless session is created for this call. |
| `wait_ms` | integer | No | `3000` | Time to wait in ms |
| `filter` | string | No | `null` | URL filter pattern |
| `timeout` | integer | No | `30000` | Operation timeout in ms |
| `path` | string | No | `null` | Optional file path to write the HAR to |
| `headless` | boolean | No | `true` | Run browser in headless mode |
| `backend` | string (cdp, bidi, auto) | No | `"cdp"` | Backend: 'cdp', 'bidi', or 'auto' |

### wavexis_get_request_body

Get the body of a network request by ID (W3).

Args:
    input: Request body parameters (session_id, request_id).

Returns:
    JSON string with ``body`` or ``error`` if not available.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `request_id` | string | Yes | — | Network request ID |

### wavexis_get_response_body

Get the body of a network response by ID (W3).

Args:
    input: Response body parameters (session_id, request_id).

Returns:
    JSON string with ``body`` or ``error`` if not available.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `request_id` | string | Yes | — | Network request ID |

### wavexis_intercept_requests

Register a request interception pattern.

Args:
    input: Interception parameters.

Returns:
    JSON string with status ``"ok"``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `pattern` | object | Yes | — | Interception pattern (urlPattern, resourceType, etc.) |

### wavexis_mock_response

Register a mock response for a URL pattern.

Args:
    input: Mock response parameters.

Returns:
    JSON string with status ``"ok"``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `url` | string | Yes | — | URL pattern to match |
| `status` | integer | No | `200` | HTTP status code for the mocked response |
| `content_type` | string | No | `"application/json"` | Content-Type header for the mocked response |
| `body` | string | No | `""` | Response body for the mocked response |
| `headers` | object | No | — | Response headers for the mocked response |

### wavexis_modify_request

Intercept and modify requests matching a pattern in-flight (W6).

Args:
    input: Modification parameters (pattern, modifications).

Returns:
    JSON string with status ``"ok"``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `pattern` | object | Yes | — | Interception pattern (urlPattern, resourceType, requestStage) |
| `modifications` | object | No | — | Modifications: headers, url, method, post_data |

### wavexis_modify_response

Intercept and modify responses matching a pattern in-flight.

Args:
    input: Modification parameters (pattern, modifications).

Returns:
    JSON string with status ``"ok"``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `pattern` | object | Yes | — | Interception pattern (urlPattern, resourceType, requestStage) |
| `modifications` | object | No | — | Modifications: status, headers, body |

### wavexis_network_clear

Clear the network event log.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |

### wavexis_network_request

Return full details for a single network request by index.

Use the index from ``wavexis_network_requests`` with ``mode="events"``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `index` | integer | Yes | — | 1-based index from wavexis_network_requests |
| `part` | string (request-headers, request-body, response-headers, response-body) | No | `null` | Return only this part |

### wavexis_network_requests

List network requests since page load with pagination.

Args:
    input: Request listing parameters (filter, pagination, mode).

Returns:
    JSON string with paginated ``requests``, ``count``, and ``total``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `filter` | string | No | `null` | URL filter pattern |
| `resource_type` | string | No | `null` | Filter by type: document, stylesheet, image, etc. |
| `limit` | integer | No | `100` | Max requests to return |
| `offset` | integer | No | `0` | Skip first N requests for pagination |
| `mode` | string (performance, events) | No | `"performance"` | Use performance.getEntriesByType or CDP network event log |

### wavexis_replay_har

Replay network requests from a HAR file (W7).

Args:
    input: HAR replay parameters (har_path, url_filter, url).

Returns:
    JSON string with status ``"ok"``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `har_path` | string | Yes | — | Path to HAR file |
| `url_filter` | string | No | `""` | Optional URL filter pattern |
| `session_id` | string | No | `null` | Active session ID. If omitted, a stateless session is created for this call. |
| `url` | string | No | `""` | URL to navigate to before replay |
| `headless` | boolean | No | `true` | Run browser in headless mode |
| `backend` | string (cdp, bidi, auto) | No | `"cdp"` | Backend: 'cdp', 'bidi', or 'auto' |

### wavexis_route

Add a network route/mock or header modification rule.

If ``status`` or ``body`` is provided, matching requests are fulfilled
with a mocked response. Otherwise the request is continued with the
supplied header changes.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `pattern` | string | Yes | — | URL glob to match (e.g. '**/api/users') |
| `status` | integer | No | `null` | HTTP status code to return |
| `body` | string | No | `null` | Response body for mocked requests |
| `content_type` | string | No | `null` | Content-Type header for mocked response |
| `headers` | array | No | `null` | Headers in "Name: Value" format |
| `remove_headers` | string | No | `null` | Comma-separated header names to remove |

### wavexis_route_list

List all active network routes/mocks.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |

### wavexis_set_cache_disabled

Enable or disable browser cache.

Args:
    input: Cache disable parameters.

Returns:
    JSON string with status ``"ok"`` and ``cache_disabled``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `disabled` | boolean | No | `true` | Whether the network is disabled |

### wavexis_set_headers

Set extra HTTP headers for all subsequent requests.

Args:
    input: Headers parameters.

Returns:
    JSON string with status ``"ok"``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `headers` | object | Yes | — | HTTP headers to set |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |

### wavexis_set_network_state

Override the browser network state to online or offline.

Args:
    input: Network state parameters.

Returns:
    JSON string with status ``"ok"`` and ``"state"``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `state` | string | No | `"online"` | Network state: 'online' or 'offline' |

### wavexis_set_user_agent

Set a custom User-Agent string for all subsequent requests.

Args:
    input: User agent parameters.

Returns:
    JSON string with status ``"ok"``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `user_agent` | string | Yes | — | User-Agent string to set |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |

### wavexis_throttle_network

Throttle network speed to emulate slow connections.

Args:
    input: Throttle parameters (preset or custom values).

Returns:
    JSON string with status ``"ok"``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `preset` | string | No | `null` | Preset: none, 2g, 3g, 4g, offline |
| `latency_ms` | integer | No | `0` | Emulated network latency in ms |
| `download_bps` | integer | No | `-1` | Download throughput in bytes/s (-1 for unlimited) |
| `upload_bps` | integer | No | `-1` | Upload throughput in bytes/s (-1 for unlimited) |
| `offline` | boolean | No | `false` | Set the browser to offline mode |

### wavexis_unroute

Remove network routes matching a pattern, or all routes.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `pattern` | string | No | `null` | Pattern to remove; omit to remove all |
