# Vision Tools (6)

Enable with `--caps=vision`.

Vision tools provide pixel-precise mouse control via raw screen coordinates. Unlike DOM-based clicks (which use CSS selectors), vision tools operate on x,y coordinates — useful when elements don't have stable selectors, when interacting with canvas/WebGL, or when the LLM has identified a location from a screenshot.

Coordinate-based mouse operations for pixel-precise interaction.

| Tool | Parameters | Description |
| --- | --- | --- |
| `wavexis_mouse_move` | `session_id`, `x`, `y` | Move the mouse cursor to coordinates `(x, y)`. Does not click. Triggers `mousemove` event. |
| `wavexis_mouse_down` | `session_id`, `x`, `y`, `button` | Press and hold a mouse button at coordinates. `button`: `left` (default), `right`, `middle`. |
| `wavexis_mouse_up` | `session_id`, `x`, `y`, `button` | Release a mouse button at coordinates. |
| `wavexis_mouse_click_xy` | `session_id`, `x`, `y`, `button`, `click_count` | Click at specific coordinates. `click_count`: 1 (default) or 2 (double-click). |
| `wavexis_mouse_double_click_xy` | `session_id`, `x`, `y` | Double-click at coordinates. Convenience wrapper around `mouse_click_xy` with `click_count=2`. |

!!! example "Click a canvas element"
    ```text
    wavexis_session_open(backend="cdp")
    wavexis_navigate(session_id="abc-123", url="https://example.com/canvas-app")
    wavexis_screenshot(session_id="abc-123")
    # LLM identifies a button at (320, 180) from the screenshot
    wavexis_mouse_click_xy(session_id="abc-123", x=320, y=180)
    wavexis_session_close(session_id="abc-123")
    ```

!!! note "When to use vision vs DOM tools"
    Use **DOM tools** (`wavexis_click`, `wavexis_fill`) when you have a CSS selector. They auto-wait for elements and handle edge cases.

    Use **vision tools** when:
    - Elements are inside a `<canvas>` or WebGL context (no DOM nodes)
    - The page uses shadow DOM that's hard to pierce
    - The LLM has identified a location from a screenshot
    - You need pixel-precise positioning
