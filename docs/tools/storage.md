# Storage Tools (18)

Enable with `--caps=storage`.

These 18 tools are added when the `storage` capability tier is enabled.

## Storage

| Tool | Parameters | Description |
| --- | --- | --- |
| `wavexis_cache_storage_delete` | `cache_name, session_id` | Delete a Cache Storage cache. |
| `wavexis_cache_storage_entries` | `cache_name, session_id` | List entries in a Cache Storage cache. |
| `wavexis_cache_storage_list` | `session_id` | List all Cache Storage cache names. |
| `wavexis_indexeddb_clear` | `database, store, session_id` | Clear an IndexedDB object store. |
| `wavexis_indexeddb_get_data` | `database, store, key?, session_id` | Get data from an IndexedDB object store. |
| `wavexis_indexeddb_list` | `session_id` | List all IndexedDB databases and their object stores. |
| `wavexis_localstorage_clear` | `session_id` | Clear all localStorage entries. |
| `wavexis_localstorage_delete` | `key, session_id` | Delete a localStorage key. |
| `wavexis_localstorage_get` | `key, session_id` | Get a localStorage value by key. |
| `wavexis_localstorage_list` | `session_id` | List all localStorage entries. |
| `wavexis_localstorage_set` | `key, value, session_id` | Set a localStorage key/value pair. |
| `wavexis_sessionstorage_clear` | `session_id` | Clear all sessionStorage entries. |
| `wavexis_sessionstorage_delete` | `key, session_id` | Delete a sessionStorage key. |
| `wavexis_sessionstorage_get` | `key, session_id` | Get a sessionStorage value by key. |
| `wavexis_sessionstorage_list` | `session_id` | List all sessionStorage entries. |
| `wavexis_sessionstorage_set` | `key, value, session_id` | Set a sessionStorage key/value pair. |
| `wavexis_storage_state_restore` | `session_id, input_path` | Restore cookies + localStorage + sessionStorage from a JSON file. |
| `wavexis_storage_state_save` | `session_id, output_path` | Save cookies + localStorage + sessionStorage to a JSON file. |
