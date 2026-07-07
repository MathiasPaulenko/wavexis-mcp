# Experimental Tools (20)

Enable with `--caps=experimental`.

Experimental tools cover niche and advanced browser features that most users won't need daily but are invaluable when they do. This tier includes service worker management, animation control, WebAuthn virtual authenticators, WebAudio inspection, media player monitoring, Cast (Chromecast) control, Bluetooth emulation, browser extension management, and browser preference get/set.

These tools map directly to Chrome DevTools Protocol domains that are considered experimental or non-standard.

## Service Workers

Service workers are background scripts that control network requests, push notifications, and offline caching. These tools let you inspect and manage registered service workers.

| Tool | Parameters | Description |
| --- | --- | --- |
| `wavexis_sw_list` | `session_id` | List all registered service workers. Returns registration ID, script URL, state, and scope. |
| `wavexis_sw_unregister` | `session_id`, `registration_id` | Unregister a service worker by its registration ID. |
| `wavexis_sw_update` | `session_id`, `registration_id` | Trigger an update check for a service worker. The browser will fetch the script and compare versions. |

## Animations

Control CSS and JavaScript animations on the page. Pause, play, seek, and list all running animations.

| Tool | Parameters | Description |
| --- | --- | --- |
| `wavexis_animation_list` | `session_id` | List all running animations. Returns animation ID, name, duration, start time, and current state. |
| `wavexis_animation_pause` | `session_id` | Pause all animations on the page. |
| `wavexis_animation_play` | `session_id` | Resume all paused animations. |
| `wavexis_animation_seek` | `session_id`, `time` | Seek all animations to a specific time (in milliseconds). |

## WebAuthn

WebAuthn (Web Authentication) tools let you emulate virtual authenticators for testing passkey and FIDO2 flows without physical hardware.

| Tool | Parameters | Description |
| --- | --- | --- |
| `wavexis_webauthn_add_virtual_authenticator` | `session_id`, `protocol`, `transport` | Add a virtual authenticator. `protocol`: `ctap2` (default) or `u2f`. `transport`: `usb`, `nfc`, `ble`, `internal`. |
| `wavexis_webauthn_remove_authenticator` | `session_id`, `authenticator_id` | Remove a virtual authenticator by ID. |
| `wavexis_webauthn_add_credential` | `session_id`, `authenticator_id`, `credential` | Add a credential to a virtual authenticator. |
| `wavexis_webauthn_get_credentials` | `session_id`, `authenticator_id` | List all credentials for a virtual authenticator. |

## WebAudio

Inspect the Web Audio API graph. List audio contexts and get details about specific contexts.

| Tool | Parameters | Description |
| --- | --- | --- |
| `wavexis_webaudio_get_contexts` | `session_id` | List all WebAudio contexts. Returns context ID, state (running/suspended/closed), and sample rate. |
| `wavexis_webaudio_get_context` | `session_id`, `context_id` | Get detailed information about a specific WebAudio context, including nodes and connections. |

## Media

Monitor media players (video, audio) on the page. Useful for debugging playback issues.

| Tool | Parameters | Description |
| --- | --- | --- |
| `wavexis_media_get_players` | `session_id` | List all media players on the page. Returns player ID, URL, state, and duration. |
| `wavexis_media_get_messages` | `session_id`, `player_id` | Get media player messages (events, errors, state changes) for a specific player. |

## Cast

Control Cast (Chromecast) functionality. List available sinks and start/stop casting.

| Tool | Parameters | Description |
| --- | --- | --- |
| `wavexis_cast_list` | `session_id` | List available Cast sinks (Chromecast devices on the network). |
| `wavexis_cast_start_tab` | `session_id`, `sink_name` | Start casting the current tab to a sink. |
| `wavexis_cast_stop` | `session_id` | Stop the current Cast session. |

## Bluetooth

Emulate Bluetooth adapters for testing Web Bluetooth API without physical devices.

| Tool | Parameters | Description |
| --- | --- | --- |
| `wavexis_bluetooth_emulate` | `session_id`, `adapter` | Emulate a Bluetooth adapter. `adapter`: dict with `address`, `name`, `manufacturerData`, `knownDevices`. |
| `wavexis_bluetooth_stop` | `session_id` | Stop Bluetooth emulation and remove the virtual adapter. |

## Extensions

Manage browser extensions (Chrome extensions). Install, uninstall, and list loaded extensions. Useful for testing extension interactions or automating extension development.

| Tool | Parameters | Description |
| --- | --- | --- |
| `wavexis_extension_install` | `session_id`, `path` | Install a browser extension from a local directory path (must contain `manifest.json`). |
| `wavexis_extension_uninstall` | `session_id`, `extension_id` | Uninstall an extension by its ID. |
| `wavexis_extension_list` | `session_id` | List all installed extensions. Returns ID, name, version, and enabled state. |

!!! example "Install and test an extension"
    ```text
    wavexis_session_open(backend="cdp")
    wavexis_extension_install(session_id="abc-123", path="./my-extension")
    → {"extension_id": "abcdef...", "name": "My Extension", "version": "1.0.0"}
    wavexis_navigate(session_id="abc-123", url="https://example.com")
    # Extension is now active on the page
    wavexis_extension_list(session_id="abc-123")
    wavexis_extension_uninstall(session_id="abc-123", extension_id="abcdef...")
    wavexis_session_close(session_id="abc-123")
    ```

## Browser Preferences

Read and write browser-level preferences (Chrome/Edge internal settings). These are the same preferences found in `chrome://settings` and `edge://settings`. Useful for configuring browser behavior during automation.

| Tool | Parameters | Description |
| --- | --- | --- |
| `wavexis_get_pref` | `session_id`, `name` | Get a browser preference by name. Returns the current value. Preference names follow Chrome's internal naming (e.g., `profile.default_content_setting_values.images`). |
| `wavexis_set_pref` | `session_id`, `name`, `value` | Set a browser preference. `value` can be a string, number, boolean, or JSON object. Changes take effect immediately for most preferences. |

!!! example "Disable images for faster loading"
    ```text
    wavexis_session_open(backend="cdp")
    wavexis_set_pref(
        session_id="abc-123",
        name="profile.default_content_setting_values.images",
        value=2  # 1=allow, 2=block
    )
    wavexis_navigate(session_id="abc-123", url="https://example.com")
    # Page loads without images — faster for scraping
    wavexis_session_close(session_id="abc-123")
    ```
