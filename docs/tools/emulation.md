# Emulation Tools (9)

Enable with `--caps=emulation`.

Emulation tools simulate devices and environments. Emulate specific phones (iPhone 15, Pixel 8) with correct viewport, user agent, and touch events. Override geolocation, timezone, dark mode, locale, CPU throttling, and sensor values.

Essential for responsive testing, geo-dependent features, and performance testing under device constraints.

| Tool | Parameters | Description |
| --- | --- | --- |
| `wavexis_emulate_device` | `session_id`, `device` | Emulate a specific device. Presets: `iPhone 15`, `iPhone 15 Pro`, `Pixel 8`, `iPad Pro`, `Galaxy S24`, and more. Sets viewport, UA, device pixel ratio, and touch. |
| `wavexis_set_viewport` | `session_id`, `width`, `height`, `device_scale_factor`, `is_mobile` | Set a custom viewport size. `device_scale_factor`: 1, 2, 3. `is_mobile`: enables touch events and mobile UA. |
| `wavexis_set_geolocation` | `session_id`, `latitude`, `longitude`, `accuracy` | Override the browser's geolocation. `accuracy`: meters (default 100). The page must request geolocation permission first. |
| `wavexis_set_timezone` | `session_id`, `timezone` | Override the browser's timezone. Accepts IANA timezone names (e.g., `America/New_York`, `Europe/London`, `Asia/Tokyo`). |
| `wavexis_set_dark_mode` | `session_id`, `enabled` | Enable or disable dark mode emulation. When `true`, the browser reports `prefers-color-scheme: dark` to CSS media queries. |
| `wavexis_set_locale` | `session_id`, `locale` | Override the browser's locale. Accepts BCP 47 tags (e.g., `en-US`, `es-ES`, `ja-JP`). Affects `navigator.language` and `Accept-Language` header. |
| `wavexis_set_cpu_throttling` | `session_id`, `rate` | Throttle CPU. `rate`: multiplier (e.g., `4` = 4x slower). Simulates low-end devices. Useful for performance testing. |
| `wavexis_set_touch` | `session_id`, `enabled` | Enable or disable touch emulation. When enabled, mouse events are translated to touch events. |
| `wavexis_set_sensors` | `session_id`, `sensor`, `values` | Set sensor values. `sensor`: `accelerometer` or `gyroscope`. `values`: dict with `x`, `y`, `z` axes. |

!!! example "Test responsive layout on iPhone 15"
    ```text
    wavexis_session_open(backend="cdp")
    wavexis_emulate_device(session_id="abc-123", device="iPhone 15")
    wavexis_navigate(session_id="abc-123", url="https://example.com")
    wavexis_screenshot(session_id="abc-123", full_page=true)
    wavexis_session_close(session_id="abc-123")
    ```

!!! example "Test geo-dependent feature"
    ```text
    wavexis_session_open(backend="cdp")
    wavexis_set_geolocation(session_id="abc-123", latitude=35.6762, longitude=139.6503)
    wavexis_set_locale(session_id="abc-123", locale="ja-JP")
    wavexis_set_timezone(session_id="abc-123", timezone="Asia/Tokyo")
    wavexis_navigate(session_id="abc-123", url="https://example.com")
    wavexis_session_close(session_id="abc-123")
    ```
