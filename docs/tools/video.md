# Video Tools (4)

Enable with `--caps=video`.

Screencast recording (MJPEG frame stream), chapters, and action overlay. Enable with `--caps=video`.

## Summary

| Tool | Parameters | Description |
| --- | --- | --- |
| [`wavexis_video_action_overlay`](#wavexis_video_action_overlay) | `session_id, show?` | Enable or disable the on-page action overlay for recordings. |
| [`wavexis_video_add_chapter`](#wavexis_video_add_chapter) | `session_id, recording_id, title, timestamp_ms?` | Add a chapter marker to an active recording. |
| [`wavexis_video_record`](#wavexis_video_record) | `session_id, output_path?, width?, height?` | Start recording a video of the page. |
| [`wavexis_video_stop`](#wavexis_video_stop) | `session_id, recording_id?, output_path?` | Stop recording and return the captured frames as an MJPEG stream. |

## Video

### wavexis_video_action_overlay

Enable or disable the on-page action overlay for recordings.

When enabled, a small fixed badge is injected into the page that
flashes the last user action (click, keypress, input) so it is
visible in captured screencast frames.

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

Stop recording and return the captured frames as an MJPEG stream.

The output is a Motion JPEG stream (concatenated JPEG frames) — a
format playable by VLC/ffmpeg and encodable to mp4/webm.  It is not
a containerized mp4/webm.

Args:
    input: Stop parameters (recording_id, output_path).

Returns:
    JSON string with ``base64`` MJPEG data or file ``path``,
    plus ``duration_ms``, ``size_bytes``, ``frames``, ``format``
    and ``chapters``.

**Parameters:**

| Parameter | Type | Required | Default | Description |
| --- | --- | :---: | --- | --- |
| `session_id` | string | Yes | — | Active session ID from wavexis_session_open |
| `recording_id` | string | No | `null` | Recording ID from wavexis_video_record. If omitted, stops the most recent recording for the session. |
| `output_path` | string | No | `null` | Output file path (.mjpg) |
