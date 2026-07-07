# DevTools Tools (31)

Enable with `--caps=devtools`.

DevTools tools expose the Chrome DevTools Protocol as MCP tools. This is the most powerful tier for debugging, performance optimization, and deep browser inspection. Covers performance metrics, CPU profiling, heap snapshots, code coverage, CSS inspection, JavaScript debugging, element highlighting, console capture, security state, and window management.

## Performance

Performance tools measure and record how the page behaves at runtime. Capture Core Web Vitals, CPU profiles, heap snapshots, and code coverage.

| Tool | Parameters | Description |
| --- | --- | --- |
| `wavexis_perf_metrics` | `session_id` | Get performance metrics: LCP, FCP, CLS, TTFB, TBT, DOM nodes, JS heap size. Returns a dict of metric name → value. |
| `wavexis_perf_trace` | `session_id`, `duration`, `categories` | Capture a performance trace. `categories`: list of trace categories (default: all). Returns a trace file that can be opened in Chrome DevTools or perf.html. |
| `wavexis_perf_profile` | `session_id`, `duration` | Capture a CPU profile for `duration` seconds. Returns profile data with function call trees and execution time. |
| `wavexis_perf_heap_snapshot` | `session_id` | Capture a heap snapshot. Returns heap data including object types, sizes, and references. Useful for finding memory leaks. |
| `wavexis_perf_coverage` | `session_id` | Get JavaScript coverage. Returns which functions were executed and which were not. Useful for identifying dead code. |
| `wavexis_perf_css_coverage` | `session_id` | Get CSS coverage. Returns which CSS rules were used. Useful for removing unused CSS. |
| `wavexis_start_combined_trace` | `session_id`, `categories` | Start a combined performance + trace recording. `categories`: list of trace categories. Returns a trace file with both perf metrics and timeline data. |
| `wavexis_stop_combined_trace` | `session_id`, `output_path` | Stop a combined trace recording and save the file. Returns the trace file path and duration. |

!!! example "Check Core Web Vitals"
    ```text
    wavexis_session_open(backend="cdp")
    wavexis_navigate(session_id="abc-123", url="https://example.com", wait_until="networkidle")
    wavexis_perf_metrics(session_id="abc-123")
    → {"lcp": 1200, "fcp": 800, "cls": 0.05, "ttfb": 200, "tbt": 50}
    wavexis_session_close(session_id="abc-123")
    ```

## CSS

CSS tools inspect styles at runtime. Get inline styles, matched CSS rules, computed styles, and list all stylesheets loaded by the page.

| Tool | Parameters | Description |
| --- | --- | --- |
| `wavexis_css_get_styles` | `session_id`, `selector` | Get inline and matched CSS rules for an element. Shows which rules apply and their source (stylesheet, line). |
| `wavexis_css_get_stylesheets` | `session_id` | List all stylesheets loaded by the page. Returns URL, disabled state, and source text length. |
| `wavexis_css_get_rules` | `session_id`, `stylesheet_id` | Get all CSS rules from a specific stylesheet. Requires `stylesheet_id` from `wavexis_css_get_stylesheets`. |
| `wavexis_css_get_computed` | `session_id`, `selector` | Get computed styles for an element. Returns the final resolved values after applying all rules and inheritance. |

## Debugging

JavaScript debugging tools. Set breakpoints, step through code, pause and resume execution, and inspect event listeners.

| Tool | Parameters | Description |
| --- | --- | --- |
| `wavexis_debug_set_breakpoint` | `session_id`, `url`, `line`, `column` | Set a breakpoint at a specific source location. `url`: source file URL. `line`/`column`: 0-indexed position. |
| `wavexis_debug_set_breakpoint_function` | `session_id`, `function_name` | Set a breakpoint by function name. The debugger pauses when the function is called. |
| `wavexis_debug_remove_breakpoint` | `session_id`, `breakpoint_id` | Remove a breakpoint by its ID. |
| `wavexis_debug_step_over` | `session_id` | Step over the next function call. Executes the call without entering it. |
| `wavexis_debug_step_into` | `session_id` | Step into the next function call. Pauses at the first line of the called function. |
| `wavexis_debug_step_out` | `session_id` | Step out of the current function. Runs until the function returns. |
| `wavexis_debug_pause` | `session_id` | Pause JavaScript execution immediately. |
| `wavexis_debug_resume` | `session_id` | Resume JavaScript execution after a pause. |
| `wavexis_debug_get_listeners` | `session_id`, `selector` | Get all event listeners attached to an element. Returns listener type, function, and useCapture flag. |

## Overlay

Overlay tools highlight elements on the page for visual debugging. Useful when the LLM needs to verify which element a selector matches.

| Tool | Parameters | Description |
| --- | --- | --- |
| `wavexis_overlay_highlight` | `session_id`, `selector`, `color`, `show_size` | Highlight an element with a colored border. `color`: CSS color (default: `#ff0000`). `show_size`: display element dimensions. |
| `wavexis_overlay_clear` | `session_id` | Clear all highlights. |

## Console

Capture console output and browser logs. Useful for debugging JavaScript errors and warnings.

| Tool | Parameters | Description |
| --- | --- | --- |
| `wavexis_capture_console` | `session_id`, `level` | Capture console messages. `level`: `log`, `info`, `warning`, `error`, `debug`, or `all` (default). Returns messages with type, text, and stack trace. |
| `wavexis_console_messages` | `session_id`, `level` | Get console messages since session start or last call. `level`: filter by severity. Returns messages with timestamp, type, and text. |
| `wavexis_capture_logs` | `session_id`, `level` | Capture browser-level logs. Includes network errors, SSL warnings, and deprecation notices. |
| `wavexis_browser_logs` | `session_id`, `level` | Get browser-level logs since session start or last call. Similar to `capture_logs` but returns all accumulated logs. |

## Capture

| Tool | Parameters | Description |
| --- | --- | --- |
| `wavexis_annotated_screenshot` | `session_id`, `selectors`, `format`, `output_path` | Take a screenshot with numbered labels (@e1, @e2, ...) overlaid on elements matching the provided selectors. Returns the image plus a label-to-selector map. |

## Security

Inspect and control the browser's security state.

| Tool | Parameters | Description |
| --- | --- | --- |
| `wavexis_get_security_state` | `session_id` | Get the page's security state: scheme (https/http), security level, certificate errors, SSL version. |
| `wavexis_ignore_cert_errors` | `session_id`, `ignore` | Enable or disable certificate error bypass. `ignore=true` allows self-signed certs. Use with caution. |

## Window

Control the browser window's position and size.

| Tool | Parameters | Description |
| --- | --- | --- |
| `wavexis_get_window_bounds` | `session_id` | Get the window's position (left, top) and size (width, height). |
| `wavexis_set_window_bounds` | `session_id`, `left`, `top`, `width`, `height` | Set the window's position and size. All parameters optional — only provided values are changed. |
