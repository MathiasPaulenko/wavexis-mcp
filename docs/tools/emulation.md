# Emulation Tools (9)

Enable with `--caps=emulation`.

These 9 tools are added when the `emulation` capability tier is enabled.

## Emulation

| Tool | Parameters | Description |
| --- | --- | --- |
| `wavexis_emulate_device` | `session_id, device` | Emulate a specific device (iphone-15, pixel-8, etc.). |
| `wavexis_set_cpu_throttle` | `session_id, rate` | Enable CPU throttling at a given multiplier. |
| `wavexis_set_dark_mode` | `session_id, enabled?` | Enable or disable dark mode emulation. |
| `wavexis_set_geolocation` | `session_id, latitude, longitude, accuracy?` | Override the browser geolocation. |
| `wavexis_set_locale` | `session_id, locale` | Override the browser locale. |
| `wavexis_set_sensors` | `session_id, sensor_type, values` | Override sensor values (orientation, motion, light, proximity). |
| `wavexis_set_timezone` | `session_id, timezone` | Override the browser timezone. |
| `wavexis_set_touch_emulation` | `session_id, enabled?` | Enable or disable touch event emulation. |
| `wavexis_set_viewport` | `session_id, width, height, device_scale_factor?` | Set a custom viewport size and scale factor. |
