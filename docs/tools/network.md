# Network Tools (20)

Enable with `--caps=network`.

These 20 tools are added when the `network` capability tier is enabled.

## Network

| Tool | Parameters | Description |
| --- | --- | --- |
| `wavexis_block_requests` | `patterns, session_id` | Block requests matching URL patterns. |
| `wavexis_capture_har` | `url, session_id?, wait_ms?, filter?, timeout?, headless?, backend?` | Capture HAR (HTTP Archive) data for a page load. |
| `wavexis_get_request_body` | `session_id, request_id` | Get the body of a network request by ID (W3). |
| `wavexis_get_response_body` | `session_id, request_id` | Get the body of a network response by ID (W3). |
| `wavexis_intercept_requests` | `session_id, pattern` | Register a request interception pattern. |
| `wavexis_mock_response` | `session_id, url, status?, content_type?, body?, headers?` | Register a mock response for a URL pattern. |
| `wavexis_modify_request` | `session_id, pattern, modifications?` | Intercept and modify requests matching a pattern in-flight (W6). |
| `wavexis_modify_response` | `session_id, pattern, modifications?` | Intercept and modify responses matching a pattern in-flight. |
| `wavexis_network_clear` | `session_id` | Clear the network event log. |
| `wavexis_network_request` | `session_id, index, part?` | Return full details for a single network request by index. |
| `wavexis_network_requests` | `session_id, filter?, resource_type?, limit?, offset?, mode?` | List network requests since page load with pagination. |
| `wavexis_replay_har` | `har_path, url_filter?, session_id?, url?, headless?, backend?` | Replay network requests from a HAR file (W7). |
| `wavexis_route` | `session_id, pattern, status?, body?, content_type?, headers?, remove_headers?` | Add a network route/mock or header modification rule. |
| `wavexis_route_list` | `session_id` | List all active network routes/mocks. |
| `wavexis_set_cache_disabled` | `session_id, disabled?` | Enable or disable browser cache. |
| `wavexis_set_headers` | `headers, session_id` | Set extra HTTP headers for all subsequent requests. |
| `wavexis_set_network_state` | `session_id, state?` | Override the browser network state to online or offline. |
| `wavexis_set_user_agent` | `user_agent, session_id` | Set a custom User-Agent string for all subsequent requests. |
| `wavexis_throttle_network` | `session_id, preset?, latency_ms?, download_bps?, upload_bps?, offline?` | Throttle network speed to emulate slow connections. |
| `wavexis_unroute` | `session_id, pattern?` | Remove network routes matching a pattern, or all routes. |
