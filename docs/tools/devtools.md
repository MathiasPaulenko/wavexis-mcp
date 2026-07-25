# DevTools Tools (31)

Enable with `--caps=devtools`.

These 31 tools are added when the `devtools` capability tier is enabled.

## DevTools

| Tool | Parameters | Description |
| --- | --- | --- |
| `wavexis_browser_logs` | `session_id` | Get browser-level log entries. |
| `wavexis_console_messages` | `session_id, level?, all?, limit?, offset?` | Get console messages with pagination. |
| `wavexis_css_get_computed` | `selector, session_id` | Get computed styles for an element. |
| `wavexis_css_get_rules` | `stylesheet_id, session_id` | Get CSS rules from a specific stylesheet. |
| `wavexis_css_get_styles` | `selector, session_id` | Get inline and matched CSS styles for an element. |
| `wavexis_css_get_stylesheets` | `session_id` | List all stylesheets loaded by the page. |
| `wavexis_debug_get_listeners` | `selector, session_id` | Get event listeners attached to an element. |
| `wavexis_debug_pause` | `session_id` | Pause script execution. |
| `wavexis_debug_remove_breakpoint` | `session_id, breakpoint_id` | Remove a breakpoint by ID. |
| `wavexis_debug_resume` | `session_id` | Resume script execution. |
| `wavexis_debug_set_breakpoint` | `session_id, url, line, condition?` | Set a breakpoint by URL and line number. |
| `wavexis_debug_set_breakpoint_function` | `session_id, function_name` | Set a breakpoint by function name. |
| `wavexis_debug_step_into` | `session_id` | Step into in the debugger. |
| `wavexis_debug_step_out` | `session_id` | Step out in the debugger. |
| `wavexis_debug_step_over` | `session_id` | Step over in the debugger. |
| `wavexis_get_security_state` | `session_id` | Get the page security state. |
| `wavexis_get_window_bounds` | `session_id` | Get the browser window bounds. |
| `wavexis_ignore_cert_errors` | `session_id, ignore?` | Enable or disable certificate error ignoring. |
| `wavexis_overlay_clear` | `session_id` | Clear all overlay highlights. |
| `wavexis_overlay_highlight` | `selector, color?, session_id` | Highlight an element with a colored overlay. |
| `wavexis_perf_coverage` | `session_id` | Get JavaScript code coverage. |
| `wavexis_perf_css_coverage` | `session_id` | Get CSS code coverage. |
| `wavexis_perf_heap_snapshot` | `session_id, output_path?` | Capture a heap snapshot. |
| `wavexis_perf_metrics` | `session_id` | Get performance metrics (LCP, FCP, CLS, TTFB, DOMNodes, etc.). |
| `wavexis_perf_profile` | `session_id, duration_ms?, output_path?` | Capture a CPU profile. |
| `wavexis_perf_trace` | `session_id, duration_ms?, output_path?` | Capture a performance trace. |
| `wavexis_set_window_bounds` | `session_id, width, height, x?, y?` | Set the browser window bounds. |
| `wavexis_start_combined_trace` | `session_id, capture_screenshots?, capture_network?, capture_console?` | Start a combined trace capturing screenshots, network, and console (W8). |
| `wavexis_stop_combined_trace` | `session_id, trace_id` | Stop a combined trace and return collected data (W8). |
| `wavexis_subscribe_events` | `session_id, event_types` | Subscribe to real-time browser events (W10). |
| `wavexis_unsubscribe_events` | `session_id, subscription_id` | Unsubscribe from browser events by subscription ID (W10). |
