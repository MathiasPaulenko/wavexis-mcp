# Core Tools (72)

Always enabled. No `--caps` flag needed.

Always enabled — no `--caps` flag needed. Covers the essential browser automation workflow: session management, navigation, screenshots, DOM, JavaScript evaluation, tabs, cookies, and utility tools.

## Summary

| Tool | Parameters | Description |
| --- | --- | --- |
| [`wavexis_act`](#wavexis_act) | `instruction, session_id, max_retries?, value?` | Execute a natural language instruction on the current page (M1). |
| [`wavexis_activate_tab`](#wavexis_activate_tab) | `session_id, tab_id` | Focus (bring to front) a browser tab by its ID. |
| [`wavexis_annotated_screenshot`](#wavexis_annotated_screenshot) | `session_id, selectors, format?, output_path?` | Capture a screenshot with numbered labels overlaid on elements. |
| [`wavexis_back`](#wavexis_back) | `session_id` | Navigate backward one step in the browser history. |
| [`wavexis_backends`](#wavexis_backends) | — | List installed browser backends and their versions without launching a browser. |
| [`wavexis_browser_version`](#wavexis_browser_version) | `session_id?, backend?` | Query the active browser's version string via the selected backend. |
| [`wavexis_check`](#wavexis_check) | `selector, session_id` | Check a checkbox or radio button matching a CSS selector. |
| [`wavexis_click`](#wavexis_click) | `selector, session_id?, url?, button?, click_count?, wait_timeout?, headless?, backend?` | Click an element matching a CSS selector. |
| [`wavexis_close_page`](#wavexis_close_page) | `tab_id?, session_id` | Close a browser page/tab by target id, or the current page if omitted. |
| [`wavexis_close_tab`](#wavexis_close_tab) | `session_id, tab_id` | Close a browser tab by its ID. |
| [`wavexis_console_clear`](#wavexis_console_clear) | `session_id` | Clear all buffered console messages for the session. |
| [`wavexis_cookie_get`](#wavexis_cookie_get) | `name, domain?, path?, session_id` | Retrieve a single cookie by name (and optional domain/path) from the browser. |
| [`wavexis_cookie_list`](#wavexis_cookie_list) | `name?, domain?, path?, limit?, session_id` | List browser cookies with optional name, domain, and path filters. |
| [`wavexis_cookies_clear`](#wavexis_cookies_clear) | `session_id` | Clear all cookies from the browser session. |
| [`wavexis_cookies_delete`](#wavexis_cookies_delete) | `name, domain, session_id?, url?, wait_timeout?, headless?, backend?` | Delete cookies matching a name and domain in the browser. |
| [`wavexis_cookies_get`](#wavexis_cookies_get) | `session_id?, url?, wait_timeout?, headless?, backend?` | Retrieve all cookies for the current page context. |
| [`wavexis_cookies_set`](#wavexis_cookies_set) | `name, value, domain, path?, secure?, http_only?, same_site?, session_id?, url?, wait_timeout?, headless?, backend?` | Set a single cookie in the browser for the current page. |
| [`wavexis_dom_focus`](#wavexis_dom_focus) | `selector, session_id` | Focus an element matching a CSS selector. |
| [`wavexis_dom_get`](#wavexis_dom_get) | `selector, session_id?, url?, outer?, wait_timeout?, headless?, backend?` | Retrieve the HTML of an element matching a CSS selector. |
| [`wavexis_dom_get_attr`](#wavexis_dom_get_attr) | `selector, name, session_id` | Read an attribute value from an element matching a CSS selector. |
| [`wavexis_dom_query`](#wavexis_dom_query) | `selector, session_id?, url?, all?, limit?, offset?, wait_timeout?, headless?, backend?` | Query elements by CSS selector and return paginated metadata. |
| [`wavexis_dom_remove`](#wavexis_dom_remove) | `selector, session_id` | Remove an element matching a CSS selector from the DOM. |
| [`wavexis_dom_remove_attr`](#wavexis_dom_remove_attr) | `selector, name, session_id` | Remove an attribute from an element matching a CSS selector. |
| [`wavexis_dom_scroll`](#wavexis_dom_scroll) | `session_id, selector?, x?, y?` | Scroll to an element or by a pixel offset. |
| [`wavexis_dom_set_attr`](#wavexis_dom_set_attr) | `selector, name, value, session_id` | Set an attribute on an element matching a CSS selector. |
| [`wavexis_dom_snapshot`](#wavexis_dom_snapshot) | `session_id` | Capture a full DOM snapshot of the page including iframes and shadow roots. |
| [`wavexis_double_click`](#wavexis_double_click) | `selector, session_id?, url?, auto_wait?, wait_timeout?, headless?, backend?` | Double-click an element matching a CSS selector. |
| [`wavexis_drag`](#wavexis_drag) | `source, target, session_id?, url?, wait_timeout?, headless?, backend?` | Drag an element from a source selector to a target selector. |
| [`wavexis_drop`](#wavexis_drop) | `selector, data?, paths?, session_id?, url?, wait_timeout?, headless?, backend?` | Drop files or MIME-typed data onto an element via drag events. |
| [`wavexis_eval`](#wavexis_eval) | `expression, session_id?, url?, await_promise?, wait_timeout?, headless?, backend?` | Evaluate a JavaScript expression in the browser context and return the result. |
| [`wavexis_fill`](#wavexis_fill) | `selector, value, session_id?, url?, wait_timeout?, headless?, backend?` | Fill an input element with a value, replacing existing content. |
| [`wavexis_fill_form`](#wavexis_fill_form) | `fields, session_id?, url?, wait_timeout?, headless?, backend?` | Fill multiple form fields in one call (convenience composite tool). |
| [`wavexis_find`](#wavexis_find) | `text, limit?, session_id` | Search the accessibility snapshot for nodes matching text or a regex pattern. |
| [`wavexis_find_by_text`](#wavexis_find_by_text) | `query, all?, session_id` | Find element selector(s) by visible text content without interacting. |
| [`wavexis_forward`](#wavexis_forward) | `session_id` | Navigate forward one step in the browser history. |
| [`wavexis_get_config`](#wavexis_get_config) | — | Return wavexis-mcp server configuration and available browser backends. |
| [`wavexis_hover`](#wavexis_hover) | `selector, session_id?, url?, wait_timeout?, headless?, backend?` | Hover over an element matching a CSS selector. |
| [`wavexis_iframe_click`](#wavexis_iframe_click) | `session_id, iframe_selector, selector` | Click an element inside an iframe. |
| [`wavexis_iframe_eval`](#wavexis_iframe_eval) | `session_id, iframe_selector, expression, await_promise?` | Evaluate a JavaScript expression inside an iframe. |
| [`wavexis_iframe_fill`](#wavexis_iframe_fill) | `session_id, iframe_selector, selector, value` | Fill an input element inside an iframe with a value. |
| [`wavexis_invoke`](#wavexis_invoke) | `method, params?, session_id?, url?, output_path?, backend?, headless?, width?, height?, user_agent?, extra_headers?, proxy?, timeout?, user_data_dir?, browser_url?, remote_url?, stealth?, browser?, wait_strategy?, wait_selector?, wait_timeout?` | Invoke any wavexis backend method by name, the ultimate escape hatch. |
| [`wavexis_key_down`](#wavexis_key_down) | `key, code?, alt?, ctrl?, meta?, shift?, session_id` | Dispatch a raw keyDown event to the active page via CDP. |
| [`wavexis_key_press`](#wavexis_key_press) | `key, session_id` | Press a single keyboard key on the focused element. |
| [`wavexis_key_up`](#wavexis_key_up) | `key, code?, alt?, ctrl?, meta?, shift?, session_id` | Dispatch a raw keyUp event to the active page via CDP. |
| [`wavexis_list_tabs`](#wavexis_list_tabs) | `session_id` | List all open browser tabs in the session. |
| [`wavexis_mouse_drag_xy`](#wavexis_mouse_drag_xy) | `start_x, start_y, end_x, end_y, button?, steps?, session_id` | Drag the mouse from one screen coordinate to another via CDP mouse events. |
| [`wavexis_navigate`](#wavexis_navigate) | `url, session_id?, wait_strategy?, wait_selector?, wait_url_pattern?, wait_timeout?, headless?, backend?` | Navigate the browser to a URL with a configurable wait strategy. |
| [`wavexis_new_tab`](#wavexis_new_tab) | `session_id, url?` | Create a new browser tab, optionally navigating to a URL. |
| [`wavexis_nl_click`](#wavexis_nl_click) | `query, auto_wait?, session_id` | Click an element described in natural language. |
| [`wavexis_nl_fill`](#wavexis_nl_fill) | `query, value, auto_wait?, session_id` | Fill an element described in natural language with a value. |
| [`wavexis_page_pdf`](#wavexis_page_pdf) | `url?, session_id?, landscape?, display_header_footer?, print_background?, scale?, paper_width?, paper_height?, margin_top?, margin_bottom?, margin_left?, margin_right?, output_path?, wait_timeout?, headless?, backend?` | Generate a PDF via the low-level Page.printToPDF CDP method. |
| [`wavexis_page_snapshot`](#wavexis_page_snapshot) | `url?, session_id?, format?, output_path?, wait_timeout?, headless?, backend?` | Capture the page as MHTML or a plain text document. |
| [`wavexis_pdf`](#wavexis_pdf) | `url?, session_id?, paper?, landscape?, margin?, no_header_footer?, media?, js?, output_path?, wait_timeout?, headless?, backend?` | Generate a PDF document from a web page. |
| [`wavexis_press_keys`](#wavexis_press_keys) | `text, delay?, session_id` | Type a sequence of characters at the page level without targeting an element. |
| [`wavexis_reload`](#wavexis_reload) | `session_id, ignore_cache?` | Reload the current page, optionally bypassing the cache. |
| [`wavexis_right_click`](#wavexis_right_click) | `selector, session_id?, url?, auto_wait?, wait_timeout?, headless?, backend?` | Right-click an element matching a CSS selector. |
| [`wavexis_scrape`](#wavexis_scrape) | `urls, session_id?, expression?, output_format?, selector?, wait_timeout?, headless?, backend?, limit?, offset?` | Scrape data from multiple URLs by evaluating a JS expression on each. |
| [`wavexis_screencast`](#wavexis_screencast) | `url?, session_id?, format?, quality?, max_width?, max_height?, duration?, interval?, output_dir?, wait_timeout?, headless?, backend?` | Capture a frame-by-frame screenshot sequence over a duration. |
| [`wavexis_screenshot`](#wavexis_screenshot) | `url?, session_id?, full_page?, format?, quality?, selector?, js?, device?, output_path?, wait_strategy?, wait_selector?, wait_timeout?, headless?, width?, height?, backend?` | Capture a screenshot of a web page or matched element. |
| [`wavexis_select_option`](#wavexis_select_option) | `selector, value, session_id?, url?, wait_timeout?, headless?, backend?` | Select an option in a ``<select>`` element by value. |
| [`wavexis_session_close`](#wavexis_session_close) | `session_id` | Close a browser session and release all associated resources. |
| [`wavexis_session_info`](#wavexis_session_info) | `session_id` | Query metadata and current URL of an active browser session. |
| [`wavexis_session_open`](#wavexis_session_open) | `backend?, headless?, width?, height?, user_agent?, extra_headers?, proxy?, timeout?, user_data_dir?, browser_url?, remote_url?, stealth?, browser?, connect_existing?` | Launch a persistent browser session for multi-step workflows. |
| [`wavexis_set_files`](#wavexis_set_files) | `selector, files, session_id?, url?, wait_timeout?, headless?, backend?` | Upload files to a file input element (``<input type="file">``). |
| [`wavexis_shadow_click`](#wavexis_shadow_click) | `session_id, selectors` | Click an element inside a shadow DOM tree. |
| [`wavexis_shadow_eval`](#wavexis_shadow_eval) | `session_id, selectors, expression, await_promise?` | Evaluate a JavaScript expression inside a shadow DOM tree. |
| [`wavexis_shadow_fill`](#wavexis_shadow_fill) | `session_id, selectors, value` | Fill an input element inside a shadow DOM tree with a value. |
| [`wavexis_stop`](#wavexis_stop) | `session_id` | Stop all pending navigations and resource loads in the session. |
| [`wavexis_tap`](#wavexis_tap) | `selector, session_id?, url?, wait_timeout?, headless?, backend?` | Tap an element matching a CSS selector (touch-emulated click). |
| [`wavexis_type`](#wavexis_type) | `selector, text, session_id?, url?, delay?, wait_timeout?, headless?, backend?` | Type text into an element character by character with optional delay. |
| [`wavexis_uncheck`](#wavexis_uncheck) | `selector, session_id` | Uncheck a checkbox matching a CSS selector by clicking it. |
| [`wavexis_wait`](#wavexis_wait) | `session_id, strategy?, selector?, url_pattern?, timeout?` | Block until a page condition (load, selector, URL, network idle) is met. |

## Natural Language Interaction

### wavexis_act

Execute a natural language instruction on the current page (M1).

Takes an a11y snapshot, matches the instruction to an element,
and performs the detected action (click, type, fill, hover).

Args:
    input: Act parameters (instruction, session_id, max_retries).

Returns:
    JSON string with ``action``, ``element``, ``score``, ``status``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `instruction` | string | Yes | — | Natural language instruction (e.g. 'click the login button') |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `max_retries` | integer | No | `3` | Maximum number of retry attempts |
| `value` | string | No | `null` | Explicit text value for type/fill actions (overrides auto-extraction) |

## Tabs

### wavexis_activate_tab

Focus (bring to front) a browser tab by its ID.

Use to switch the active tab before running navigation or interaction
tools; use wavexis_list_tabs to obtain tab IDs first.

Side effects: Changes the browser's active tab; subsequent tool calls
operate on the newly focused tab.
Returns: JSON string with keys: 'status' ('ok'/'error').

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `tab_id` | string | Yes | — | Tab ID to operate on |

### wavexis_close_tab

Close a browser tab by its ID.

Use to clean up tabs created with wavexis_new_tab; use
wavexis_session_close to terminate the entire session instead.

Side effects: Closes the specified tab and discards its page state.
Destructive — unsaved data in that tab is lost.
Returns: JSON string with keys: 'status' ('ok'/'error').

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `tab_id` | string | Yes | — | Tab ID to operate on |

### wavexis_list_tabs

List all open browser tabs in the session.

Use to discover tab IDs before calling wavexis_activate_tab or
wavexis_close_tab; use wavexis_session_info for session-level metadata
instead.

Side effects: None — read-only query of the browser's tab list.
Returns: JSON string with keys: 'status' ('ok'/'error'),
'tabs' (list[dict]), 'count' (int).

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |

### wavexis_new_tab

Create a new browser tab, optionally navigating to a URL.

Use to open a parallel page without losing the current tab; use
wavexis_navigate to change the current tab's URL instead.

Side effects: Opens a new browser tab; if a URL is provided, issues a
network request to it.
Returns: JSON string with keys: 'status' ('ok'/'error'),
'tab_id' (str), 'url' (str).

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `url` | string | No | `"about:blank"` | URL for the new tab |

## Screenshot / PDF / Capture

### wavexis_annotated_screenshot

Capture a screenshot with numbered labels overlaid on elements.

Injects overlay divs with labels @e1, @e2, ... on each element
matching the provided selectors, captures a screenshot, removes
the overlays, and returns the image plus a label-to-selector map.

Use ``wavexis_screenshot`` for plain captures, or this tool when
visual element identification is needed for follow-up actions.

Side effects: uses an existing session backend, injects and removes
temporary overlay DOM nodes; writes to ``output_path`` when given.
Returns: JSON string with keys: 'status' ('ok'/'error'), 'format'
(str), 'base64' (str) or 'path' (str), 'size_bytes' (int), 'labels'
(dict[str, str]).

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `selectors` | array | Yes | — | CSS selectors to annotate with labels |
| `format` | string | No | `"png"` | Image format: 'png' or 'jpeg' |
| `output_path` | string | No | `null` | File path to save the output. If omitted, a default path is used. |

### wavexis_page_pdf

Generate a PDF via the low-level Page.printToPDF CDP method.

Offers pixel-level control over paper size, margins, and print
options beyond ``wavexis_pdf``. Use ``wavexis_pdf`` for simpler
high-level PDF generation.

Side effects: launches/acquires a browser backend, navigates to ``url``
if provided; writes to ``output_path`` when given.
Returns: JSON string with keys: 'status' ('ok'/'error'), 'type'
('pdf'), 'base64' (str) or 'path' (str), 'size_bytes' (int).

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `url` | string | No | `null` | URL to navigate to (required without session_id) |
| `session_id` | string | No | `null` | Active session ID. If omitted, a stateless session is created for this call. |
| `landscape` | boolean | No | `false` | Use landscape orientation |
| `display_header_footer` | boolean | No | `false` | Include header and footer in PDF |
| `print_background` | boolean | No | `false` | Print background graphics in PDF |
| `scale` | number | No | `1.0` | Scale factor for PDF rendering |
| `paper_width` | number | No | `8.5` | Paper width in inches |
| `paper_height` | number | No | `11.0` | Paper height in inches |
| `margin_top` | number | No | `0.4` | Top margin in inches |
| `margin_bottom` | number | No | `0.4` | Bottom margin in inches |
| `margin_left` | number | No | `0.4` | Left margin in inches |
| `margin_right` | number | No | `0.4` | Right margin in inches |
| `output_path` | string | No | `null` | Path to save the decoded PDF bytes |
| `wait_timeout` | integer | No | `30000` | Timeout in ms for wait conditions |
| `headless` | boolean | No | `true` | Run browser in headless mode |
| `backend` | string (cdp, bidi, auto) | No | `"cdp"` | Backend: 'cdp', 'bidi', or 'auto' |

### wavexis_page_snapshot

Capture the page as MHTML or a plain text document.

Use ``wavexis_scrape`` for structured data extraction, or this tool
when a full page archive (MHTML) or text dump is required.

Side effects: launches/acquires a browser backend, navigates to ``url``
if provided; writes to ``output_path`` when given.
Returns: JSON string with keys: 'status' ('ok'/'error'), 'format'
(str), 'content' (str) or 'path' (str), 'size_bytes' (int).

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `url` | string | No | `null` | URL to navigate to (required without session_id) |
| `session_id` | string | No | `null` | Active session ID. If omitted, a stateless session is created for this call. |
| `format` | string (mhtml, text) | No | `"mhtml"` | Output format: 'mhtml' or 'text' |
| `output_path` | string | No | `null` | File path to save the output. If omitted, a default path is used. |
| `wait_timeout` | integer | No | `30000` | Timeout in ms for wait conditions |
| `headless` | boolean | No | `true` | Run browser in headless mode |
| `backend` | string (cdp, bidi, auto) | No | `"cdp"` | Backend: 'cdp', 'bidi', or 'auto' |

### wavexis_pdf

Generate a PDF document from a web page.

Use ``wavexis_screenshot`` for image capture, or ``wavexis_page_pdf``
when pixel-level control over paper size and margins is required.

Side effects: launches/acquires a browser backend, navigates to ``url``
if provided, optionally evaluates ``js``; writes to ``output_path`` when
given.
Returns: JSON string with keys: 'status' ('ok'/'error'), 'base64'
(str) or 'path' (str), 'size_bytes' (int).

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `url` | string | No | `null` | URL to navigate to (required without session_id) |
| `session_id` | string | No | `null` | Active session ID. If omitted, a stateless session is created for this call. |
| `paper` | string (a4, letter, legal, a3, a5) | No | `"letter"` | Paper size: a4, letter, legal, a3, a5 |
| `landscape` | boolean | No | `false` | Use landscape orientation |
| `margin` | string | No | `"0.4in"` | Page margin (e.g. '0.4in') |
| `no_header_footer` | boolean | No | `false` | Exclude header and footer from PDF |
| `media` | string (print, screen) | No | `"print"` | CSS media: 'print' or 'screen' |
| `js` | string | No | `null` | JavaScript to execute before the action |
| `output_path` | string | No | `null` | File path to save the output. If omitted, a default path is used. |
| `wait_timeout` | integer | No | `30000` | Timeout in ms for wait conditions |
| `headless` | boolean | No | `true` | Run browser in headless mode |
| `backend` | string (cdp, bidi, auto) | No | `"cdp"` | Backend: 'cdp', 'bidi', or 'auto' |

### wavexis_scrape

Scrape data from multiple URLs by evaluating a JS expression on each.

Use ``wavexis_eval`` for single-page evaluation, or ``wavexis_scrape``
when the same expression must run across many pages with pagination.

Side effects: launches/acquires a browser backend, navigates to each
URL in ``urls`` sequentially, evaluates ``expression`` in every page
context.
Returns: JSON string with keys: 'status' ('ok'/'error'), 'results'
(list[dict[str, Any]]), 'format' (str), 'count' (int), 'total' (int).

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `urls` | array | Yes | — | URLs to scrape |
| `session_id` | string | No | `null` | Active session ID. If omitted, a stateless session is created for this call. |
| `expression` | string | No | `"document.title"` | JS expression to evaluate on each page |
| `output_format` | string (json, csv) | No | `"json"` | Output format: 'json' or 'csv' |
| `selector` | string | No | `null` | CSS selector to wait for |
| `wait_timeout` | integer | No | `30000` | Timeout in ms for wait conditions |
| `headless` | boolean | No | `true` | Run browser in headless mode |
| `backend` | string (cdp, bidi, auto) | No | `"cdp"` | Backend: 'cdp', 'bidi', or 'auto' |
| `limit` | integer | No | `50` | Max results to return |
| `offset` | integer | No | `0` | Skip first N results for pagination |

### wavexis_screencast

Capture a frame-by-frame screenshot sequence over a duration.

Use ``wavexis_screenshot`` for a single still image, or
``wavexis_screencast`` when animation or time-series capture is needed.

Side effects: launches/acquires a browser backend, navigates to ``url``
if provided, captures frames for ``duration``; writes frame files to
``output_dir`` when given.
Returns: JSON string with keys: 'status' ('ok'/'error'), 'frames'
(list[str]) or 'dir' (str), 'count' (int).

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `url` | string | No | `null` | URL to navigate to (required without session_id) |
| `session_id` | string | No | `null` | Active session ID. If omitted, a stateless session is created for this call. |
| `format` | string (png, jpeg) | No | `"png"` | Image format: 'png' or 'jpeg' |
| `quality` | integer | No | `80` | JPEG quality 1-100 (ignored for PNG) |
| `max_width` | integer | No | `1280` | Maximum screenshot width in pixels |
| `max_height` | integer | No | `800` | Maximum screenshot height in pixels |
| `duration` | number | No | `5.0` | Capture duration in seconds |
| `interval` | number | No | `1.0` | Seconds between frames |
| `output_dir` | string | No | `null` | Save frames to directory |
| `wait_timeout` | integer | No | `30000` | Timeout in ms for wait conditions |
| `headless` | boolean | No | `true` | Run browser in headless mode |
| `backend` | string (cdp, bidi, auto) | No | `"cdp"` | Backend: 'cdp', 'bidi', or 'auto' |

### wavexis_screenshot

Capture a screenshot of a web page or matched element.

Use ``wavexis_pdf`` when a print-ready document is needed, or
``wavexis_annotated_screenshot`` when labelled element markers are
required.

Side effects: launches/acquires a browser backend, navigates to ``url``
if provided, optionally evaluates ``js``; writes to ``output_path`` when
given.
Returns: JSON string with keys: 'status' ('ok'/'error'), 'format'
(str), 'base64' (str) or 'path' (str), 'size_bytes' (int).

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `url` | string | No | `null` | URL to navigate to (required without session_id) |
| `session_id` | string | No | `null` | Active session ID. If omitted, a stateless session is created for this call. |
| `full_page` | boolean | No | `true` | Capture full scrollable page |
| `format` | string (png, jpeg) | No | `"png"` | Image format: 'png' or 'jpeg' |
| `quality` | integer | No | `80` | JPEG quality (ignored for PNG) |
| `selector` | string | No | `null` | CSS selector — screenshot only this element |
| `js` | string | No | `null` | JavaScript to execute before screenshot |
| `device` | string | No | `null` | Device preset name (e.g. 'iphone-15') |
| `output_path` | string | No | `null` | Save to file instead of returning base64 |
| `wait_strategy` | string (load, domcontentloaded, networkidle, selector, url, none) | No | `"load"` | Wait strategy: load, domcontentloaded, networkidle, selector, url, none |
| `wait_selector` | string | No | `null` | CSS selector to wait for (used when wait_strategy='selector') |
| `wait_timeout` | integer | No | `30000` | Timeout in ms for wait conditions |
| `headless` | boolean | No | `true` | Run browser in headless mode |
| `width` | integer | No | `1280` | Viewport width in pixels |
| `height` | integer | No | `800` | Viewport height in pixels |
| `backend` | string (cdp, bidi, auto) | No | `"cdp"` | Backend: 'cdp', 'bidi', or 'auto' |

## Navigation

### wavexis_back

Navigate backward one step in the browser history.

Use for history navigation instead of wavexis_navigate when the target
is the previous page.

Side effects: Changes the active page to the previous history entry;
may trigger network requests if that page was not cached.
Returns: JSON string with keys: 'status' ('ok'/'error').

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID |

### wavexis_forward

Navigate forward one step in the browser history.

Use after wavexis_back to restore a page; use wavexis_navigate for
direct URL navigation instead.

Side effects: Changes the active page to the next history entry; may
trigger network requests if that page was not cached.
Returns: JSON string with keys: 'status' ('ok'/'error').

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID |

### wavexis_navigate

Navigate the browser to a URL with a configurable wait strategy.

Use for direct URL navigation; use wavexis_back/wavexis_forward for
history navigation, or wavexis_act for natural-language interaction
instead.

Side effects: Issues a network request to the target URL and replaces
the current page content; may auto-create a stateless session if
session_id is omitted.
Returns: JSON string with keys: 'status' ('ok'/'error'), 'url' (str).

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `url` | string | Yes | — | URL to navigate to |
| `session_id` | string | No | `null` | Active session ID. If omitted, a stateless session is created for this call. |
| `wait_strategy` | string (load, domcontentloaded, networkidle, selector, url, none) | No | `"load"` | Wait strategy: load, domcontentloaded, networkidle, selector, url, none |
| `wait_selector` | string | No | `null` | CSS selector to wait for (used when wait_strategy='selector') |
| `wait_url_pattern` | string | No | `null` | URL pattern to wait for (used when wait_strategy='url') |
| `wait_timeout` | integer | No | `30000` | Timeout in ms for wait conditions |
| `headless` | boolean | No | `true` | Run browser in headless mode |
| `backend` | string (cdp, bidi, auto) | No | `"cdp"` | Backend: 'cdp', 'bidi', or 'auto' |

### wavexis_reload

Reload the current page, optionally bypassing the cache.

Use to refresh stale content or retry a failed load; use
wavexis_navigate to go to a different URL instead.

Side effects: Re-issues network requests for the current page and its
resources; discards in-memory page state.
Returns: JSON string with keys: 'status' ('ok'/'error').

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `ignore_cache` | boolean | No | `false` | Bypass cache on reload |

### wavexis_stop

Stop all pending navigations and resource loads in the session.

Use when a page load is hanging or no longer needed; use wavexis_wait
to wait for a load to complete instead.

Side effects: Aborts in-flight network requests and pending
navigations; the page is left in its current partial state.
Returns: JSON string with keys: 'status' ('ok'/'error').

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID |

### wavexis_wait

Block until a page condition (load, selector, URL, network idle) is met.

Use after wavexis_navigate when the wait strategy was 'none', or to
wait for dynamic content; use wavexis_stop to cancel a load instead.

Side effects: None — read-only polling with no page mutations; blocks
the tool call up to the configured timeout.
Returns: JSON string with keys: 'status' ('ok'/'error'),
'elapsed_ms' (int).

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `strategy` | string (load, domcontentloaded, networkidle, selector, url, none) | No | `"load"` | load, domcontentloaded, networkidle, selector, url, none |
| `selector` | string | No | `null` | CSS selector to target an element |
| `url_pattern` | string | No | `null` | URL pattern to wait for (used when strategy='url') |
| `timeout` | integer | No | `30000` | Operation timeout in ms |

## Utility

### wavexis_backends

List installed browser backends and their versions without launching a browser.

Use ``wavexis_browser_version`` instead when you need the version of a
specific running session's backend.

Side effects: None; queries the local filesystem only.
Returns: JSON string with keys: 'status' ('ok'/'error'),
'backends' (dict), 'available' (list[str]).

**Parameters:**

_This tool takes no parameters._

### wavexis_browser_version

Query the active browser's version string via the selected backend.

Use ``wavexis_backends`` instead when you need a list of all installed
backends without launching a browser.

Side effects: Acquires (and may launch) a browser backend, then releases it.
Returns: JSON string with keys: 'status' ('ok'/'error'), 'version' (str), 'backend' (str).

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | No | `null` | Active session ID. If omitted, a stateless session is created for this call. |
| `backend` | string (cdp, bidi, auto) | No | `"cdp"` | Backend: 'cdp', 'bidi', or 'auto' |

### wavexis_invoke

Invoke any wavexis backend method by name, the ultimate escape hatch.

Use a dedicated MCP tool (e.g. ``wavexis_act``, ``wavexis_navigate``)
instead when one exists for the desired action; this tool exposes the
full ``AbstractBackend`` API (e.g. ``page_print_to_pdf``, ``perf_trace``,
``runtime_evaluate``, ``pwa_install``) for methods without a wrapper.

Side effects: May launch an ephemeral browser, navigate to a URL, and
execute arbitrary backend methods; potentially destructive.
Returns: JSON string with keys: 'status' ('ok'/'error'), 'type' (str),
and either 'result' (any), 'base64' (str), or 'path' (str) depending on output.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `method` | string | Yes | — | Backend method name (snake_case), e.g. 'page_print_to_pdf' or 'runtime_evaluate'. |
| `params` | object | No | — | Keyword arguments for the method. For methods that expect a single dataclass parameter (e.g. 'pdf'), pass the datacla... |
| `session_id` | string | No | `null` | Existing session ID. If omitted, an ephemeral browser is launched and closed automatically. |
| `url` | string | No | `null` | URL to navigate to before invoking the method. |
| `output_path` | string | No | `null` | If the method returns bytes, save to this path instead of base64. |
| `backend` | string | No | `"cdp"` | Backend type for ephemeral sessions: 'cdp', 'bidi', or 'auto'. |
| `headless` | boolean | No | `true` | Run browser in headless mode |
| `width` | integer | No | `1280` | Viewport width in pixels |
| `height` | integer | No | `800` | Viewport height in pixels |
| `user_agent` | string | No | `null` | Custom User-Agent string |
| `extra_headers` | object | No | — | Extra HTTP headers to send |
| `proxy` | string | No | `null` | Proxy server URL (e.g. http://host:port) |
| `timeout` | integer | No | `30000` | Operation timeout in ms |
| `user_data_dir` | string | No | `null` | Persistent Chrome user data directory |
| `browser_url` | string | No | `null` | WebSocket URL of an existing browser (e.g. ws://localhost:9222) |
| `remote_url` | string | No | `null` | Cloud browser WebSocket URL |
| `stealth` | boolean | No | `false` | Enable anti-bot stealth mode |
| `browser` | string (chrome, firefox) | No | `"chrome"` | Browser engine for BiDi backend: 'chrome' or 'firefox'. |
| `wait_strategy` | string (load, domcontentloaded, networkidle, selector, url, none) | No | `"load"` | Wait strategy: load, domcontentloaded, networkidle, selector, url, none |
| `wait_selector` | string | No | `null` | CSS selector to wait for (used when wait_strategy='selector') |
| `wait_timeout` | integer | No | `30000` | Timeout in ms for wait conditions |

## Input

### wavexis_check

Check a checkbox or radio button matching a CSS selector.

Use wavexis_uncheck to uncheck a checkbox or wavexis_click for generic
element activation.

Side effects: Clicks the target checkbox/radio, toggling its checked
state and firing change events.
Returns: JSON string with keys: 'status' ('ok'/'error'), 'checked'
(bool, the element's checked state after the action). On error also
'error', 'tool', 'type', 'message', 'suggestion' (all str).

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `selector` | string | Yes | — | CSS selector for checkbox/radio |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |

### wavexis_click

Click an element matching a CSS selector.

Use wavexis_double_click for double clicks, wavexis_right_click for
context menus, or wavexis_nl_click when you only have a text description.

Side effects: Triggers a click event on the target element, which may
submit forms, toggle controls, or navigate the page.
Returns: JSON string with keys: 'status' ('ok'/'error'). On error also
'error', 'tool', 'type', 'message', 'suggestion' (all str).

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `selector` | string | Yes | — | CSS selector for element to click |
| `session_id` | string | No | `null` | Active session ID. If omitted, a stateless session is created for this call. |
| `url` | string | No | `null` | URL to navigate to (required without session_id) |
| `button` | string (left, right, middle) | No | `"left"` | left, right, middle |
| `click_count` | integer | No | `1` | Number of clicks to perform |
| `wait_timeout` | integer | No | `30000` | Timeout in ms for wait conditions |
| `headless` | boolean | No | `true` | Run browser in headless mode |
| `backend` | string (cdp, bidi, auto) | No | `"cdp"` | Backend: 'cdp', 'bidi', or 'auto' |

### wavexis_double_click

Double-click an element matching a CSS selector.

Use wavexis_click for single clicks or wavexis_nl_click when you only
have a natural language description of the element.

Side effects: Fires two rapid click events on the element, which may
open files, edit cells, or trigger application-specific actions.
Returns: JSON string with keys: 'status' ('ok'/'error'). On error also
'error', 'tool', 'type', 'message', 'suggestion' (all str).

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `selector` | string | Yes | — | CSS selector for element to double-click |
| `session_id` | string | No | `null` | Active session ID. If omitted, a stateless session is created for this call. |
| `url` | string | No | `null` | URL to navigate to (required without session_id) |
| `auto_wait` | boolean | No | `true` | Wait for the element before clicking |
| `wait_timeout` | integer | No | `30000` | Timeout in ms for wait conditions |
| `headless` | boolean | No | `true` | Run browser in headless mode |
| `backend` | string (cdp, bidi, auto) | No | `"cdp"` | Backend: 'cdp', 'bidi', or 'auto' |

### wavexis_drag

Drag an element from a source selector to a target selector.

Use wavexis_drop when you need to drop arbitrary MIME data or files
onto an element rather than dragging an existing DOM element.

Side effects: Performs a drag-and-drop operation between two elements,
firing drag/dragstart/dragend and drop events.
Returns: JSON string with keys: 'status' ('ok'/'error'). On error also
'error', 'tool', 'type', 'message', 'suggestion' (all str).

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `source` | string | Yes | — | CSS selector for drag source |
| `target` | string | Yes | — | CSS selector for drop target |
| `session_id` | string | No | `null` | Active session ID. If omitted, a stateless session is created for this call. |
| `url` | string | No | `null` | URL to navigate to (required without session_id) |
| `wait_timeout` | integer | No | `30000` | Timeout in ms for wait conditions |
| `headless` | boolean | No | `true` | Run browser in headless mode |
| `backend` | string (cdp, bidi, auto) | No | `"cdp"` | Backend: 'cdp', 'bidi', or 'auto' |

### wavexis_drop

Drop files or MIME-typed data onto an element via drag events.

Use wavexis_set_files for standard ``<input type="file">`` uploads or
wavexis_drag for dragging an existing DOM element to another element.

Side effects: Dispatches dragEnter, dragOver, and drop events with the
supplied data and files onto the target element's coordinates.
Returns: JSON string with keys: 'status' ('ok'/'error'), 'selector'
(str), 'x' (float), 'y' (float), 'data_types' (list[str]), 'files'
(list[str]). On error also 'error', 'tool', 'type', 'message',
'suggestion' (all str).

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `selector` | string | Yes | — | CSS selector for the drop target |
| `data` | object | No | — | MIME type to string payload map |
| `paths` | array | No | — | Absolute file paths to drop |
| `session_id` | string | No | `null` | Active session ID. If omitted, a stateless session is created for this call. |
| `url` | string | No | `null` | URL to navigate to (required without session_id) |
| `wait_timeout` | integer | No | `30000` | Timeout in ms for wait conditions |
| `headless` | boolean | No | `true` | Run browser in headless mode |
| `backend` | string (cdp, bidi, auto) | No | `"cdp"` | Backend: 'cdp', 'bidi', or 'auto' |

### wavexis_fill

Fill an input element with a value, replacing existing content.

Use wavexis_type for character-by-character typing with key events, or
wavexis_fill_form when filling multiple fields in one call.

Side effects: Clears the target input/textarea and sets its value to
the provided string, firing a single input event.
Returns: JSON string with keys: 'status' ('ok'/'error'). On error also
'error', 'tool', 'type', 'message', 'suggestion' (all str).

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `selector` | string | Yes | — | CSS selector for the target element |
| `value` | string | Yes | — | Value to fill (replaces existing content) |
| `session_id` | string | No | `null` | Active session ID. If omitted, a stateless session is created for this call. |
| `url` | string | No | `null` | URL to navigate to (required without session_id) |
| `wait_timeout` | integer | No | `30000` | Timeout in ms for wait conditions |
| `headless` | boolean | No | `true` | Run browser in headless mode |
| `backend` | string (cdp, bidi, auto) | No | `"cdp"` | Backend: 'cdp', 'bidi', or 'auto' |

### wavexis_fill_form

Fill multiple form fields in one call (convenience composite tool).

Use wavexis_fill for a single field or wavexis_type when per-keystroke
events are required.

Side effects: Clears and sets the value of each field in the provided
list, firing input events on every targeted element.
Returns: JSON string with keys: 'status' ('ok'/'error'), 'fields_filled'
(int, number of fields successfully filled). On error also 'error',
'tool', 'type', 'message', 'suggestion' (all str).

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `fields` | array | Yes | — | Form fields to fill |
| `session_id` | string | No | `null` | Active session ID. If omitted, a stateless session is created for this call. |
| `url` | string | No | `null` | URL to navigate to (required without session_id) |
| `wait_timeout` | integer | No | `30000` | Timeout in ms for wait conditions |
| `headless` | boolean | No | `true` | Run browser in headless mode |
| `backend` | string (cdp, bidi, auto) | No | `"cdp"` | Backend: 'cdp', 'bidi', or 'auto' |

### wavexis_find_by_text

Find element selector(s) by visible text content without interacting.

Use this to locate elements before calling wavexis_click or wavexis_fill
when you know the visible text but not the CSS selector.

Side effects: None — this is a read-only lookup that does not modify the
page or interact with any element.
Returns: JSON string with keys: 'selector' (str, first match) when
all=False, or 'selectors' (list[str]) and 'count' (int) when all=True.
On error also 'error', 'tool', 'type', 'message', 'suggestion' (all str).

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `query` | string | Yes | — | Text to search for in visible page content |
| `all` | boolean | No | `false` | Return all matches (True) or first match (False) |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |

### wavexis_hover

Hover over an element matching a CSS selector.

Use wavexis_click to actually activate an element; hover only moves the
cursor without clicking.

Side effects: Moves the mouse cursor over the target element, firing
mouseover/mouseenter events that may reveal tooltips or menus.
Returns: JSON string with keys: 'status' ('ok'/'error'). On error also
'error', 'tool', 'type', 'message', 'suggestion' (all str).

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `selector` | string | Yes | — | CSS selector for the target element |
| `session_id` | string | No | `null` | Active session ID. If omitted, a stateless session is created for this call. |
| `url` | string | No | `null` | URL to navigate to (required without session_id) |
| `wait_timeout` | integer | No | `30000` | Timeout in ms for wait conditions |
| `headless` | boolean | No | `true` | Run browser in headless mode |
| `backend` | string (cdp, bidi, auto) | No | `"cdp"` | Backend: 'cdp', 'bidi', or 'auto' |

### wavexis_key_press

Press a single keyboard key on the focused element.

Use wavexis_type for typing full strings or wavexis_fill for setting
field values without individual key events.

Side effects: Dispatches a keydown/keypress/keyup sequence for the
given key on whatever element currently has focus.
Returns: JSON string with keys: 'status' ('ok'/'error'). On error also
'error', 'tool', 'type', 'message', 'suggestion' (all str).

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `key` | string | Yes | — | Key to press (e.g. 'Enter', 'Tab', 'Escape', 'a') |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |

### wavexis_nl_click

Click an element described in natural language.

Use wavexis_click when you already know the CSS selector, or
wavexis_nl_fill to fill a field described in natural language.

Side effects: Locates the best-matching element via text/semantic
matching and triggers a click event on it.
Returns: JSON string with keys: 'status' ('ok'/'error'). On error also
'error', 'tool', 'type', 'message', 'suggestion' (all str).

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `query` | string | Yes | — | Natural language description of the element to click |
| `auto_wait` | boolean | No | `true` | Wait for element to be ready before clicking |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |

### wavexis_nl_fill

Fill an element described in natural language with a value.

Use wavexis_fill when you already know the CSS selector, or
wavexis_nl_click to click an element described in natural language.

Side effects: Locates the best-matching element via text/semantic
matching, clears it, and sets its value to the provided string.
Returns: JSON string with keys: 'status' ('ok'/'error'). On error also
'error', 'tool', 'type', 'message', 'suggestion' (all str).

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `query` | string | Yes | — | Natural language description of the element to fill |
| `value` | string | Yes | — | Value to fill |
| `auto_wait` | boolean | No | `true` | Wait for element to be ready before filling |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |

### wavexis_right_click

Right-click an element matching a CSS selector.

Use wavexis_click for standard left clicks or wavexis_double_click for
double clicks.

Side effects: Fires a contextmenu event on the element, typically
opening a context menu in the browser.
Returns: JSON string with keys: 'status' ('ok'/'error'). On error also
'error', 'tool', 'type', 'message', 'suggestion' (all str).

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `selector` | string | Yes | — | CSS selector for element to right-click |
| `session_id` | string | No | `null` | Active session ID. If omitted, a stateless session is created for this call. |
| `url` | string | No | `null` | URL to navigate to (required without session_id) |
| `auto_wait` | boolean | No | `true` | Wait for the element before clicking |
| `wait_timeout` | integer | No | `30000` | Timeout in ms for wait conditions |
| `headless` | boolean | No | `true` | Run browser in headless mode |
| `backend` | string (cdp, bidi, auto) | No | `"cdp"` | Backend: 'cdp', 'bidi', or 'auto' |

### wavexis_select_option

Select an option in a ``<select>`` element by value.

Use wavexis_fill for text inputs or wavexis_click for custom dropdown
widgets that are not native ``<select>`` elements.

Side effects: Changes the selected option of the ``<select>`` element,
firing change and input events.
Returns: JSON string with keys: 'status' ('ok'/'error'). On error also
'error', 'tool', 'type', 'message', 'suggestion' (all str).

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `selector` | string | Yes | — | CSS selector for <select> element |
| `value` | string | Yes | — | Option value to select |
| `session_id` | string | No | `null` | Active session ID. If omitted, a stateless session is created for this call. |
| `url` | string | No | `null` | URL to navigate to (required without session_id) |
| `wait_timeout` | integer | No | `30000` | Timeout in ms for wait conditions |
| `headless` | boolean | No | `true` | Run browser in headless mode |
| `backend` | string (cdp, bidi, auto) | No | `"cdp"` | Backend: 'cdp', 'bidi', or 'auto' |

### wavexis_set_files

Upload files to a file input element (``<input type="file">``).

Use wavexis_drop when you need to simulate drag-and-drop of files or
MIME data onto a non-file-input element.

Side effects: Sets the selected files on the target file input element,
firing change events that typically trigger upload logic.
Returns: JSON string with keys: 'status' ('ok'/'error'). On error also
'error', 'tool', 'type', 'message', 'suggestion' (all str).

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `selector` | string | Yes | — | CSS selector for <input type='file'> element |
| `files` | array | Yes | — | Absolute file paths to upload |
| `session_id` | string | No | `null` | Active session ID. If omitted, a stateless session is created for this call. |
| `url` | string | No | `null` | URL to navigate to (required without session_id) |
| `wait_timeout` | integer | No | `30000` | Timeout in ms for wait conditions |
| `headless` | boolean | No | `true` | Run browser in headless mode |
| `backend` | string (cdp, bidi, auto) | No | `"cdp"` | Backend: 'cdp', 'bidi', or 'auto' |

### wavexis_tap

Tap an element matching a CSS selector (touch-emulated click).

Use wavexis_click for mouse-based clicking on desktop contexts or
wavexis_nl_click when you only have a natural language description.

Side effects: Dispatches a touch tap on the target element, which may
toggle controls or trigger navigation on mobile-optimised pages.
Returns: JSON string with keys: 'status' ('ok'/'error'). On error also
'error', 'tool', 'type', 'message', 'suggestion' (all str).

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `selector` | string | Yes | — | CSS selector for element to tap |
| `session_id` | string | No | `null` | Active session ID. If omitted, a stateless session is created for this call. |
| `url` | string | No | `null` | URL to navigate to (required without session_id) |
| `wait_timeout` | integer | No | `30000` | Timeout in ms for wait conditions |
| `headless` | boolean | No | `true` | Run browser in headless mode |
| `backend` | string (cdp, bidi, auto) | No | `"cdp"` | Backend: 'cdp', 'bidi', or 'auto' |

### wavexis_type

Type text into an element character by character with optional delay.

Use wavexis_fill instead when you want to set a field's value instantly
without per-keystroke delays, or wavexis_fill_form for multiple fields.

Side effects: Appends characters to the target input/textarea element,
firing keydown/keypress/input/keyup events per character.
Returns: JSON string with keys: 'status' ('ok'/'error'). On error also
'error', 'tool', 'type', 'message', 'suggestion' (all str).

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `selector` | string | Yes | — | CSS selector for the target element |
| `text` | string | Yes | — | Text to type character by character |
| `session_id` | string | No | `null` | Active session ID. If omitted, a stateless session is created for this call. |
| `url` | string | No | `null` | URL to navigate to (required without session_id) |
| `delay` | integer | No | `0` | Delay between keystrokes in ms |
| `wait_timeout` | integer | No | `30000` | Timeout in ms for wait conditions |
| `headless` | boolean | No | `true` | Run browser in headless mode |
| `backend` | string (cdp, bidi, auto) | No | `"cdp"` | Backend: 'cdp', 'bidi', or 'auto' |

### wavexis_uncheck

Uncheck a checkbox matching a CSS selector by clicking it.

Use wavexis_check to check a checkbox or wavexis_click for generic
element activation.

Side effects: Clicks the target checkbox to toggle it to unchecked,
firing change events.
Returns: JSON string with keys: 'status' ('ok'/'error'). On error also
'error', 'tool', 'type', 'message', 'suggestion' (all str).

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `selector` | string | Yes | — | CSS selector for checkbox/radio |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |

## Page Actions

### wavexis_close_page

Close a browser page/tab by target id, or the current page if omitted.

This tool mirrors Playwright's API for compatibility; use it to free
resources. The session itself remains active for other tabs.

Side effects: Closes the specified browser target; destructive and
irreversible.
Returns: JSON string with keys: 'status' ('ok'/'error'), 'closed' (str).

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `tab_id` | string | No | `null` | Optional tab/target id; current page is closed if omitted |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |

### wavexis_console_clear

Clear all buffered console messages for the session.

This tool mirrors Playwright's API for compatibility; use it before
capturing a fresh set of console logs to avoid stale entries.

Side effects: Resets the session's in-memory console message buffer.
Returns: JSON string with keys: 'status' ('ok'/'error').

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |

### wavexis_cookie_get

Retrieve a single cookie by name (and optional domain/path) from the browser.

Use ``wavexis_cookie_list`` instead when you need multiple cookies or
broad filtering.

Side effects: None; reads cookie state from the browser session.
Returns: JSON string with keys: 'status' ('ok'/'error'), 'cookie' (dict|null).

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `name` | string | Yes | — | Cookie name to retrieve |
| `domain` | string | No | `null` | Optional domain filter |
| `path` | string | No | `null` | Optional path filter |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |

### wavexis_cookie_list

List browser cookies with optional name, domain, and path filters.

Use ``wavexis_cookie_get`` instead when you need a single named cookie.

Side effects: None; reads cookie state from the browser session.
Returns: JSON string with keys: 'status' ('ok'/'error'),
'cookies' (list[dict]), 'count' (int).

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `name` | string | No | `null` | Optional cookie name filter |
| `domain` | string | No | `null` | Optional domain filter |
| `path` | string | No | `null` | Optional path filter |
| `limit` | integer | No | `100` | Maximum number of cookies to return |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |

### wavexis_find

Search the accessibility snapshot for nodes matching text or a regex pattern.

Use ``wavexis_act`` instead for natural-language element interaction;
this tool mirrors Playwright's snapshot search for compatibility.

Side effects: None; fetches and searches the a11y tree read-only.
Returns: JSON string with keys: 'status' ('ok'/'error'),
'matches' (list[dict]), 'count' (int).

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `text` | string | Yes | — | Text or regex to search in the a11y snapshot |
| `limit` | integer | No | `20` | Maximum number of matches to return |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |

### wavexis_get_config

Return wavexis-mcp server configuration and available browser backends.

Use ``wavexis_backends`` instead when you only need the backend list;
this tool additionally exposes the server name for introspection.

Side effects: None; queries the local filesystem only.
Returns: JSON string with keys: 'status' ('ok'/'error'), 'name' (str),
'available_backends' (list[str]), 'backend_versions' (dict).

**Parameters:**

_This tool takes no parameters._

### wavexis_key_down

Dispatch a raw keyDown event to the active page via CDP.

This tool mirrors Playwright's API for compatibility; use
``wavexis_press_keys`` for typing text and ``wavexis_act`` for
natural-language interaction.

Side effects: Sends a key-down input event to the browser page.
Returns: JSON string with keys: 'status' ('ok'/'error').

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `key` | string | Yes | — | Key to press (e.g. 'Enter', 'a', 'ArrowLeft') |
| `code` | string | No | `""` | Optional physical key code |
| `alt` | boolean | No | `false` | Whether to hold the Alt key |
| `ctrl` | boolean | No | `false` | Whether to hold the Ctrl key |
| `meta` | boolean | No | `false` | Whether to hold the Meta (Cmd) key |
| `shift` | boolean | No | `false` | Whether to hold the Shift key |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |

### wavexis_key_up

Dispatch a raw keyUp event to the active page via CDP.

This tool mirrors Playwright's API for compatibility; pair with
``wavexis_key_down`` for low-level key control, or use
``wavexis_press_keys`` for simple text entry.

Side effects: Sends a key-up input event to the browser page.
Returns: JSON string with keys: 'status' ('ok'/'error').

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `key` | string | Yes | — | Key to release (e.g. 'Enter', 'a') |
| `code` | string | No | `""` | Optional physical key code |
| `alt` | boolean | No | `false` | Whether to hold the Alt key |
| `ctrl` | boolean | No | `false` | Whether to hold the Ctrl key |
| `meta` | boolean | No | `false` | Whether to hold the Meta (Cmd) key |
| `shift` | boolean | No | `false` | Whether to hold the Shift key |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |

### wavexis_mouse_drag_xy

Drag the mouse from one screen coordinate to another via CDP mouse events.

This tool mirrors Playwright's API for compatibility; use ``wavexis_act``
instead for natural-language drag interactions.

Side effects: Dispatches mouseMoved, mousePressed, and mouseReleased
events to the browser page; may trigger page interactions.
Returns: JSON string with keys: 'status' ('ok'/'error').

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `start_x` | number | Yes | — | Starting X coordinate in CSS pixels |
| `start_y` | number | Yes | — | Starting Y coordinate in CSS pixels |
| `end_x` | number | Yes | — | Ending X coordinate in CSS pixels |
| `end_y` | number | Yes | — | Ending Y coordinate in CSS pixels |
| `button` | string (left, right, middle) | No | `"left"` | Mouse button to use |
| `steps` | integer | No | `5` | Number of intermediate steps for smooth dragging |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |

### wavexis_press_keys

Type a sequence of characters at the page level without targeting an element.

Use ``wavexis_key_down``/``wavexis_key_up`` instead for individual
modifier-key control, or ``wavexis_act`` for natural-language typing.

Side effects: Dispatches keyDown/keyUp pairs to the browser page; no
network requests.
Returns: JSON string with keys: 'status' ('ok'/'error'), 'typed' (str).

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `text` | string | Yes | — | Text/keys to type character by character |
| `delay` | integer | No | `0` | Delay between keystrokes in milliseconds |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |

## Cookies

### wavexis_cookies_clear

Clear all cookies from the browser session.

Use ``wavexis_cookies_delete`` to remove a specific cookie, or
``wavexis_cookies_get`` to inspect cookies before clearing.

Side effects: uses an existing session backend, destructively removes
all cookies from the browser.
Returns: JSON string with keys: 'status' ('ok'/'error').

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |

### wavexis_cookies_delete

Delete cookies matching a name and domain in the browser.

Use ``wavexis_cookies_clear`` to remove all cookies, or
``wavexis_cookies_set`` to add a new cookie.

Side effects: launches/acquires a browser backend, navigates to ``url``
if provided, destructively removes matching cookies from browser state.
Returns: JSON string with keys: 'status' ('ok'/'error').

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `name` | string | Yes | — | Name of the item |
| `domain` | string | Yes | — | Cookie domain |
| `session_id` | string | No | `null` | Active session ID. If omitted, a stateless session is created for this call. |
| `url` | string | No | `null` | URL to navigate to (required without session_id) |
| `wait_timeout` | integer | No | `30000` | Timeout in ms for wait conditions |
| `headless` | boolean | No | `true` | Run browser in headless mode |
| `backend` | string (cdp, bidi, auto) | No | `"cdp"` | Backend: 'cdp', 'bidi', or 'auto' |

### wavexis_cookies_get

Retrieve all cookies for the current page context.

Use ``wavexis_cookies_set`` to add a cookie, or
``wavexis_cookies_clear`` to remove all cookies at once.

Side effects: launches/acquires a browser backend, navigates to ``url``
if provided; read-only with respect to browser state.
Returns: JSON string with keys: 'status' ('ok'/'error'), 'cookies'
(list[dict]), 'count' (int).

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | No | `null` | Active session ID. If omitted, a stateless session is created for this call. |
| `url` | string | No | `null` | URL to navigate to (required without session_id) |
| `wait_timeout` | integer | No | `30000` | Timeout in ms for wait conditions |
| `headless` | boolean | No | `true` | Run browser in headless mode |
| `backend` | string (cdp, bidi, auto) | No | `"cdp"` | Backend: 'cdp', 'bidi', or 'auto' |

### wavexis_cookies_set

Set a single cookie in the browser for the current page.

Use ``wavexis_cookies_get`` to read cookies, or
``wavexis_cookies_delete`` to remove a specific cookie.

Side effects: launches/acquires a browser backend, navigates to ``url``
if provided, mutates browser cookie state.
Returns: JSON string with keys: 'status' ('ok'/'error').

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `name` | string | Yes | — | Name of the item |
| `value` | string | Yes | — | Value to set |
| `domain` | string | Yes | — | Cookie domain |
| `path` | string | No | `"/"` | Cookie path |
| `secure` | boolean | No | `true` | Whether the cookie is Secure |
| `http_only` | boolean | No | `false` | Whether the cookie is HttpOnly |
| `same_site` | string (Strict, Lax, None) | No | `"Lax"` | SameSite attribute: Strict, Lax, or None |
| `session_id` | string | No | `null` | Active session ID. If omitted, a stateless session is created for this call. |
| `url` | string | No | `null` | URL to navigate to (required without session_id) |
| `wait_timeout` | integer | No | `30000` | Timeout in ms for wait conditions |
| `headless` | boolean | No | `true` | Run browser in headless mode |
| `backend` | string (cdp, bidi, auto) | No | `"cdp"` | Backend: 'cdp', 'bidi', or 'auto' |

## DOM

### wavexis_dom_focus

Focus an element matching a CSS selector.

Use wavexis_dom_click instead when the intent is to activate a control rather than focus it.

Side effects: Mutates DOM focus state; may trigger focus event handlers on the element.
Returns: JSON string with keys: 'status' ('ok'/'error').

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `selector` | string | Yes | — | CSS selector for the target element |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |

### wavexis_dom_get

Retrieve the HTML of an element matching a CSS selector.

Use wavexis_dom_query instead when you need element metadata rather than raw HTML.

Side effects: None; read-only. May navigate to ``url`` if provided.
Returns: JSON string with keys: 'status' ('ok'/'error'), 'html' (str), 'selector' (str).

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `selector` | string | Yes | — | CSS selector for the target element |
| `session_id` | string | No | `null` | Active session ID. If omitted, a stateless session is created for this call. |
| `url` | string | No | `null` | URL to navigate to (required without session_id) |
| `outer` | boolean | No | `true` | Return outerHTML (True) or innerHTML (False) |
| `wait_timeout` | integer | No | `30000` | Timeout in ms for wait conditions |
| `headless` | boolean | No | `true` | Run browser in headless mode |
| `backend` | string (cdp, bidi, auto) | No | `"cdp"` | Backend: 'cdp', 'bidi', or 'auto' |

### wavexis_dom_get_attr

Read an attribute value from an element matching a CSS selector.

Use wavexis_dom_set_attr to write an attribute value.

Side effects: None; read-only.
Returns: JSON string with keys: 'status' ('ok'/'error'), 'value' (str|None),
    'selector' (str), 'name' (str).

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `selector` | string | Yes | — | CSS selector for the target element |
| `name` | string | Yes | — | Name of the item |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |

### wavexis_dom_query

Query elements by CSS selector and return paginated metadata.

Use wavexis_dom_get instead when you only need the raw HTML of a single element.

Side effects: None; read-only. May navigate to ``url`` if provided.
Returns: JSON string with keys: 'status' ('ok'/'error'), 'elements' (list[dict]),
    'count' (int), 'total' (int).

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `selector` | string | Yes | — | CSS selector for the target element |
| `session_id` | string | No | `null` | Active session ID. If omitted, a stateless session is created for this call. |
| `url` | string | No | `null` | URL to navigate to (required without session_id) |
| `all` | boolean | No | `false` | Return all matches (True) or first only (False) |
| `limit` | integer | No | `50` | Max elements to return when all=True |
| `offset` | integer | No | `0` | Skip first N elements for pagination |
| `wait_timeout` | integer | No | `30000` | Timeout in ms for wait conditions |
| `headless` | boolean | No | `true` | Run browser in headless mode |
| `backend` | string (cdp, bidi, auto) | No | `"cdp"` | Backend: 'cdp', 'bidi', or 'auto' |

### wavexis_dom_remove

Remove an element matching a CSS selector from the DOM.

Use wavexis_dom_set_attr to hide an element (e.g. ``display:none``) instead of deleting it.

Side effects: Destructive; permanently removes the matched element from the live DOM.
Returns: JSON string with keys: 'status' ('ok'/'error').

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `selector` | string | Yes | — | CSS selector for the target element |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |

### wavexis_dom_remove_attr

Remove an attribute from an element matching a CSS selector.

Use wavexis_dom_set_attr to restore or change an attribute instead of removing it.

Side effects: Mutates the DOM by deleting the attribute from the matched element.
Returns: JSON string with keys: 'status' ('ok'/'error').

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `selector` | string | Yes | — | CSS selector for the target element |
| `name` | string | Yes | — | Name of the item |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |

### wavexis_dom_scroll

Scroll to an element or by a pixel offset.

Use wavexis_dom_get to inspect an element's position before scrolling by offset.

Side effects: Changes the page scroll position; may trigger scroll event listeners.
Returns: JSON string with keys: 'status' ('ok'/'error').

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `selector` | string | No | `null` | CSS selector to scroll to |
| `x` | integer | No | `0` | Horizontal scroll offset |
| `y` | integer | No | `0` | Vertical scroll offset |

### wavexis_dom_set_attr

Set an attribute on an element matching a CSS selector.

Use wavexis_dom_get_attr to read the current value before setting.

Side effects: Mutates the DOM by writing the attribute on the matched element.
Returns: JSON string with keys: 'status' ('ok'/'error').

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `selector` | string | Yes | — | CSS selector for the target element |
| `name` | string | Yes | — | Attribute name |
| `value` | string | Yes | — | Attribute value |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |

### wavexis_dom_snapshot

Capture a full DOM snapshot of the page including iframes and shadow roots.

Use wavexis_dom_query for lightweight element metadata instead of a full snapshot.

Side effects: None; read-only.
Returns: JSON string with keys: 'status' ('ok'/'error'), 'snapshot' (dict),
    'documents' (int).

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |

### wavexis_iframe_click

Click an element inside an iframe.

Use wavexis_iframe_eval only for custom JS that click/fill cannot express.

Side effects: Triggers click handlers and may navigate or mutate the iframe DOM.
Returns: JSON string with keys: 'status' ('ok'/'error').

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `iframe_selector` | string | Yes | — | CSS selector for the <iframe> element |
| `selector` | string | Yes | — | CSS selector inside the iframe |

### wavexis_iframe_eval

Evaluate a JavaScript expression inside an iframe.

Use wavexis_iframe_click or wavexis_iframe_fill for standard interactions instead of raw JS.

Side effects: Arbitrary; executes user-supplied JavaScript within the iframe context.
Returns: JSON string with keys: 'status' ('ok'/'error'), 'result' (any).

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `iframe_selector` | string | Yes | — | CSS selector for the <iframe> element |
| `expression` | string | Yes | — | JavaScript expression to evaluate |
| `await_promise` | boolean | No | `false` | Whether to await the returned promise |

### wavexis_iframe_fill

Fill an input element inside an iframe with a value.

Use wavexis_iframe_click to submit or activate the field after filling.

Side effects: Mutates the input value within the iframe; may trigger input/change events.
Returns: JSON string with keys: 'status' ('ok'/'error').

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `iframe_selector` | string | Yes | — | CSS selector for the <iframe> element |
| `selector` | string | Yes | — | CSS selector inside the iframe |
| `value` | string | Yes | — | Value to set in the input field |

### wavexis_shadow_click

Click an element inside a shadow DOM tree.

Pierces shadow boundaries using the provided selector chain.
Use wavexis_shadow_eval only for custom JS that click/fill cannot express.

Side effects: Triggers click handlers and may navigate or mutate the shadow DOM.
Returns: JSON string with keys: 'status' ('ok'/'error').

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `selectors` | array | Yes | — | CSS selectors piercing shadow boundaries |

### wavexis_shadow_eval

Evaluate a JavaScript expression inside a shadow DOM tree.

Pierces shadow boundaries using the provided selector chain: ``selectors[0]`` is in the
main document, ``selectors[1]`` in ``selectors[0].shadowRoot``, and so on.
Use wavexis_shadow_click or wavexis_shadow_fill for standard interactions instead of raw JS.

Side effects: Arbitrary; executes user-supplied JavaScript within the shadow DOM context.
Returns: JSON string with keys: 'status' ('ok'/'error'), 'result' (any).

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `selectors` | array | Yes | — | CSS selectors piercing shadow boundaries (selectors[0] in document, selectors[1] in selectors[0].shadowRoot, etc.) |
| `expression` | string | Yes | — | JavaScript expression to evaluate |
| `await_promise` | boolean | No | `false` | Whether to await the returned promise |

### wavexis_shadow_fill

Fill an input element inside a shadow DOM tree with a value.

Pierces shadow boundaries using the provided selector chain.
Use wavexis_shadow_click to submit or activate the field after filling.

Side effects: Mutates the input value within the shadow DOM; may trigger
input/change events.
Returns: JSON string with keys: 'status' ('ok'/'error').

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `selectors` | array | Yes | — | CSS selectors piercing shadow boundaries |
| `value` | string | Yes | — | Value to set in the input field |

## JavaScript

### wavexis_eval

Evaluate a JavaScript expression in the browser context and return the result.

Use ``wavexis_scrape`` when the same expression must run across many
pages, or ``wavexis_act`` for natural-language interaction instead of
raw JS.

Side effects: launches/acquires a browser backend, navigates to ``url``
if provided, executes arbitrary JS in the page (may trigger network
requests or DOM mutations).
Returns: JSON string with keys: 'status' ('ok'/'error'), 'result'
(Any), 'type' (str).

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `expression` | string | Yes | — | JavaScript expression to evaluate |
| `session_id` | string | No | `null` | Active session ID. If omitted, a stateless session is created for this call. |
| `url` | string | No | `null` | URL to navigate to first (required without session) |
| `await_promise` | boolean | No | `false` | Await a returned Promise |
| `wait_timeout` | integer | No | `30000` | Timeout in ms for wait conditions |
| `headless` | boolean | No | `true` | Run browser in headless mode |
| `backend` | string (cdp, bidi, auto) | No | `"cdp"` | Backend: 'cdp', 'bidi', or 'auto' |

## Session Management

### wavexis_session_close

Close a browser session and release all associated resources.

Call when the session is no longer needed to free memory and browser
processes; use wavexis_close_tab to close individual tabs instead.

Side effects: Terminates the browser process (or disconnects from a
remote one) and frees session state. Destructive — all unsaved page
state is lost.
Returns: JSON string with keys: 'status' ('ok'/'error'),
'session_id' (str).

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Session ID from wavexis_session_open |

### wavexis_session_info

Query metadata and current URL of an active browser session.

Use to inspect session health or retrieve the current page URL; use
wavexis_list_tabs for tab-level details instead.

Side effects: None — read-only; queries in-memory session state and
the browser's current URL.
Returns: JSON string with keys: 'status' ('ok'/'error'),
'session_id' (str), 'backend' (str), 'created_at' (str),
'current_url' (str).

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |

### wavexis_session_open

Launch a persistent browser session for multi-step workflows.

Call once at the start of a task and reuse the returned session_id for
all subsequent calls; use wavexis_navigate with session_id omitted for
one-off page fetches instead.

Side effects: Launches a browser process (or connects to an existing
one) and allocates server-side session state; may open network
connections to remote/cloud browsers.
Returns: JSON string with keys: 'status' ('ok'/'error'),
'session_id' (str), 'backend' (str).

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `backend` | string (cdp, bidi, auto) | No | `"cdp"` | Backend: 'cdp', 'bidi', or 'auto' |
| `headless` | boolean | No | `true` | Run browser in headless mode |
| `width` | integer | No | `1280` | Viewport width in pixels |
| `height` | integer | No | `800` | Viewport height in pixels |
| `user_agent` | string | No | `null` | Custom User-Agent string |
| `extra_headers` | object | No | — | Extra HTTP headers to send |
| `proxy` | string | No | `null` | Proxy server URL (e.g. http://host:port) |
| `timeout` | integer | No | `30000` | Operation timeout in ms |
| `user_data_dir` | string | No | `null` | Persistent Chrome user data directory |
| `browser_url` | string | No | `null` | WebSocket URL of an existing browser (e.g. ws://localhost:9222) |
| `remote_url` | string | No | `null` | Cloud browser WebSocket URL |
| `stealth` | boolean | No | `false` | Enable anti-bot stealth mode |
| `browser` | string (chrome, firefox) | No | `"chrome"` | Browser engine for BiDi backend: 'chrome' (chromedriver) or 'firefox' (geckodriver). Only used when backend='bidi'. |
| `connect_existing` | boolean | No | `false` | Launch Chrome with --remote-debugging-port and connect to it. Useful for reusing an existing browser profile with log... |
