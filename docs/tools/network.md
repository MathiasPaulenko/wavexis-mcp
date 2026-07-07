# Network Tools (9)

Enable with `--caps=network`.

Network tools give you full control over HTTP traffic. Set custom headers, override User-Agent, block requests by URL pattern, throttle network speed, disable cache, capture HAR files, intercept and modify requests in-flight, mock responses, and list all network requests made by the page.

Essential for testing API interactions, simulating slow connections, debugging network issues, and mocking backend responses.

| Tool | Parameters | Description |
| --- | --- | --- |
| `wavexis_set_headers` | `session_id`, `headers` | Set HTTP headers sent on all requests. `headers`: dict of header name → value. Existing headers are merged. |
| `wavexis_set_user_agent` | `session_id`, `user_agent`, `accept_language` | Override the User-Agent string. Optionally set `Accept-Language` header. |
| `wavexis_block_requests` | `session_id`, `patterns` | Block requests matching URL patterns. `patterns`: list of glob strings (e.g., `["*.css", "*google-analytics*"]`). |
| `wavexis_throttle_network` | `session_id`, `preset`, `download`, `upload`, `latency` | Throttle network speed. Presets: `offline`, `gprs`, `slow-2g`, `2g`, `3g`, `4g`, `wifi`. Or set custom `download`/`upload` (bytes/sec) and `latency` (ms). |
| `wavexis_set_cache_disabled` | `session_id`, `disabled` | Disable or re-enable the browser cache. `disabled=true` forces all requests to hit the network. |
| `wavexis_capture_har` | `session_id`, `output_path` | Start capturing a HAR (HTTP Archive) file. Call again to stop and save. HAR files record all network requests with timing, headers, and bodies. |
| `wavexis_intercept_requests` | `session_id`, `enabled` | Enable/disable request interception. When enabled, requests are paused before sending and can be modified with `wavexis_modify_request`. |
| `wavexis_mock_response` | `session_id`, `url_pattern`, `status`, `headers`, `body` | Mock a response for a URL pattern. The browser receives the mocked response without hitting the network. `status`: HTTP status code (default 200). |
| `wavexis_network_requests` | `session_id`, `filter` | List captured network requests. Optional `filter` regex to match URLs. Returns method, URL, status, timing, and resource type. |

!!! example "Throttle to 3G and block analytics"
    ```text
    wavexis_session_open(backend="cdp")
    wavexis_throttle_network(session_id="abc-123", preset="3g")
    wavexis_block_requests(session_id="abc-123", patterns=["*google-analytics*", "*doubleclick*"])
    wavexis_navigate(session_id="abc-123", url="https://example.com")
    wavexis_network_requests(session_id="abc-123")
    wavexis_session_close(session_id="abc-123")
    ```

!!! example "Mock an API response"
    ```text
    wavexis_session_open(backend="cdp")
    wavexis_mock_response(
        session_id="abc-123",
        url_pattern="*/api/users*",
        status=200,
        body='[{"id": 1, "name": "Alice"}]'
    )
    wavexis_navigate(session_id="abc-123", url="https://app.example.com/users")
    wavexis_session_close(session_id="abc-123")
    ```
