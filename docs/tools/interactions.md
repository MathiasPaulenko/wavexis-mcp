# Interactions Tools (5)

Enable with `--caps=interactions`.

These 5 tools are added when the `interactions` capability tier is enabled.

## Interactions

| Tool | Parameters | Description |
| --- | --- | --- |
| `wavexis_dialog_accept` | `session_id, prompt_text?` | Accept a JavaScript dialog (alert, confirm, prompt). |
| `wavexis_dialog_dismiss` | `session_id` | Dismiss a JavaScript dialog. |
| `wavexis_grant_permission` | `session_id, permission` | Grant a browser permission (geolocation, notifications, etc.). |
| `wavexis_intercept_download` | `session_id, pattern?, output_path?` | Intercept a download matching a URL pattern. |
| `wavexis_reset_permissions` | `session_id` | Reset all granted permissions. |
