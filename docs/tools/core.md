# Core Tools (42)

Always enabled. No `--caps` flag needed.

## Session management

| Tool | Description |
| --- | --- |
| `wavexis_session_open` | Open a browser session, returns `session_id` |
| `wavexis_session_close` | Close a session and kill browser |
| `wavexis_session_info` | Get session metadata |
| `wavexis_session_list` | List active sessions |
| `wavexis_session_cleanup` | Close all sessions |

## Navigation

| Tool | Description |
| --- | --- |
| `wavexis_navigate` | Navigate to a URL |
| `wavexis_back` | Go back |
| `wavexis_forward` | Go forward |
| `wavexis_reload` | Reload page |
| `wavexis_stop` | Stop loading |
| `wavexis_wait` | Wait for a condition (load, selector, url, timeout) |

## Capture

| Tool | Description |
| --- | --- |
| `wavexis_screenshot` | Take a screenshot (full page, selector, device) |
| `wavexis_pdf` | Generate PDF |
| `wavexis_scrape` | Scrape text/HTML from one or more URLs |
| `wavexis_screencast` | Capture frames (GIF-like) |

## JavaScript

| Tool | Description |
| --- | --- |
| `wavexis_eval` | Evaluate JavaScript expression |

## DOM

| Tool | Description |
| --- | --- |
| `wavexis_dom_html` | Get HTML of an element |
| `wavexis_dom_text` | Get text content of an element |
| `wavexis_dom_query` | Query elements by selector |
| `wavexis_dom_set_attr` | Set attribute on element |
| `wavexis_dom_remove_attr` | Remove attribute from element |
| `wavexis_dom_remove` | Remove element from DOM |
| `wavexis_dom_focus` | Focus an element |
| `wavexis_dom_scroll` | Scroll to element or coordinates |

## Input

| Tool | Description |
| --- | --- |
| `wavexis_click` | Click an element |
| `wavexis_type` | Type text into element |
| `wavexis_fill` | Fill input field |
| `wavexis_fill_form` | Fill multiple form fields |
| `wavexis_select_option` | Select dropdown option |
| `wavexis_hover` | Hover over element |
| `wavexis_key_press` | Press keyboard key |
| `wavexis_drag` | Drag element to target |
| `wavexis_tap` | Touch tap element |
| `wavexis_set_files` | Set file input |
| `wavexis_check` | Check checkbox |
| `wavexis_uncheck` | Uncheck checkbox |

## Cookies

| Tool | Description |
| --- | --- |
| `wavexis_cookies_get` | Get cookies |
| `wavexis_cookies_set` | Set cookie |
| `wavexis_cookies_delete` | Delete cookie |
| `wavexis_cookies_clear` | Clear all cookies |

## Tabs

| Tool | Description |
| --- | --- |
| `wavexis_tabs_list` | List browser tabs |
| `wavexis_tabs_new` | Open new tab |
| `wavexis_tabs_close` | Close tab |
| `wavexis_tabs_activate` | Switch to tab |

## Utility

| Tool | Description |
| --- | --- |
| `wavexis_browser_version` | Get browser version |
| `wavexis_backends` | List available backends |
