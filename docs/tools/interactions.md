# Interactions Tools (5)

Enable with `--caps=interactions`.

Dialog handling, permission management, and download interception. Enable with `--caps=interactions`.

## Summary

| Tool | Parameters | Description |
| --- | --- | --- |
| [`wavexis_dialog_accept`](#wavexis_dialog_accept) | `session_id, prompt_text?` | Accept a JavaScript dialog (alert, confirm, prompt). |
| [`wavexis_dialog_dismiss`](#wavexis_dialog_dismiss) | `session_id` | Dismiss a JavaScript dialog. |
| [`wavexis_grant_permission`](#wavexis_grant_permission) | `session_id, permission` | Grant a browser permission (geolocation, notifications, etc.). |
| [`wavexis_intercept_download`](#wavexis_intercept_download) | `session_id, pattern?, output_path?` | Intercept a download matching a URL pattern. |
| [`wavexis_reset_permissions`](#wavexis_reset_permissions) | `session_id` | Reset all granted permissions. |

## Interactions

### wavexis_dialog_accept

Accept a JavaScript dialog (alert, confirm, prompt).

Args:
    input: Dialog accept parameters (prompt_text).

Returns:
    JSON string with status ``"ok"``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `prompt_text` | string | No | `null` | Text for prompt dialogs |

### wavexis_dialog_dismiss

Dismiss a JavaScript dialog.

Args:
    input: Dialog dismiss parameters.

Returns:
    JSON string with status ``"ok"``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |

### wavexis_grant_permission

Grant a browser permission (geolocation, notifications, etc.).

Args:
    input: Permission parameters.

Returns:
    JSON string with status ``"ok"`` and ``permission``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `permission` | string | Yes | — | Permission name: geolocation, notifications, camera, microphone, etc. |

### wavexis_intercept_download

Intercept a download matching a URL pattern.

Args:
    input: Download interception parameters (pattern, output_path).

Returns:
    JSON string with file path or base64 data and size.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `pattern` | string | No | `".*"` | URL pattern to match |
| `output_path` | string | No | `null` | Save to file instead of returning base64 |

### wavexis_reset_permissions

Reset all granted permissions.

Args:
    input: Session reference parameters.

Returns:
    JSON string with status ``"ok"``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
