# Core Tools (72)

Always enabled. No `--caps` flag needed.

Core tools cover the essential browser automation workflow. These 72 tools are always registered regardless of which capability tiers you enable.

## Natural language interaction

| Tool | Parameters | Description |
| --- | --- | --- |
| `wavexis_act` | `instruction, session_id, max_retries?, value?` | Execute a natural language instruction on the current page (M1). |

## Tabs

| Tool | Parameters | Description |
| --- | --- | --- |
| `wavexis_activate_tab` | `session_id, tab_id` | Activate (focus) a tab by its ID. |
| `wavexis_close_tab` | `session_id, tab_id` | Close a tab by its ID. |
| `wavexis_list_tabs` | `session_id` | List all open browser tabs. |
| `wavexis_new_tab` | `session_id, url?` | Create a new browser tab. |

## Screenshot / PDF / Capture

| Tool | Parameters | Description |
| --- | --- | --- |
| `wavexis_annotated_screenshot` | `session_id, selectors, format?, output_path?` | Take a screenshot with numbered labels overlaid on elements. |
| `wavexis_page_pdf` | `url?, session_id?, landscape?, display_header_footer?, print_background?, scale?, paper_width?, paper_height?, margin_top?, margin_bottom?, margin_left?, margin_right?, output_path?, wait_timeout?, headless?, backend?` | Generate a PDF using the low-level Page.printToPDF CDP method. |
| `wavexis_page_snapshot` | `url?, session_id?, format?, output_path?, wait_timeout?, headless?, backend?` | Capture the page as MHTML or a plain text document. |
| `wavexis_pdf` | `url?, session_id?, paper?, landscape?, margin?, no_header_footer?, media?, js?, output_path?, wait_timeout?, headless?, backend?` | Generate a PDF of a web page. |
| `wavexis_scrape` | `urls, session_id?, expression?, output_format?, selector?, wait_timeout?, headless?, backend?, limit?, offset?` | Scrape multiple URLs by evaluating a JS expression on each page. |
| `wavexis_screencast` | `url?, session_id?, format?, quality?, max_width?, max_height?, duration?, interval?, output_dir?, wait_timeout?, headless?, backend?` | Capture a sequence of screenshots (frame-by-frame). |
| `wavexis_screenshot` | `url?, session_id?, full_page?, format?, quality?, selector?, js?, device?, output_path?, wait_strategy?, wait_selector?, wait_timeout?, headless?, width?, height?, backend?` | Take a screenshot of a web page or element. |

## Navigation

| Tool | Parameters | Description |
| --- | --- | --- |
| `wavexis_back` | `session_id` | Navigate back in browser history. |
| `wavexis_forward` | `session_id` | Navigate forward in browser history. |
| `wavexis_navigate` | `url, session_id?, wait_strategy?, wait_selector?, wait_url_pattern?, wait_timeout?, headless?, backend?` | Navigate to a URL in the browser. |
| `wavexis_reload` | `session_id, ignore_cache?` | Reload the current page. |
| `wavexis_stop` | `session_id` | Stop all pending navigations and resource loads. |
| `wavexis_wait` | `session_id, strategy?, selector?, url_pattern?, timeout?` | Wait for a specific condition on the page. |

## Utility

| Tool | Parameters | Description |
| --- | --- | --- |
| `wavexis_backends` | — | List available browser backends and their versions. |
| `wavexis_browser_version` | `session_id?, backend?` | Get the browser version string. |
| `wavexis_invoke` | `method, params?, session_id?, url?, output_path?, backend?, headless?, width?, height?, user_agent?, extra_headers?, proxy?, timeout?, user_data_dir?, browser_url?, remote_url?, stealth?, wait_strategy?, wait_selector?, wait_timeout?` | Invoke any wavexis backend method by name. |

## Input

| Tool | Parameters | Description |
| --- | --- | --- |
| `wavexis_check` | `selector, session_id` | Check a checkbox or radio button. |
| `wavexis_click` | `selector, session_id?, url?, button?, click_count?, wait_timeout?, headless?, backend?` | Click an element matching a CSS selector. |
| `wavexis_double_click` | `selector, session_id?, url?, auto_wait?, wait_timeout?, headless?, backend?` | Double-click an element matching a CSS selector. |
| `wavexis_drag` | `source, target, session_id?, url?, wait_timeout?, headless?, backend?` | Drag an element from source selector to target selector. |
| `wavexis_drop` | `selector, data?, paths?, session_id?, url?, wait_timeout?, headless?, backend?` | Drop files or MIME-typed data onto an element. |
| `wavexis_fill` | `selector, value, session_id?, url?, wait_timeout?, headless?, backend?` | Fill an input element with a value (replaces existing content). |
| `wavexis_fill_form` | `fields, session_id?, url?, wait_timeout?, headless?, backend?` | Fill multiple form fields in one call (convenience tool). |
| `wavexis_find_by_text` | `query, all?, session_id` | Find element(s) by visible text content. |
| `wavexis_hover` | `selector, session_id?, url?, wait_timeout?, headless?, backend?` | Hover over an element matching a CSS selector. |
| `wavexis_key_press` | `key, session_id` | Press a keyboard key. |
| `wavexis_nl_click` | `query, auto_wait?, session_id` | Click an element described in natural language. |
| `wavexis_nl_fill` | `query, value, auto_wait?, session_id` | Fill an element described in natural language. |
| `wavexis_right_click` | `selector, session_id?, url?, auto_wait?, wait_timeout?, headless?, backend?` | Right-click an element matching a CSS selector. |
| `wavexis_select_option` | `selector, value, session_id?, url?, wait_timeout?, headless?, backend?` | Select an option in a ``<select>`` element by value. |
| `wavexis_set_files` | `selector, files, session_id?, url?, wait_timeout?, headless?, backend?` | Upload files to a file input element. |
| `wavexis_tap` | `selector, session_id?, url?, wait_timeout?, headless?, backend?` | Tap an element (touch emulation click). |
| `wavexis_type` | `selector, text, session_id?, url?, delay?, wait_timeout?, headless?, backend?` | Type text into an element character by character. |
| `wavexis_uncheck` | `selector, session_id` | Uncheck a checkbox. |

## Page actions

| Tool | Parameters | Description |
| --- | --- | --- |
| `wavexis_close_page` | `tab_id?, session_id` | Close the current page/tab. |
| `wavexis_console_clear` | `session_id` | Clear all console messages. |
| `wavexis_cookie_get` | `name, domain?, path?, session_id` | Get a specific cookie by name. |
| `wavexis_cookie_list` | `name?, domain?, path?, limit?, session_id` | List cookies with optional filters. |
| `wavexis_find` | `text, limit?, session_id` | Find nodes in the accessibility snapshot matching the given text/regex. |
| `wavexis_get_config` | — | Return wavexis-mcp server configuration and available backends. |
| `wavexis_key_down` | `key, code?, alt?, ctrl?, meta?, shift?, session_id` | Dispatch a keyDown event to the page. |
| `wavexis_key_up` | `key, code?, alt?, ctrl?, meta?, shift?, session_id` | Dispatch a keyUp event to the page. |
| `wavexis_mouse_drag_xy` | `start_x, start_y, end_x, end_y, button?, steps?, session_id` | Drag the mouse from one coordinate to another. |
| `wavexis_press_keys` | `text, delay?, session_id` | Type a sequence of keys at the page level (no element target required). |

## Cookies

| Tool | Parameters | Description |
| --- | --- | --- |
| `wavexis_cookies_clear` | `session_id` | Clear all browser cookies. |
| `wavexis_cookies_delete` | `name, domain, session_id?, url?, wait_timeout?, headless?, backend?` | Delete cookies matching name and domain. |
| `wavexis_cookies_get` | `session_id?, url?, wait_timeout?, headless?, backend?` | Get all cookies for the current page. |
| `wavexis_cookies_set` | `name, value, domain, path?, secure?, http_only?, same_site?, session_id?, url?, wait_timeout?, headless?, backend?` | Set a cookie in the browser. |

## DOM

| Tool | Parameters | Description |
| --- | --- | --- |
| `wavexis_dom_focus` | `selector, session_id` | Focus an element matching a CSS selector. |
| `wavexis_dom_get` | `selector, session_id?, url?, outer?, wait_timeout?, headless?, backend?` | Get the HTML of an element matching a CSS selector. |
| `wavexis_dom_get_attr` | `selector, name, session_id` | Get an attribute value from an element matching a CSS selector. |
| `wavexis_dom_query` | `selector, session_id?, url?, all?, limit?, offset?, wait_timeout?, headless?, backend?` | Query elements by CSS selector. |
| `wavexis_dom_remove` | `selector, session_id` | Remove an element matching a CSS selector from the DOM. |
| `wavexis_dom_remove_attr` | `selector, name, session_id` | Remove an attribute from an element matching a CSS selector. |
| `wavexis_dom_scroll` | `session_id, selector?, x?, y?` | Scroll to an element or by offset. |
| `wavexis_dom_set_attr` | `selector, name, value, session_id` | Set an attribute on an element matching a CSS selector. |
| `wavexis_dom_snapshot` | `session_id` | Capture a full DOM snapshot of the page. |
| `wavexis_iframe_click` | `session_id, iframe_selector, selector` | Click an element inside an iframe. |
| `wavexis_iframe_eval` | `session_id, iframe_selector, expression, await_promise?` | Evaluate a JavaScript expression inside an iframe. |
| `wavexis_iframe_fill` | `session_id, iframe_selector, selector, value` | Fill an input element inside an iframe. |
| `wavexis_shadow_click` | `session_id, selectors` | Click an element inside a shadow DOM tree. |
| `wavexis_shadow_eval` | `session_id, selectors, expression, await_promise?` | Evaluate a JavaScript expression inside a shadow DOM tree. |
| `wavexis_shadow_fill` | `session_id, selectors, value` | Fill an input element inside a shadow DOM tree. |

## JavaScript

| Tool | Parameters | Description |
| --- | --- | --- |
| `wavexis_eval` | `expression, session_id?, url?, await_promise?, wait_timeout?, headless?, backend?` | Evaluate a JavaScript expression and return the result. |

## Session management

| Tool | Parameters | Description |
| --- | --- | --- |
| `wavexis_session_close` | `session_id` | Close a browser session and release resources. |
| `wavexis_session_info` | `session_id` | Get information about an active browser session. |
| `wavexis_session_open` | `backend?, headless?, width?, height?, user_agent?, extra_headers?, proxy?, timeout?, user_data_dir?, browser_url?, remote_url?, stealth?` | Launch a persistent browser session for multi-step workflows. |
