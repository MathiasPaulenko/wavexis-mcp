# DevTools Tools (31)

Enable with `--caps=devtools`.

Console messages, performance metrics, CPU throttling, and raw CDP access. Enable with `--caps=devtools`.

## Summary

| Tool | Parameters | Description |
| --- | --- | --- |
| [`wavexis_browser_logs`](#wavexis_browser_logs) | `session_id` | Get browser-level log entries. |
| [`wavexis_console_messages`](#wavexis_console_messages) | `session_id, level?, all?, limit?, offset?` | Get console messages with pagination. |
| [`wavexis_css_get_computed`](#wavexis_css_get_computed) | `selector, session_id` | Get computed styles for an element. |
| [`wavexis_css_get_rules`](#wavexis_css_get_rules) | `stylesheet_id, session_id` | Get CSS rules from a specific stylesheet. |
| [`wavexis_css_get_styles`](#wavexis_css_get_styles) | `selector, session_id` | Get inline and matched CSS styles for an element. |
| [`wavexis_css_get_stylesheets`](#wavexis_css_get_stylesheets) | `session_id` | List all stylesheets loaded by the page. |
| [`wavexis_debug_get_listeners`](#wavexis_debug_get_listeners) | `selector, session_id` | Get event listeners attached to an element. |
| [`wavexis_debug_pause`](#wavexis_debug_pause) | `session_id` | Pause script execution. |
| [`wavexis_debug_remove_breakpoint`](#wavexis_debug_remove_breakpoint) | `session_id, breakpoint_id` | Remove a breakpoint by ID. |
| [`wavexis_debug_resume`](#wavexis_debug_resume) | `session_id` | Resume script execution. |
| [`wavexis_debug_set_breakpoint`](#wavexis_debug_set_breakpoint) | `session_id, url, line, condition?` | Set a breakpoint by URL and line number. |
| [`wavexis_debug_set_breakpoint_function`](#wavexis_debug_set_breakpoint_function) | `session_id, function_name` | Set a breakpoint by function name. |
| [`wavexis_debug_step_into`](#wavexis_debug_step_into) | `session_id` | Step into in the debugger. |
| [`wavexis_debug_step_out`](#wavexis_debug_step_out) | `session_id` | Step out in the debugger. |
| [`wavexis_debug_step_over`](#wavexis_debug_step_over) | `session_id` | Step over in the debugger. |
| [`wavexis_get_security_state`](#wavexis_get_security_state) | `session_id` | Get the page security state. |
| [`wavexis_get_window_bounds`](#wavexis_get_window_bounds) | `session_id` | Get the browser window bounds. |
| [`wavexis_ignore_cert_errors`](#wavexis_ignore_cert_errors) | `session_id, ignore?` | Enable or disable certificate error ignoring. |
| [`wavexis_overlay_clear`](#wavexis_overlay_clear) | `session_id` | Clear all overlay highlights. |
| [`wavexis_overlay_highlight`](#wavexis_overlay_highlight) | `selector, color?, session_id` | Highlight an element with a colored overlay. |
| [`wavexis_perf_coverage`](#wavexis_perf_coverage) | `session_id` | Get JavaScript code coverage. |
| [`wavexis_perf_css_coverage`](#wavexis_perf_css_coverage) | `session_id` | Get CSS code coverage. |
| [`wavexis_perf_heap_snapshot`](#wavexis_perf_heap_snapshot) | `session_id, output_path?` | Capture a heap snapshot. |
| [`wavexis_perf_metrics`](#wavexis_perf_metrics) | `session_id` | Get performance metrics (LCP, FCP, CLS, TTFB, DOMNodes, etc.). |
| [`wavexis_perf_profile`](#wavexis_perf_profile) | `session_id, duration_ms?, output_path?` | Capture a CPU profile. |
| [`wavexis_perf_trace`](#wavexis_perf_trace) | `session_id, duration_ms?, output_path?` | Capture a performance trace. |
| [`wavexis_set_window_bounds`](#wavexis_set_window_bounds) | `session_id, width, height, x?, y?` | Set the browser window bounds. |
| [`wavexis_start_combined_trace`](#wavexis_start_combined_trace) | `session_id, capture_screenshots?, capture_network?, capture_console?` | Start a combined trace capturing screenshots, network, and console (W8). |
| [`wavexis_stop_combined_trace`](#wavexis_stop_combined_trace) | `session_id, trace_id` | Stop a combined trace and return collected data (W8). |
| [`wavexis_subscribe_events`](#wavexis_subscribe_events) | `session_id, event_types` | Subscribe to real-time browser events (W10). |
| [`wavexis_unsubscribe_events`](#wavexis_unsubscribe_events) | `session_id, subscription_id` | Unsubscribe from browser events by subscription ID (W10). |

## DevTools

### wavexis_browser_logs

Get browser-level log entries.

Args:
    input: Session reference parameters.

Returns:
    JSON string with ``logs`` list and ``count``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |

### wavexis_console_messages

Get console messages with pagination.

Args:
    input: Console messages parameters (level, pagination).

Returns:
    JSON string with paginated ``messages``, ``count``, and ``total``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `level` | string | No | `"info"` | Minimum level: error, warning, info, debug |
| `all` | boolean | No | `false` | Return all messages since session start, not just last navigation |
| `limit` | integer | No | `100` | Max messages to return |
| `offset` | integer | No | `0` | Skip first N messages for pagination |

### wavexis_css_get_computed

Get computed styles for an element.

Args:
    input: Computed styles parameters (selector).

Returns:
    JSON string with ``computed`` styles.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `selector` | string | Yes | — | CSS selector for the target element |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |

### wavexis_css_get_rules

Get CSS rules from a specific stylesheet.

Args:
    input: CSS rules parameters (stylesheet_id).

Returns:
    JSON string with ``stylesheet_id``, ``rules``, and ``count``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `stylesheet_id` | string | Yes | — | CSS stylesheet ID |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |

### wavexis_css_get_styles

Get inline and matched CSS styles for an element.

Args:
    input: CSS styles parameters (selector).

Returns:
    JSON string with ``styles`` data.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `selector` | string | Yes | — | CSS selector for the target element |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |

### wavexis_css_get_stylesheets

List all stylesheets loaded by the page.

Args:
    input: Session reference parameters.

Returns:
    JSON string with ``stylesheets`` list and ``count``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |

### wavexis_debug_get_listeners

Get event listeners attached to an element.

Args:
    input: Event listener parameters (selector).

Returns:
    JSON string with ``listeners`` list and ``count``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `selector` | string | Yes | — | CSS selector for the target element |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |

### wavexis_debug_pause

Pause script execution.

Args:
    input: Session reference parameters.

Returns:
    JSON string with status ``"ok"``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |

### wavexis_debug_remove_breakpoint

Remove a breakpoint by ID.

Args:
    input: Breakpoint removal parameters (breakpoint_id).

Returns:
    JSON string with status ``"ok"``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `breakpoint_id` | string | Yes | — | Breakpoint ID to remove |

### wavexis_debug_resume

Resume script execution.

Args:
    input: Session reference parameters.

Returns:
    JSON string with status ``"ok"``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |

### wavexis_debug_set_breakpoint

Set a breakpoint by URL and line number.

Args:
    input: Breakpoint parameters (url, line, condition).

Returns:
    JSON string with ``breakpoint_id``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `url` | string | Yes | — | URL of the script |
| `line` | integer | Yes | — | Line number (0-based) |
| `condition` | string | No | `null` | Optional condition expression |

### wavexis_debug_set_breakpoint_function

Set a breakpoint by function name.

Args:
    input: Breakpoint parameters (function_name).

Returns:
    JSON string with ``breakpoint_id``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `function_name` | string | Yes | — | JavaScript function name to set breakpoint on |

### wavexis_debug_step_into

Step into in the debugger.

Args:
    input: Session reference parameters.

Returns:
    JSON string with status ``"ok"``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |

### wavexis_debug_step_out

Step out in the debugger.

Args:
    input: Session reference parameters.

Returns:
    JSON string with status ``"ok"``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |

### wavexis_debug_step_over

Step over in the debugger.

Args:
    input: Session reference parameters.

Returns:
    JSON string with status ``"ok"``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |

### wavexis_get_security_state

Get the page security state.

Args:
    input: Session reference parameters.

Returns:
    JSON string with ``state`` data.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |

### wavexis_get_window_bounds

Get the browser window bounds.

Args:
    input: Session reference parameters.

Returns:
    JSON string with window bounds (width, height, x, y).

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |

### wavexis_ignore_cert_errors

Enable or disable certificate error ignoring.

Args:
    input: Certificate error parameters (ignore).

Returns:
    JSON string with status ``"ok"`` and ``ignore``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `ignore` | boolean | No | `true` | Whether to ignore cache |

### wavexis_overlay_clear

Clear all overlay highlights.

Args:
    input: Session reference parameters.

Returns:
    JSON string with status ``"ok"``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |

### wavexis_overlay_highlight

Highlight an element with a colored overlay.

Args:
    input: Highlight parameters (selector, color).

Returns:
    JSON string with status ``"ok"`` and ``selector``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `selector` | string | Yes | — | CSS selector for the target element |
| `color` | string | No | `"rgba(255,0,0,0.5)"` | RGBA color string |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |

### wavexis_perf_coverage

Get JavaScript code coverage.

Args:
    input: Session reference parameters.

Returns:
    JSON string with ``coverage`` data and ``scripts`` count.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |

### wavexis_perf_css_coverage

Get CSS code coverage.

Args:
    input: Session reference parameters.

Returns:
    JSON string with ``coverage`` data.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |

### wavexis_perf_heap_snapshot

Capture a heap snapshot.

Args:
    input: Heap snapshot parameters (output_path).

Returns:
    JSON string with ``snapshot`` data or file ``path``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `output_path` | string | No | `null` | File path to save the output. If omitted, a default path is used. |

### wavexis_perf_metrics

Get performance metrics (LCP, FCP, CLS, TTFB, DOMNodes, etc.).

Args:
    input: Session reference parameters.

Returns:
    JSON string with ``metrics`` dict.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |

### wavexis_perf_profile

Capture a CPU profile.

Args:
    input: Profile parameters (duration_ms, output_path).

Returns:
    JSON string with ``profile`` data or file ``path``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `duration_ms` | integer | No | `3000` | Duration in ms |
| `output_path` | string | No | `null` | File path to save the output. If omitted, a default path is used. |

### wavexis_perf_trace

Capture a performance trace.

Args:
    input: Trace parameters (duration_ms, output_path).

Returns:
    JSON string with ``trace`` data or file ``path``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `duration_ms` | integer | No | `3000` | Duration in ms |
| `output_path` | string | No | `null` | File path to save the output. If omitted, a default path is used. |

### wavexis_set_window_bounds

Set the browser window bounds.

Args:
    input: Window bounds parameters (width, height, x, y).

Returns:
    JSON string with status ``"ok"`` and bounds values.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `width` | integer | Yes | — | Viewport width in pixels |
| `height` | integer | Yes | — | Viewport height in pixels |
| `x` | integer | No | `0` | X coordinate |
| `y` | integer | No | `0` | Y coordinate |

### wavexis_start_combined_trace

Start a combined trace capturing screenshots, network, and console (W8).

Args:
    input: Combined trace start parameters.

Returns:
    JSON string with ``trace_id``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `capture_screenshots` | boolean | No | `true` | Capture screenshots during the trace |
| `capture_network` | boolean | No | `true` | Capture network activity during the trace |
| `capture_console` | boolean | No | `true` | Capture console messages during the trace |

### wavexis_stop_combined_trace

Stop a combined trace and return collected data (W8).

Args:
    input: Combined trace stop parameters (trace_id).

Returns:
    JSON string with ``trace`` data including events, screenshots, network, console.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `trace_id` | string | Yes | — | Trace ID from start_combined_trace |

### wavexis_subscribe_events

Subscribe to real-time browser events (W10).

Event types: console, network_request, network_response,
dom_mutation, dialog, navigation.  Events are collected
internally and can be retrieved via console_messages or
network_requests tools while the subscription is active.

Args:
    input: Subscription parameters (event_types).

Returns:
    JSON string with ``subscription_id``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `event_types` | array | Yes | — | Event types: 'console', 'network_request', 'network_response', 'dom_mutation', 'dialog', 'navigation' |

### wavexis_unsubscribe_events

Unsubscribe from browser events by subscription ID (W10).

Args:
    input: Unsubscribe parameters (subscription_id).

Returns:
    JSON string with status ``"ok"``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `subscription_id` | string | Yes | — | Subscription ID from subscribe_events |
