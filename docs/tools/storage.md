# Storage Tools (13)

Enable with `--caps=storage`.

Storage tools provide full CRUD access to browser storage mechanisms: localStorage, sessionStorage, and Cache Storage. Additionally, the storage state save/restore tools export the entire browser state (cookies + all storage) as JSON for later restoration.

Useful for preserving authentication state between sessions, testing storage-dependent features, and debugging storage issues.

## localStorage

Persistent key-value storage scoped per origin. Survives browser restarts.

| Tool | Parameters | Description |
| --- | --- | --- |
| `wavexis_localstorage_get` | `session_id`, `key` | Get a localStorage item by key. Returns `null` if key doesn't exist. |
| `wavexis_localstorage_set` | `session_id`, `key`, `value` | Set a localStorage item. Creates or overwrites. |
| `wavexis_localstorage_delete` | `session_id`, `key` | Delete a localStorage item by key. |
| `wavexis_localstorage_clear` | `session_id` | Clear all localStorage for the current origin. |
| `wavexis_localstorage_list` | `session_id` | List all localStorage keys and values for the current origin. |

## sessionStorage

Key-value storage scoped per origin AND per tab. Cleared when the tab is closed.

| Tool | Parameters | Description |
| --- | --- | --- |
| `wavexis_sessionstorage_get` | `session_id`, `key` | Get a sessionStorage item by key. |
| `wavexis_sessionstorage_set` | `session_id`, `key`, `value` | Set a sessionStorage item. |
| `wavexis_sessionstorage_delete` | `session_id`, `key` | Delete a sessionStorage item. |
| `wavexis_sessionstorage_clear` | `session_id` | Clear all sessionStorage for the current origin. |
| `wavexis_sessionstorage_list` | `session_id` | List all sessionStorage keys and values. |

## Cache Storage

Stores `Request`/`Response` pairs for use by Service Workers. Used by PWAs for offline access.

| Tool | Parameters | Description |
| --- | --- | --- |
| `wavexis_cache_storage_list` | `session_id` | List all Cache Storage entries (cache names and their contents). |
| `wavexis_cache_storage_delete` | `session_id`, `cache_name` | Delete a specific cache by name. |

## State save/restore

Export and import the full browser state — cookies, localStorage, sessionStorage — as a single JSON blob. Useful for session persistence across restarts.

| Tool | Parameters | Description |
| --- | --- | --- |
| `wavexis_storage_state_save` | `session_id`, `output_path` | Save the full storage state (cookies + localStorage + sessionStorage) to a JSON file. |
| `wavexis_storage_state_restore` | `session_id`, `state` | Restore a previously saved storage state. `state`: JSON string or file path. |

!!! example "Save and restore auth state"
    ```text
    # Session 1: Log in and save state
    wavexis_session_open(backend="cdp")
    wavexis_navigate(session_id="s1", url="https://app.example.com/login")
    wavexis_fill(session_id="s1", selector="#email", value="user@example.com")
    wavexis_click(session_id="s1", selector="#submit")
    wavexis_storage_state_save(session_id="s1", output_path="./auth-state.json")
    wavexis_session_close(session_id="s1")

    # Session 2: Restore state — already logged in
    wavexis_session_open(backend="cdp")
    wavexis_storage_state_restore(session_id="s2", state="./auth-state.json")
    wavexis_navigate(session_id="s2", url="https://app.example.com/dashboard")
    wavexis_session_close(session_id="s2")
    ```
