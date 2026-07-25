# Vision Tools (7)

Enable with `--caps=vision`.

These 7 tools are added when the `vision` capability tier is enabled.

## Vision

| Tool | Parameters | Description |
| --- | --- | --- |
| `wavexis_mouse_click_xy` | `session_id, x, y, button?, click_count?` | Click at absolute pixel coordinates (press + release). |
| `wavexis_mouse_double_click_xy` | `session_id, x, y, button?` | Double-click at absolute pixel coordinates. |
| `wavexis_mouse_down` | `session_id, button?, x?, y?` | Press a mouse button at the given coordinates. |
| `wavexis_mouse_move` | `session_id, selector` | Move the mouse to an element matching a CSS selector. |
| `wavexis_mouse_move_xy` | `session_id, x, y` | Move the mouse to absolute pixel coordinates. |
| `wavexis_mouse_up` | `session_id, button?, x?, y?` | Release a mouse button at the given coordinates. |
| `wavexis_mouse_wheel` | `session_id, x?, y?, delta_x?, delta_y?` | Simulate a mouse wheel (scroll) event at the given coordinates. |
