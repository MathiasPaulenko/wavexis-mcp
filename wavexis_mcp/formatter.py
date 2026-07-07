"""Response formatting helpers for WaveXisMCP tools.

These utilities serialize tool outputs (JSON, base64, file metadata)
into the string format expected by the FastMCP SDK.
"""

from __future__ import annotations

import base64
import json
from pathlib import Path
from typing import Any


def encode_base64(data: bytes) -> str:
    """Encode raw bytes as a base64 ASCII string.

    Args:
        data: Raw binary data to encode.

    Returns:
        Base64-encoded string representation of *data*.
    """
    return base64.b64encode(data).decode("ascii")


def save_to_file(data: bytes, path: str) -> dict[str, Any]:
    """Save bytes to a file and return a metadata dictionary.

    Parent directories are created automatically if they do not exist.

    Args:
        data: Raw binary data to write.
        path: Destination file path.

    Returns:
        A dict with ``"path"`` and ``"size_bytes"`` keys.
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(data)
    return {"path": str(p), "size_bytes": len(data)}


def format_json_response(data: Any) -> str:
    """Serialize arbitrary data as a JSON string.

    Args:
        data: Any JSON-serializable Python object.

    Returns:
        A JSON string with ``ensure_ascii=False``.
    """
    return json.dumps(data, default=str, ensure_ascii=False)


def format_error(tool: str, error: Exception) -> str:
    """Format an exception as a JSON error string with actionable suggestions.

    Args:
        tool: Name of the tool that raised the error.
        error: The exception instance.

    Returns:
        A JSON string with ``error``, ``tool``, ``type``, ``message``,
        and ``suggestion`` keys.
    """
    from wavexis_mcp.errors import get_suggestion

    return json.dumps(
        {
            "error": str(error),
            "tool": tool,
            "type": type(error).__name__,
            "message": str(error),
            "suggestion": get_suggestion(error),
        },
        ensure_ascii=False,
    )
