# Workflows Tools (6)

Enable with `--caps=workflows`.

Multi-action YAML batching and natural language interaction. Enable with `--caps=workflows`.

## Summary

| Tool | Parameters | Description |
| --- | --- | --- |
| [`wavexis_browser_context_close`](#wavexis_browser_context_close) | `session_id, context_id` | Close an isolated browser context. |
| [`wavexis_browser_context_create`](#wavexis_browser_context_create) | `session_id` | Create an isolated browser context within a session. |
| [`wavexis_browser_context_list`](#wavexis_browser_context_list) | `session_id` | List all browser contexts in a session. |
| [`wavexis_multi_action`](#wavexis_multi_action) | `config, session_id?, backend?, headless?, continue_on_error?` | Execute multiple actions from a YAML config sequentially. |
| [`wavexis_raw_bidi`](#wavexis_raw_bidi) | `session_id, method, params?` | Send a raw BiDi command (escape hatch). |
| [`wavexis_raw_cdp`](#wavexis_raw_cdp) | `session_id, method, params?` | Send a raw CDP command (escape hatch). |

## Workflows

### wavexis_browser_context_close

Close an isolated browser context.

Args:
    input: Context close parameters (session_id, context_id).

Returns:
    JSON string with status ``"ok"``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `context_id` | string | Yes | — | Execution context ID |

### wavexis_browser_context_create

Create an isolated browser context within a session.

Args:
    input: Context creation parameters (session_id).

Returns:
    JSON string with ``context_id``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |

### wavexis_browser_context_list

List all browser contexts in a session.

Args:
    input: List contexts parameters (session_id).

Returns:
    JSON string with ``contexts`` list and ``count``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |

### wavexis_multi_action

Execute multiple actions from a YAML config sequentially.

Args:
    input: Multi-action parameters (YAML config, continue_on_error).

Returns:
    JSON string with ``actions`` count, ``results``, and ``errors``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `config` | string | Yes | — | YAML config string (not file path) |
| `session_id` | string | No | `null` | Active session ID. If omitted, a stateless session is created for this call. |
| `backend` | string (cdp, bidi, auto) | No | `"cdp"` | Backend: 'cdp', 'bidi', or 'auto' |
| `headless` | boolean | No | `true` | Run browser in headless mode |
| `continue_on_error` | boolean | No | `false` | Continue on action errors |

### wavexis_raw_bidi

Send a raw BiDi command (escape hatch).

Args:
    input: Raw BiDi parameters (method, params).

Returns:
    JSON string with raw ``result`` from the BiDi command.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `method` | string | Yes | — | BiDi command (e.g. 'browsingContext.navigate') |
| `params` | object | No | `null` | Parameters to pass to the CDP/BiDi method |

### wavexis_raw_cdp

Send a raw CDP command (escape hatch).

Args:
    input: Raw CDP parameters (method, params).

Returns:
    JSON string with raw ``result`` from the CDP command.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `method` | string | Yes | — | CDP method (e.g. 'Page.reload') |
| `params` | object | No | `null` | Parameters to pass to the CDP/BiDi method |
