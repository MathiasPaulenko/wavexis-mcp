# Experimental Tools (31)

Enable with `--caps=experimental`.

These 31 tools are added when the `experimental` capability tier is enabled.

## Experimental

| Tool | Parameters | Description |
| --- | --- | --- |
| `wavexis_animation_list` | `session_id` | List all active animations on the page. |
| `wavexis_animation_pause` | `session_id, animation_id` | Pause an animation by ID. |
| `wavexis_animation_play` | `session_id, animation_id` | Play/resume an animation by ID. |
| `wavexis_animation_set_rate` | `session_id, animation_id, playback_rate?` | Set the playback rate of an animation. |
| `wavexis_bluetooth_adapter_state` | `session_id, state` | Set Bluetooth adapter state (powered on/off). |
| `wavexis_bluetooth_device_connect` | `session_id, name, address?` | Emulate a Bluetooth device connection. |
| `wavexis_bluetooth_device_disconnect` | `session_id` | Stop Bluetooth emulation. |
| `wavexis_bluetooth_device_list` | `session_id` | List emulated Bluetooth devices. |
| `wavexis_cast_list` | `session_id` | List available cast sinks. |
| `wavexis_cast_start` | `session_id, sink_name` | Start tab mirroring to a cast sink. |
| `wavexis_cast_stop` | `session_id` | Stop active cast mirroring. |
| `wavexis_extension_install` | `session_id, path` | Install a browser extension from a .crx or unpacked directory. |
| `wavexis_extension_list` | `session_id` | List installed browser extensions. |
| `wavexis_extension_uninstall` | `session_id, extension_id` | Uninstall a browser extension by ID. |
| `wavexis_get_pref` | `session_id, key` | Get a browser preference value by key. |
| `wavexis_media_get_messages` | `session_id, player_id` | Get messages for a specific media player. |
| `wavexis_media_get_players` | `session_id` | List all media players on the page. |
| `wavexis_media_player_pause` | `session_id, player_id` | Pause a media player by ID. |
| `wavexis_media_player_play` | `session_id, player_id` | Play a media player by ID. |
| `wavexis_media_player_seek` | `session_id, player_id, time_ms` | Seek a media player to a specific time. |
| `wavexis_service_worker_emulate` | `session_id, script_url` | Emulate a service worker with a script URL. |
| `wavexis_service_worker_list` | `session_id` | List registered service workers. |
| `wavexis_service_worker_unregister` | `session_id, registration_id` | Unregister a service worker. |
| `wavexis_service_worker_update` | `session_id, registration_id` | Trigger an update for a service worker registration. |
| `wavexis_set_pref` | `session_id, key, value` | Set a browser preference value. |
| `wavexis_webaudio_capture` | `session_id, context_id?` | Capture WebAudio context data. |
| `wavexis_webaudio_stop_capture` | `session_id` | Stop WebAudio capture. |
| `wavexis_webauthn_add_authenticator` | `session_id, protocol?, transport?` | Add a virtual WebAuthn authenticator for testing. |
| `wavexis_webauthn_add_credential` | `session_id, authenticator_id, credential` | Add a credential to a virtual authenticator. |
| `wavexis_webauthn_get_credential` | `session_id, authenticator_id` | Get credentials from a virtual authenticator. |
| `wavexis_webauthn_remove_credential` | `session_id, authenticator_id` | Remove a virtual authenticator. |
