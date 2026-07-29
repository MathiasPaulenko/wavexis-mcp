# Experimental Tools (31)

Enable with `--caps=experimental`.

Experimental and advanced tools — raw protocol access, CDP/BiDi escape hatch. Enable with `--caps=experimental`.

## Summary

| Tool | Parameters | Description |
| --- | --- | --- |
| [`wavexis_animation_list`](#wavexis_animation_list) | `session_id` | List all active animations on the page. |
| [`wavexis_animation_pause`](#wavexis_animation_pause) | `session_id, animation_id` | Pause an animation by ID. |
| [`wavexis_animation_play`](#wavexis_animation_play) | `session_id, animation_id` | Play/resume an animation by ID. |
| [`wavexis_animation_set_rate`](#wavexis_animation_set_rate) | `session_id, animation_id, playback_rate?` | Set the playback rate of an animation. |
| [`wavexis_bluetooth_adapter_state`](#wavexis_bluetooth_adapter_state) | `session_id, state` | Set Bluetooth adapter state (powered on/off). |
| [`wavexis_bluetooth_device_connect`](#wavexis_bluetooth_device_connect) | `session_id, name, address?` | Emulate a Bluetooth device connection. |
| [`wavexis_bluetooth_device_disconnect`](#wavexis_bluetooth_device_disconnect) | `session_id` | Stop Bluetooth emulation. |
| [`wavexis_bluetooth_device_list`](#wavexis_bluetooth_device_list) | `session_id` | List emulated Bluetooth devices. |
| [`wavexis_cast_list`](#wavexis_cast_list) | `session_id` | List available cast sinks. |
| [`wavexis_cast_start`](#wavexis_cast_start) | `session_id, sink_name` | Start tab mirroring to a cast sink. |
| [`wavexis_cast_stop`](#wavexis_cast_stop) | `session_id` | Stop active cast mirroring. |
| [`wavexis_extension_install`](#wavexis_extension_install) | `session_id, path` | Install a browser extension from a .crx or unpacked directory. |
| [`wavexis_extension_list`](#wavexis_extension_list) | `session_id` | List installed browser extensions. |
| [`wavexis_extension_uninstall`](#wavexis_extension_uninstall) | `session_id, extension_id` | Uninstall a browser extension by ID. |
| [`wavexis_get_pref`](#wavexis_get_pref) | `session_id, key` | Get a browser preference value by key. |
| [`wavexis_media_get_messages`](#wavexis_media_get_messages) | `session_id, player_id` | Get messages for a specific media player. |
| [`wavexis_media_get_players`](#wavexis_media_get_players) | `session_id` | List all media players on the page. |
| [`wavexis_media_player_pause`](#wavexis_media_player_pause) | `session_id, player_id` | Pause a media player by ID. |
| [`wavexis_media_player_play`](#wavexis_media_player_play) | `session_id, player_id` | Play a media player by ID. |
| [`wavexis_media_player_seek`](#wavexis_media_player_seek) | `session_id, player_id, time_ms` | Seek a media player to a specific time. |
| [`wavexis_service_worker_emulate`](#wavexis_service_worker_emulate) | `session_id, script_url` | Emulate a service worker with a script URL. |
| [`wavexis_service_worker_list`](#wavexis_service_worker_list) | `session_id` | List registered service workers. |
| [`wavexis_service_worker_unregister`](#wavexis_service_worker_unregister) | `session_id, registration_id` | Unregister a service worker. |
| [`wavexis_service_worker_update`](#wavexis_service_worker_update) | `session_id, registration_id` | Trigger an update for a service worker registration. |
| [`wavexis_set_pref`](#wavexis_set_pref) | `session_id, key, value` | Set a browser preference value. |
| [`wavexis_webaudio_capture`](#wavexis_webaudio_capture) | `session_id, context_id?` | Capture WebAudio context data. |
| [`wavexis_webaudio_stop_capture`](#wavexis_webaudio_stop_capture) | `session_id` | Stop WebAudio capture. |
| [`wavexis_webauthn_add_authenticator`](#wavexis_webauthn_add_authenticator) | `session_id, protocol?, transport?` | Add a virtual WebAuthn authenticator for testing. |
| [`wavexis_webauthn_add_credential`](#wavexis_webauthn_add_credential) | `session_id, authenticator_id, credential` | Add a credential to a virtual authenticator. |
| [`wavexis_webauthn_get_credential`](#wavexis_webauthn_get_credential) | `session_id, authenticator_id` | Get credentials from a virtual authenticator. |
| [`wavexis_webauthn_remove_credential`](#wavexis_webauthn_remove_credential) | `session_id, authenticator_id` | Remove a virtual authenticator. |

## Experimental

### wavexis_animation_list

List all active animations on the page.

Args:
    input: List parameters (session_id).

Returns:
    JSON string with ``animations`` list and ``count``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |

### wavexis_animation_pause

Pause an animation by ID.

Args:
    input: Animation pause parameters (session_id, animation_id).

Returns:
    JSON string with status ``"ok"``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `animation_id` | string | Yes | — | Animation ID |

### wavexis_animation_play

Play/resume an animation by ID.

Args:
    input: Animation play parameters (session_id, animation_id).

Returns:
    JSON string with status ``"ok"``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `animation_id` | string | Yes | — | Animation ID |

### wavexis_animation_set_rate

Set the playback rate of an animation.

Args:
    input: Animation rate parameters (session_id, animation_id, playback_rate).

Returns:
    JSON string with status ``"ok"`` and ``playback_rate``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `animation_id` | string | Yes | — | Animation ID |
| `playback_rate` | number | No | `1.0` | Playback rate multiplier |

### wavexis_bluetooth_adapter_state

Set Bluetooth adapter state (powered on/off).

Args:
    input: Adapter state parameters (session_id, state).

Returns:
    JSON string with status ``"ok"`` and ``state``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `state` | string | Yes | — | Adapter state: 'powered-on' or 'powered-off' |

### wavexis_bluetooth_device_connect

Emulate a Bluetooth device connection.

Args:
    input: Device connect parameters (session_id, name, address).

Returns:
    JSON string with status ``"ok"`` and device info.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `name` | string | Yes | — | Device name |
| `address` | string | No | `"00:00:00:00:00:01"` | Device MAC address |

### wavexis_bluetooth_device_disconnect

Stop Bluetooth emulation.

Args:
    input: Disconnect parameters (session_id).

Returns:
    JSON string with status ``"ok"``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |

### wavexis_bluetooth_device_list

List emulated Bluetooth devices.

Args:
    input: List parameters (session_id).

Returns:
    JSON string with ``devices`` list.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |

### wavexis_cast_list

List available cast sinks.

Args:
    input: List parameters (session_id).

Returns:
    JSON string with ``sinks`` list and ``count``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |

### wavexis_cast_start

Start tab mirroring to a cast sink.

Args:
    input: Cast start parameters (session_id, sink_name).

Returns:
    JSON string with status ``"ok"``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `sink_name` | string | Yes | — | Cast sink name |

### wavexis_cast_stop

Stop active cast mirroring.

Args:
    input: Cast stop parameters (session_id).

Returns:
    JSON string with status ``"ok"``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |

### wavexis_extension_install

Install a browser extension from a .crx or unpacked directory.

Args:
    input: Extension install parameters (path).

Returns:
    JSON string with ``extension_id``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `path` | string | Yes | — | Path to .crx file or unpacked extension directory |

### wavexis_extension_list

List installed browser extensions.

Args:
    input: Session reference parameters.

Returns:
    JSON string with ``extensions`` list and ``count``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |

### wavexis_extension_uninstall

Uninstall a browser extension by ID.

Args:
    input: Extension uninstall parameters (extension_id).

Returns:
    JSON string with status ``"ok"``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `extension_id` | string | Yes | — | Extension ID returned by extension_install |

### wavexis_get_pref

Get a browser preference value by key.

Args:
    input: Preference parameters (key).

Returns:
    JSON string with ``key`` and ``value``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `key` | string | Yes | — | Preference key (e.g. 'download.default_directory') |

### wavexis_media_get_messages

Get messages for a specific media player.

Args:
    input: Message parameters (session_id, player_id).

Returns:
    JSON string with ``messages`` list and ``count``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `player_id` | string | Yes | — | Media player ID |

### wavexis_media_get_players

List all media players on the page.

Args:
    input: List parameters (session_id).

Returns:
    JSON string with ``players`` list and ``count``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |

### wavexis_media_player_pause

Pause a media player by ID.

Args:
    input: Pause parameters (session_id, player_id).

Returns:
    JSON string with status ``"ok"``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `player_id` | string | Yes | — | Media player ID |

### wavexis_media_player_play

Play a media player by ID.

Args:
    input: Play parameters (session_id, player_id).

Returns:
    JSON string with status ``"ok"``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `player_id` | string | Yes | — | Media player ID |

### wavexis_media_player_seek

Seek a media player to a specific time.

Args:
    input: Seek parameters (session_id, player_id, time_ms).

Returns:
    JSON string with status ``"ok"`` and ``time_ms``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `player_id` | string | Yes | — | Media player ID |
| `time_ms` | integer | Yes | — | Seek time in milliseconds |

### wavexis_service_worker_emulate

Emulate a service worker with a script URL.

Args:
    input: Emulate parameters (session_id, script_url).

Returns:
    JSON string with status ``"ok"``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `script_url` | string | Yes | — | Script URL for the emulated service worker |

### wavexis_service_worker_list

List registered service workers.

Args:
    input: List parameters (session_id).

Returns:
    JSON string with ``workers`` list and ``count``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |

### wavexis_service_worker_unregister

Unregister a service worker.

Args:
    input: Unregister parameters (session_id, registration_id).

Returns:
    JSON string with status ``"ok"``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `registration_id` | string | Yes | — | Service worker registration ID |

### wavexis_service_worker_update

Trigger an update for a service worker registration.

Args:
    input: Update parameters (session_id, registration_id).

Returns:
    JSON string with status ``"ok"``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `registration_id` | string | Yes | — | Service worker registration ID |

### wavexis_set_pref

Set a browser preference value.

Args:
    input: Preference parameters (key, value).

Returns:
    JSON string with status ``"ok"``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `key` | string | Yes | — | Preference key |
| `value` | string | Yes | — | Preference value to set |

### wavexis_webaudio_capture

Capture WebAudio context data.

Args:
    input: Capture parameters (session_id, context_id).

Returns:
    JSON string with ``contexts`` list.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `context_id` | string | No | `null` | Specific context ID (empty = all) |

### wavexis_webaudio_stop_capture

Stop WebAudio capture.

Args:
    input: Stop parameters (session_id).

Returns:
    JSON string with status ``"ok"``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |

### wavexis_webauthn_add_authenticator

Add a virtual WebAuthn authenticator for testing.

Args:
    input: Authenticator parameters (session_id, protocol, transport).

Returns:
    JSON string with ``authenticator_id``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `protocol` | string | No | `"ctap2"` | Authenticator protocol: 'ctap2' or 'u2f' |
| `transport` | string | No | `"usb"` | Transport type: 'usb', 'nfc', 'ble', 'internal' |

### wavexis_webauthn_add_credential

Add a credential to a virtual authenticator.

Args:
    input: Add credential parameters (session_id, authenticator_id, credential).

Returns:
    JSON string with status ``"ok"``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `authenticator_id` | string | Yes | — | WebAuthn authenticator ID |
| `credential` | object | Yes | — | WebAuthn credential to add |

### wavexis_webauthn_get_credential

Get credentials from a virtual authenticator.

Args:
    input: Get credentials parameters (session_id, authenticator_id).

Returns:
    JSON string with ``credentials`` list.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `authenticator_id` | string | Yes | — | WebAuthn authenticator ID |

### wavexis_webauthn_remove_credential

Remove a virtual authenticator.

Args:
    input: Remove authenticator parameters (session_id, authenticator_id).

Returns:
    JSON string with status ``"ok"``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `authenticator_id` | string | Yes | — | WebAuthn authenticator ID |
