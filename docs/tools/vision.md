# Vision Tools (7)

Enable with `--caps=vision`.

Lighthouse audits, WebAuthn, Bluetooth, and Cast. Enable with `--caps=vision`.

## Summary

| Tool | Parameters | Description |
| --- | --- | --- |
| [`wavexis_mouse_click_xy`](#wavexis_mouse_click_xy) | `session_id, x, y, button?, click_count?` | Click at absolute pixel coordinates (press + release). |
| [`wavexis_mouse_double_click_xy`](#wavexis_mouse_double_click_xy) | `session_id, x, y, button?` | Double-click at absolute pixel coordinates. |
| [`wavexis_mouse_down`](#wavexis_mouse_down) | `session_id, button?, x?, y?` | Press a mouse button at the given coordinates. |
| [`wavexis_mouse_move`](#wavexis_mouse_move) | `session_id, selector` | Move the mouse to an element matching a CSS selector. |
| [`wavexis_mouse_move_xy`](#wavexis_mouse_move_xy) | `session_id, x, y` | Move the mouse to absolute pixel coordinates. |
| [`wavexis_mouse_up`](#wavexis_mouse_up) | `session_id, button?, x?, y?` | Release a mouse button at the given coordinates. |
| [`wavexis_mouse_wheel`](#wavexis_mouse_wheel) | `session_id, x?, y?, delta_x?, delta_y?` | Simulate a mouse wheel (scroll) event at the given coordinates. |

## Vision

### wavexis_mouse_click_xy

Click at absolute pixel coordinates (press + release).

Args:
    input: Click parameters (x, y, button, click_count).

Returns:
    JSON string with status ``"ok"`` and coordinates.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `x` | integer | Yes | — | X coordinate |
| `y` | integer | Yes | — | Y coordinate |
| `button` | string (left, right, middle) | No | `"left"` | Mouse button: left, right, or middle |
| `click_count` | integer | No | `1` | Number of clicks to perform |

### wavexis_mouse_double_click_xy

Double-click at absolute pixel coordinates.

Args:
    input: Double-click parameters (x, y, button).

Returns:
    JSON string with status ``"ok"`` and coordinates.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `x` | integer | Yes | — | X coordinate |
| `y` | integer | Yes | — | Y coordinate |
| `button` | string (left, right, middle) | No | `"left"` | Mouse button: left, right, or middle |

### wavexis_mouse_down

Press a mouse button at the given coordinates.

Args:
    input: Mouse down parameters (button, x, y).

Returns:
    JSON string with status ``"ok"``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `button` | string (left, right, middle) | No | `"left"` | Mouse button: left, right, or middle |
| `x` | integer | No | `0` | X coordinate |
| `y` | integer | No | `0` | Y coordinate |

### wavexis_mouse_move

Move the mouse to an element matching a CSS selector.

Args:
    input: Mouse move parameters (selector).

Returns:
    JSON string with status ``"ok"`` and ``selector``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `selector` | string | Yes | — | CSS selector for the target element |

### wavexis_mouse_move_xy

Move the mouse to absolute pixel coordinates.

Args:
    input: Mouse move parameters (x, y).

Returns:
    JSON string with status ``"ok"`` and coordinates.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `x` | integer | Yes | — | X coordinate in CSS pixels |
| `y` | integer | Yes | — | Y coordinate in CSS pixels |

### wavexis_mouse_up

Release a mouse button at the given coordinates.

Args:
    input: Mouse up parameters (button, x, y).

Returns:
    JSON string with status ``"ok"``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `button` | string (left, right, middle) | No | `"left"` | Mouse button: left, right, or middle |
| `x` | integer | No | `0` | X coordinate |
| `y` | integer | No | `0` | Y coordinate |

### wavexis_mouse_wheel

Simulate a mouse wheel (scroll) event at the given coordinates.

Args:
    input: Mouse wheel parameters (x, y, delta_x, delta_y).

Returns:
    JSON string with status ``"ok"`` and scroll amounts.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `x` | integer | No | `0` | X coordinate of the wheel event |
| `y` | integer | No | `0` | Y coordinate of the wheel event |
| `delta_x` | integer | No | `0` | Horizontal scroll amount |
| `delta_y` | integer | No | `0` | Vertical scroll amount |
