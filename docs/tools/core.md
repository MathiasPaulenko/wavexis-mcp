# Core Tools (42)

Always enabled. No `--caps` flag needed.

Core tools cover the essential browser automation workflow: open a session, navigate, interact with the page, capture output, and close. These 42 tools are always registered regardless of which capability tiers you enable.

## Session management

Sessions are persistent browser instances. Open a session once, chain multiple tool calls, then close it. Each session holds a browser process (Chrome/Edge) and maintains full state (cookies, localStorage, page context) across calls.

| Tool | Parameters | Description |
| --- | --- | --- |
| `wavexis_session_open` | `backend`, `headless`, `user_data_dir` | Open a browser session. Returns `session_id`. Choose `cdp` (default, Chromium-native) or `bidi` (W3C cross-browser). Set `headless=false` to see the browser window. |
| `wavexis_session_close` | `session_id` | Close a session and kill the browser process. Always call this when done to free resources. |
| `wavexis_session_info` | `session_id` | Get session metadata: backend type, created timestamp, current URL, tab count. |
| `wavexis_session_list` | — | List all active sessions with their IDs and metadata. |
| `wavexis_session_cleanup` | — | Close all active sessions. Useful for cleanup after errors or at end of a workflow. |

!!! example "Session lifecycle"
    ```text
    wavexis_session_open(backend="cdp", headless=false)
    → {"session_id": "abc-123"}

    wavexis_session_info(session_id="abc-123")
    → {"session_id": "abc-123", "backend": "cdp", "created_at": "..."}

    wavexis_session_close(session_id="abc-123")
    → {"status": "ok"}
    ```

## Navigation

Control the browser's URL bar. Navigate to pages, go back/forward in history, reload, stop loading, and wait for conditions.

| Tool | Parameters | Description |
| --- | --- | --- |
| `wavexis_navigate` | `session_id`, `url`, `wait_until` | Navigate to a URL. `wait_until` can be `load`, `domcontentloaded`, or `networkidle`. Default: `load`. |
| `wavexis_back` | `session_id` | Go back in browser history. |
| `wavexis_forward` | `session_id` | Go forward in browser history. |
| `wavexis_reload` | `session_id` | Reload the current page. |
| `wavexis_stop` | `session_id` | Stop loading the current page. |
| `wavexis_wait` | `session_id`, `strategy`, `selector`, `url`, `timeout` | Wait for a condition. Strategies: `load`, `selector` (wait for element), `url` (wait for URL match), `timeout` (fixed wait). Default timeout: 30s. |

!!! example "Navigate and wait"
    ```text
    wavexis_navigate(session_id="abc-123", url="https://example.com", wait_until="networkidle")
    wavexis_wait(session_id="abc-123", strategy="selector", selector="#content", timeout=5000)
    ```

## Capture

Capture visual or textual output from the page. Screenshots support full page, specific elements, and device emulation. PDF generation is available for Chromium-based browsers.

| Tool | Parameters | Description |
| --- | --- | --- |
| `wavexis_screenshot` | `session_id`, `url` (stateless), `selector`, `full_page`, `output_path`, `format` | Take a screenshot. Without `selector`, captures viewport. With `selector`, captures specific element. `full_page=true` captures entire scrollable page. `format`: `png` (default) or `jpeg`. Returns base64 or writes to `output_path`. |
| `wavexis_pdf` | `session_id`, `url` (stateless), `output_path`, `format`, `landscape`, `print_background` | Generate PDF. `format`: `A4` (default), `Letter`, `Legal`. `print_background=true` includes background graphics. |
| `wavexis_scrape` | `session_id`, `url` (stateless), `urls`, `selector`, `output_format` | Scrape text or HTML from one or more URLs. `output_format`: `text` or `html`. When `urls` is a list, scrapes all URLs in batch. |
| `wavexis_screencast` | `session_id`, `duration`, `output_path`, `format` | Capture frames over a duration. `format`: `gif` (default) or `webm`. Useful for capturing animations. |

!!! example "Stateless screenshot"
    ```text
    # No session needed — browser launches, captures, closes
    wavexis_screenshot(url="https://example.com", full_page=true)
    → {"data": "iVBORw0KGgo...", "format": "png", "encoding": "base64"}
    ```

!!! example "Session-based element screenshot"
    ```text
    wavexis_session_open(backend="cdp")
    wavexis_navigate(session_id="abc-123", url="https://example.com")
    wavexis_screenshot(session_id="abc-123", selector="#hero", output_path="./hero.png")
    → {"path": "./hero.png", "format": "png", "encoding": "file"}
    wavexis_session_close(session_id="abc-123")
    ```

## JavaScript

| Tool | Parameters | Description |
| --- | --- | --- |
| `wavexis_eval` | `session_id`, `expression`, `return_by_value` | Evaluate a JavaScript expression in the page context. `return_by_value=true` (default) serializes the result as JSON. Set `false` to get a remote object handle. |

!!! example "Get page title"
    ```text
    wavexis_eval(session_id="abc-123", expression="document.title")
    → {"result": "Example Domain"}
    ```

!!! example "Scroll to bottom"
    ```text
    wavexis_eval(session_id="abc-123", expression="window.scrollTo(0, document.body.scrollHeight)")
    → {"result": null}
    ```

## DOM

Read and manipulate the DOM. Query elements by CSS selector, get/set HTML and text, manage attributes, focus elements, and scroll.

| Tool | Parameters | Description |
| --- | --- | --- |
| `wavexis_dom_html` | `session_id`, `selector`, `outer` | Get HTML of an element. `outer=true` includes the element itself; `false` returns only inner HTML. |
| `wavexis_dom_text` | `session_id`, `selector` | Get text content of an element (innerText). |
| `wavexis_dom_query` | `session_id`, `selector`, `all` | Query elements by CSS selector. `all=true` returns all matches; `false` returns first match only. Returns element refs and metadata. |
| `wavexis_dom_set_attr` | `session_id`, `selector`, `name`, `value` | Set an attribute on an element. |
| `wavexis_dom_remove_attr` | `session_id`, `selector`, `name` | Remove an attribute from an element. |
| `wavexis_dom_remove` | `session_id`, `selector` | Remove an element from the DOM. |
| `wavexis_dom_focus` | `session_id`, `selector` | Focus an element. Triggers `focus` event and makes it the active element. |
| `wavexis_dom_scroll` | `session_id`, `selector`, `x`, `y`, `behavior` | Scroll to element (`selector`) or coordinates (`x`, `y`). `behavior`: `smooth` or `instant`. |

!!! example "Query all buttons"
    ```text
    wavexis_dom_query(session_id="abc-123", selector="button", all=true)
    → {"elements": [{"ref": "el-1", "tag": "button", "text": "Submit"}, ...]}
    ```

## Input

Simulate user interactions. Click, type, fill, select, hover, drag, key press, tap, file upload, and checkbox toggle. All input tools auto-wait for the element to be visible and enabled before acting.

| Tool | Parameters | Description |
| --- | --- | --- |
| `wavexis_click` | `session_id`, `selector`, `button`, `click_count`, `delay` | Click an element. `button`: `left` (default), `right`, `middle`. `click_count`: 1 (default) or 2 (double-click). `delay`: ms between mousedown and mouseup. |
| `wavexis_type` | `session_id`, `selector`, `text`, `delay` | Type text character by character. `delay`: ms between keystrokes. Simulates real typing. |
| `wavexis_fill` | `session_id`, `selector`, `value` | Fill an input field. Replaces existing content. Faster than `type` (no per-character delay). |
| `wavexis_fill_form` | `session_id`, `fields` | Fill multiple form fields in one call. `fields`: list of `{selector, value}` objects. |
| `wavexis_select_option` | `session_id`, `selector`, `value` | Select a dropdown option by value. Works with `<select>` elements. |
| `wavexis_hover` | `session_id`, `selector` | Hover over an element. Triggers `mouseenter` and `mouseover` events. |
| `wavexis_key_press` | `session_id`, `key`, `modifiers` | Press a keyboard key. `key`: e.g., `Enter`, `Tab`, `Escape`, `ArrowDown`. `modifiers`: list of `Shift`, `Control`, `Alt`, `Meta`. |
| `wavexis_drag` | `session_id`, `source_selector`, `target_selector` | Drag an element to a target element. Simulates mousedown → mousemove → mouseup. |
| `wavexis_tap` | `session_id`, `selector` | Touch tap an element. Simulates a touch event (for mobile emulation). |
| `wavexis_set_files` | `session_id`, `selector`, `files` | Set file input. `files`: list of file paths. Works with `<input type="file">`. |
| `wavexis_check` | `session_id`, `selector` | Check a checkbox. No-op if already checked. |
| `wavexis_uncheck` | `session_id`, `selector` | Uncheck a checkbox. No-op if already unchecked. |

!!! example "Fill a login form"
    ```text
    wavexis_fill_form(
        session_id="abc-123",
        fields=[
            {"selector": "#email", "value": "user@example.com"},
            {"selector": "#password", "value": "secret123"}
        ]
    )
    wavexis_click(session_id="abc-123", selector="#submit")
    ```

## Cookies

Read and write browser cookies. Cookies are scoped to the current page's domain.

| Tool | Parameters | Description |
| --- | --- | --- |
| `wavexis_cookies_get` | `session_id`, `urls` | Get cookies. Without `urls`, returns all cookies. With `urls`, returns cookies for specific URLs. |
| `wavexis_cookies_set` | `session_id`, `name`, `value`, `url`, `domain`, `path`, `secure`, `http_only`, `same_site` | Set a cookie. Requires at least `name`, `value`, and `url` or `domain`. |
| `wavexis_cookies_delete` | `session_id`, `name`, `url` | Delete a cookie by name. |
| `wavexis_cookies_clear` | `session_id` | Clear all cookies for the current page. |

## Tabs

Manage browser tabs. Each tab is a separate page context. Opening a new tab creates a new page in the same browser instance.

| Tool | Parameters | Description |
| --- | --- | --- |
| `wavexis_tabs_list` | `session_id` | List all open tabs with their IDs, URLs, and titles. |
| `wavexis_tabs_new` | `session_id`, `url` | Open a new tab and navigate to `url`. Returns the new tab ID. |
| `wavexis_tabs_close` | `session_id`, `tab_id` | Close a specific tab by ID. |
| `wavexis_tabs_activate` | `session_id`, `tab_id` | Switch to a specific tab. Subsequent tool calls operate on the activated tab. |

## Utility

| Tool | Parameters | Description |
| --- | --- | --- |
| `wavexis_browser_version` | `session_id` | Get the browser's version string. Useful for compatibility checks. |
| `wavexis_backends` | — | List available backends (`cdp`, `bidi`) and whether they're installed. |
