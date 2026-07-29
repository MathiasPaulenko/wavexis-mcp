# Storage Tools (18)

Enable with `--caps=storage`.

localStorage, sessionStorage, IndexedDB, and cache management. Enable with `--caps=storage`.

## Summary

| Tool | Parameters | Description |
| --- | --- | --- |
| [`wavexis_cache_storage_delete`](#wavexis_cache_storage_delete) | `cache_name, session_id` | Delete a Cache Storage cache. |
| [`wavexis_cache_storage_entries`](#wavexis_cache_storage_entries) | `cache_name, session_id` | List entries in a Cache Storage cache. |
| [`wavexis_cache_storage_list`](#wavexis_cache_storage_list) | `session_id` | List all Cache Storage cache names. |
| [`wavexis_indexeddb_clear`](#wavexis_indexeddb_clear) | `database, store, session_id` | Clear an IndexedDB object store. |
| [`wavexis_indexeddb_get_data`](#wavexis_indexeddb_get_data) | `database, store, key?, session_id` | Get data from an IndexedDB object store. |
| [`wavexis_indexeddb_list`](#wavexis_indexeddb_list) | `session_id` | List all IndexedDB databases and their object stores. |
| [`wavexis_localstorage_clear`](#wavexis_localstorage_clear) | `session_id` | Clear all localStorage entries. |
| [`wavexis_localstorage_delete`](#wavexis_localstorage_delete) | `key, session_id` | Delete a localStorage key. |
| [`wavexis_localstorage_get`](#wavexis_localstorage_get) | `key, session_id` | Get a localStorage value by key. |
| [`wavexis_localstorage_list`](#wavexis_localstorage_list) | `session_id` | List all localStorage entries. |
| [`wavexis_localstorage_set`](#wavexis_localstorage_set) | `key, value, session_id` | Set a localStorage key/value pair. |
| [`wavexis_sessionstorage_clear`](#wavexis_sessionstorage_clear) | `session_id` | Clear all sessionStorage entries. |
| [`wavexis_sessionstorage_delete`](#wavexis_sessionstorage_delete) | `key, session_id` | Delete a sessionStorage key. |
| [`wavexis_sessionstorage_get`](#wavexis_sessionstorage_get) | `key, session_id` | Get a sessionStorage value by key. |
| [`wavexis_sessionstorage_list`](#wavexis_sessionstorage_list) | `session_id` | List all sessionStorage entries. |
| [`wavexis_sessionstorage_set`](#wavexis_sessionstorage_set) | `key, value, session_id` | Set a sessionStorage key/value pair. |
| [`wavexis_storage_state_restore`](#wavexis_storage_state_restore) | `session_id, input_path` | Restore cookies + localStorage + sessionStorage from a JSON file. |
| [`wavexis_storage_state_save`](#wavexis_storage_state_save) | `session_id, output_path` | Save cookies + localStorage + sessionStorage to a JSON file. |

## Storage

### wavexis_cache_storage_delete

Delete a Cache Storage cache.

Args:
    input: Cache deletion parameters (cache_name).

Returns:
    JSON string with status ``"ok"`` and ``cache_name``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `cache_name` | string | Yes | — | Cache storage name |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |

### wavexis_cache_storage_entries

List entries in a Cache Storage cache.

Args:
    input: Cache entries parameters (cache_name).

Returns:
    JSON string with ``cache_name``, ``entries``, and ``count``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `cache_name` | string | Yes | — | Cache storage name |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |

### wavexis_cache_storage_list

List all Cache Storage cache names.

Args:
    input: Session reference parameters.

Returns:
    JSON string with ``caches`` list and ``count``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |

### wavexis_indexeddb_clear

Clear an IndexedDB object store.

Args:
    input: IndexedDB clear parameters (database, store).

Returns:
    JSON string with status ``"ok"``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `database` | string | Yes | — | IndexedDB database name |
| `store` | string | Yes | — | IndexedDB object store name |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |

### wavexis_indexeddb_get_data

Get data from an IndexedDB object store.

Args:
    input: IndexedDB query parameters (database, store, key).

Returns:
    JSON string with ``database``, ``store``, and ``data``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `database` | string | Yes | — | IndexedDB database name |
| `store` | string | Yes | — | Object store name |
| `key` | string | No | `""` | Specific key (empty = all entries) |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |

### wavexis_indexeddb_list

List all IndexedDB databases and their object stores.

Args:
    input: Session reference parameters.

Returns:
    JSON string with ``databases`` list and ``count``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |

### wavexis_localstorage_clear

Clear all localStorage entries.

Args:
    input: Session reference parameters.

Returns:
    JSON string with status ``"ok"``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |

### wavexis_localstorage_delete

Delete a localStorage key.

Args:
    input: LocalStorage delete parameters.

Returns:
    JSON string with status ``"ok"``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `key` | string | Yes | — | Storage key |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |

### wavexis_localstorage_get

Get a localStorage value by key.

Args:
    input: LocalStorage get parameters.

Returns:
    JSON string with ``key`` and ``value``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `key` | string | Yes | — | Storage key |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |

### wavexis_localstorage_list

List all localStorage entries.

Args:
    input: Session reference parameters.

Returns:
    JSON string with ``entries`` dict and ``count``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |

### wavexis_localstorage_set

Set a localStorage key/value pair.

Args:
    input: LocalStorage set parameters.

Returns:
    JSON string with status ``"ok"``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `key` | string | Yes | — | Storage key |
| `value` | string | Yes | — | Storage value |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |

### wavexis_sessionstorage_clear

Clear all sessionStorage entries.

Args:
    input: Session reference parameters.

Returns:
    JSON string with status ``"ok"``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |

### wavexis_sessionstorage_delete

Delete a sessionStorage key.

Args:
    input: SessionStorage delete parameters.

Returns:
    JSON string with status ``"ok"``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `key` | string | Yes | — | Storage key |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |

### wavexis_sessionstorage_get

Get a sessionStorage value by key.

Args:
    input: SessionStorage get parameters.

Returns:
    JSON string with ``key`` and ``value``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `key` | string | Yes | — | Storage key |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |

### wavexis_sessionstorage_list

List all sessionStorage entries.

Args:
    input: Session reference parameters.

Returns:
    JSON string with ``entries`` dict and ``count``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |

### wavexis_sessionstorage_set

Set a sessionStorage key/value pair.

Args:
    input: SessionStorage set parameters.

Returns:
    JSON string with status ``"ok"``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `key` | string | Yes | — | Storage key |
| `value` | string | Yes | — | Storage value |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |

### wavexis_storage_state_restore

Restore cookies + localStorage + sessionStorage from a JSON file.

Args:
    input: Restore parameters (input_path).

Returns:
    JSON string with status ``"ok"`` and restored entry counts.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `input_path` | string | Yes | — | Path to saved state JSON file |

### wavexis_storage_state_save

Save cookies + localStorage + sessionStorage to a JSON file.

Args:
    input: Save parameters (output_path).

Returns:
    JSON string with ``path`` and entry counts.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `output_path` | string | Yes | — | File path to save state JSON |
