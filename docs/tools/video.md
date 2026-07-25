# Video Tools (4)

Enable with `--caps=video`.

These 4 tools are added when the `video` capability tier is enabled.

## Video

| Tool | Parameters | Description |
| --- | --- | --- |
| `wavexis_video_action_overlay` | `session_id, show?` | Enable or disable action overlay on the video recording. |
| `wavexis_video_add_chapter` | `session_id, recording_id, title, timestamp_ms?` | Add a chapter marker to an active recording. |
| `wavexis_video_record` | `session_id, output_path?, width?, height?` | Start recording a video of the page. |
| `wavexis_video_stop` | `session_id, output_path?` | Stop recording and return the video as base64 or save to file. |
