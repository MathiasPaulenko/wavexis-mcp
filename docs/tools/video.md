# Video Tools (4)

Enable with `--caps=video`.

Video tools record the browser screen. Start recording, perform actions, stop to get the video file. Add chapter markers at specific timestamps and overlay action labels to annotate what's happening.

Useful for bug reports, demos, regression testing, and documenting automated workflows.

| Tool | Parameters | Description |
| --- | --- | --- |
| `wavexis_video_record` | `session_id`, `output_path`, `format`, `width`, `height`, `fps` | Start video recording. `format`: `webm` (default). `width`/`height`: resolution (default: viewport size). `fps`: frames per second (default 30). |
| `wavexis_video_stop` | `session_id` | Stop recording and save the video file. Returns the file path and duration. |
| `wavexis_video_add_chapter` | `session_id`, `title`, `timestamp` | Add a chapter marker at a specific timestamp (in seconds). Chapters appear in the video player's timeline. |
| `wavexis_video_action_overlay` | `session_id`, `label`, `x`, `y`, `duration` | Add an action overlay on the video. Displays `label` text at `(x, y)` for `duration` seconds. Useful for annotating clicks and inputs. |

!!! example "Record a login flow"
    ```text
    wavexis_session_open(backend="cdp", headless=false)
    wavexis_video_record(session_id="abc-123", output_path="./login-demo.webm")

    wavexis_navigate(session_id="abc-123", url="https://app.example.com/login")
    wavexis_video_add_chapter(session_id="abc-123", title="Login page loaded", timestamp=0)

    wavexis_fill(session_id="abc-123", selector="#email", value="user@example.com")
    wavexis_video_action_overlay(session_id="abc-123", label="Fill email", x=300, y=200, duration=2)

    wavexis_fill(session_id="abc-123", selector="#password", value="secret")
    wavexis_click(session_id="abc-123", selector="#submit")
    wavexis_video_add_chapter(session_id="abc-123", title="Submitted", timestamp=5)

    wavexis_video_stop(session_id="abc-123")
    → {"path": "./login-demo.webm", "duration": 8.5}
    wavexis_session_close(session_id="abc-123")
    ```
