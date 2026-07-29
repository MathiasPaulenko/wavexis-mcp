# Emulation Tools (9)

Enable with `--caps=emulation`.

Device emulation, geolocation spoofing, timezone override, and viewport manipulation. Enable with `--caps=emulation`.

## Summary

| Tool | Parameters | Description |
| --- | --- | --- |
| [`wavexis_emulate_device`](#wavexis_emulate_device) | `session_id, device` | Emulate a specific device (iphone-15, pixel-8, etc.). |
| [`wavexis_set_cpu_throttle`](#wavexis_set_cpu_throttle) | `session_id, rate` | Enable CPU throttling at a given multiplier. |
| [`wavexis_set_dark_mode`](#wavexis_set_dark_mode) | `session_id, enabled?` | Enable or disable dark mode emulation. |
| [`wavexis_set_geolocation`](#wavexis_set_geolocation) | `session_id, latitude, longitude, accuracy?` | Override the browser geolocation. |
| [`wavexis_set_locale`](#wavexis_set_locale) | `session_id, locale` | Override the browser locale. |
| [`wavexis_set_sensors`](#wavexis_set_sensors) | `session_id, sensor_type, values` | Override sensor values (orientation, motion, light, proximity). |
| [`wavexis_set_timezone`](#wavexis_set_timezone) | `session_id, timezone` | Override the browser timezone. |
| [`wavexis_set_touch_emulation`](#wavexis_set_touch_emulation) | `session_id, enabled?` | Enable or disable touch event emulation. |
| [`wavexis_set_viewport`](#wavexis_set_viewport) | `session_id, width, height, device_scale_factor?` | Set a custom viewport size and scale factor. |

## Emulation

### wavexis_emulate_device

Emulate a specific device (iphone-15, pixel-8, etc.).

Args:
    input: Device emulation parameters.

Returns:
    JSON string with status ``"ok"`` and ``device``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `device` | string | Yes | — | Device preset: iphone-15, iphone-se, pixel-8, ipad-pro, galaxy-s23, desktop-1080p, desktop-1440p |

### wavexis_set_cpu_throttle

Enable CPU throttling at a given multiplier.

Args:
    input: CPU throttle parameters (rate).

Returns:
    JSON string with status ``"ok"`` and ``rate``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `rate` | number | Yes | — | CPU throttle multiplier (e.g. 4 = 4x slower) |

### wavexis_set_dark_mode

Enable or disable dark mode emulation.

Args:
    input: Dark mode parameters.

Returns:
    JSON string with status ``"ok"`` and ``dark_mode``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `enabled` | boolean | No | `true` | Whether the feature is enabled |

### wavexis_set_geolocation

Override the browser geolocation.

Args:
    input: Geolocation parameters (latitude, longitude, accuracy).

Returns:
    JSON string with status ``"ok"`` and coordinates.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `latitude` | number | Yes | — | Geolocation latitude |
| `longitude` | number | Yes | — | Geolocation longitude |
| `accuracy` | number | No | `100.0` | Geolocation accuracy in meters |

### wavexis_set_locale

Override the browser locale.

Args:
    input: Locale parameters.

Returns:
    JSON string with status ``"ok"`` and ``locale``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `locale` | string | Yes | — | Locale code (e.g. 'en-US', 'fr-FR', 'ja-JP') |

### wavexis_set_sensors

Override sensor values (orientation, motion, light, proximity).

Args:
    input: Sensor parameters (sensor_type, values).

Returns:
    JSON string with status ``"ok"``, ``sensor_type``, and ``values``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `sensor_type` | string | Yes | — | Sensor type: 'orientation', 'motion', 'light', 'proximity' |
| `values` | object | Yes | — | Sensor values (e.g. {'alpha': 0, 'beta': 90, 'gamma': 0}) |

### wavexis_set_timezone

Override the browser timezone.

Args:
    input: Timezone parameters.

Returns:
    JSON string with status ``"ok"`` and ``timezone``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `timezone` | string | Yes | — | IANA timezone ID (e.g. 'America/New_York') |

### wavexis_set_touch_emulation

Enable or disable touch event emulation.

Args:
    input: Touch emulation parameters.

Returns:
    JSON string with status ``"ok"`` and ``touch_emulation``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `enabled` | boolean | No | `true` | Whether the feature is enabled |

### wavexis_set_viewport

Set a custom viewport size and scale factor.

Args:
    input: Viewport parameters (width, height, scale factor).

Returns:
    JSON string with status ``"ok"`` and viewport dimensions.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `width` | integer | Yes | — | Viewport width in pixels |
| `height` | integer | Yes | — | Viewport height in pixels |
| `device_scale_factor` | number | No | `1.0` | Device scale factor (DPR) |
