# Interactions Tools (5)

Enable with `--caps=interactions`.

Interaction tools handle browser-level events that aren't DOM clicks. Accept or dismiss JavaScript dialogs (alert, confirm, prompt), intercept file downloads, grant browser permissions (geolocation, notifications, camera, microphone), and reset permissions.

Essential for testing pages with popups, permission flows, or download functionality.

| Tool | Parameters | Description |
| --- | --- | --- |
| `wavexis_dialog_accept` | `session_id`, `prompt_text` | Accept a JavaScript dialog (alert, confirm, prompt). For `prompt` dialogs, `prompt_text` sets the entered value. |
| `wavexis_dialog_dismiss` | `session_id` | Dismiss a JavaScript dialog (equivalent to clicking "Cancel"). |
| `wavexis_intercept_download` | `session_id`, `output_dir` | Intercept the next file download. The downloaded file is saved to `output_dir` (default: `./downloads`). Returns the file path. |
| `wavexis_grant_permission` | `session_id`, `permission` | Grant a browser permission. Values: `geolocation`, `notifications`, `camera`, `microphone`, `clipboard-read`, `clipboard-write`. Auto-accepts future permission requests for this type. |
| `wavexis_reset_permissions` | `session_id` | Reset all granted permissions. The browser will prompt again for each permission. |

!!! example "Handle a confirm dialog"
    ```text
    wavexis_session_open(backend="cdp")
    wavexis_navigate(session_id="abc-123", url="https://example.com")
    wavexis_click(session_id="abc-123", selector="#delete")
    # A confirm dialog appears: "Are you sure?"
    wavexis_dialog_accept(session_id="abc-123")
    wavexis_session_close(session_id="abc-123")
    ```

!!! example "Intercept a download"
    ```text
    wavexis_session_open(backend="cdp")
    wavexis_navigate(session_id="abc-123", url="https://example.com")
    wavexis_intercept_download(session_id="abc-123", output_dir="./downloads")
    wavexis_click(session_id="abc-123", selector="#download-btn")
    → {"path": "./downloads/report.pdf", "size": 102400}
    wavexis_session_close(session_id="abc-123")
    ```
