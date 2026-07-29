# Video Tools (4)

Enable with `--caps=video`.

Video recording and playback capture. Enable with `--caps=video`.

## Summary

| Tool | Parameters | Description |
| --- | --- | --- |
| [`wavexis_video_action_overlay`](#wavexis_video_action_overlay) | `session_id, show?` | Enable or disable action overlay on the video recording. |
| [`wavexis_video_add_chapter`](#wavexis_video_add_chapter) | `session_id, recording_id, title, timestamp_ms?` | Add a chapter marker to an active recording. |
| [`wavexis_video_record`](#wavexis_video_record) | `session_id, output_path?, width?, height?` | Start recording a video of the page. |
| [`wavexis_video_stop`](#wavexis_video_stop) | `session_id, output_path?` | Stop recording and return the video as base64 or save to file. |

## Video

### wavexis_video_action_overlay

Enable or disable action overlay on the video recording.

Args:
    input: Overlay parameters (show).

Returns:
    JSON string with status ``"ok"`` and ``show``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `show` | boolean | No | `true` | Whether to show the overlay |

### wavexis_video_add_chapter

Add a chapter marker to an active recording.

Args:
    input: Chapter parameters (recording_id, title, timestamp_ms).

Returns:
    JSON string with ``status`` and ``chapter`` info.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `recording_id` | string | Yes | — | Recording ID from video_record |
| `title` | string | Yes | — | Chapter title |
| `timestamp_ms` | integer | No | `null` | Timestamp in ms |

### wavexis_video_record

Start recording a video of the page.

Args:
    input: Recording parameters (output_path, width, height).

Returns:
    JSON string with ``recording_id`` and ``status``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `output_path` | string | No | `null` | Output file path |
| `width` | integer | No | `1280` | Viewport width in pixels |
| `height` | integer | No | `800` | Viewport height in pixels |

### wavexis_video_stop

Stop recording and return the video as base64 or save to file.

Args:
    input: Stop parameters (output_path).

Returns:
    JSON string with ``base64`` video data or file ``path``,
    plus ``duration_ms`` and ``size_bytes``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `output_path` | string | No | `null` | Output file path |
