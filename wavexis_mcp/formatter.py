"""Response formatting helpers for WaveXisMCP tools.

These utilities serialize tool outputs (JSON, base64, file metadata)
into the string format expected by the FastMCP SDK.
"""

from __future__ import annotations

import asyncio
import base64
import ipaddress
import json
import logging
import os
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

_logger = logging.getLogger(__name__)


def secure_output_path(path: str, base_dir: str | os.PathLike[str] | None = None) -> Path:
    """Resolve *path* and verify it lies inside the allowed output directory.

    The allowed base directory is taken from *base_dir* if supplied, then
    from the ``WAVEXIS_MCP_OUTPUT_DIR`` environment variable, and finally
    falls back to the current working directory.  Relative paths are resolved
    against the base directory.  If the resolved path escapes the base
    directory, a ``ValueError`` is raised.

    Args:
        path: Destination file or directory path supplied by a caller.
        base_dir: Optional explicit base directory to validate against.

    Returns:
        A resolved ``Path`` that is guaranteed to be inside the allowed base.

    Raises:
        ValueError: If the resolved path escapes the allowed base directory.
    """
    if base_dir is not None:
        base = Path(base_dir).resolve()
    else:
        base = Path(os.environ.get("WAVEXIS_MCP_OUTPUT_DIR", Path.cwd())).resolve()
    target = Path(path)
    resolved = target.resolve() if target.is_absolute() else (base / target).resolve()
    try:
        resolved.relative_to(base)
    except ValueError as exc:
        raise ValueError(
            f"Output path {path!r} is outside the allowed output directory {base}"
        ) from exc
    return resolved


# Hostnames/IPs that should never be reached via user-supplied URLs.
_BLOCKED_HOSTS = frozenset(
    {
        "localhost",
        "metadata",
        "metadata.google.internal",
        "metadata.google",
        "169.254.169.254",
    }
)


def validate_url(url: str, *, allow_internal: bool | None = None) -> None:
    """Validate that *url* is safe to navigate to.

    By default only ``http`` and ``https`` schemes are allowed, cloud metadata
    endpoints are blocked, and private/local IP literals are rejected.  Set the
    ``WAVEXIS_MCP_ALLOW_INTERNAL_URLS`` environment variable to ``1`` to allow
    internal/private targets, e.g. for testing local applications.

    Args:
        url: The URL to validate.
        allow_internal: Override the default internal-URL policy.  If ``None``,
            the environment variable is consulted.

    Raises:
        ValueError: If the URL is not safe to navigate to.
    """
    if allow_internal is None:
        allow_internal = os.environ.get("WAVEXIS_MCP_ALLOW_INTERNAL_URLS", "").lower() in {
            "1",
            "true",
            "yes",
        }

    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError(f"URL scheme {parsed.scheme!r} is not allowed: {url}")

    hostname = (parsed.hostname or "").lower()
    if not hostname:
        raise ValueError(f"URL has no host: {url}")

    if hostname in _BLOCKED_HOSTS:
        raise ValueError(f"URL host {hostname!r} is blocked: {url}")

    try:
        addr = ipaddress.ip_address(hostname)
    except ValueError:
        # Hostname is not an IP literal; further checks are not possible without
        # DNS resolution, which introduces TOCTOU concerns.  Non-IP hostnames are
        # accepted unless they match the explicit blocklist above.
        return

    if (
        addr.is_loopback or addr.is_link_local or addr.is_private or addr.is_reserved
    ) and not allow_internal:
        raise ValueError(
            f"URL resolves to a private/internal IP ({addr}) and is blocked: {url}. "
            "Set WAVEXIS_MCP_ALLOW_INTERNAL_URLS=1 to allow internal URLs."
        )


def encode_base64(data: bytes) -> str:
    """Encode raw bytes as a base64 ASCII string.

    Args:
        data: Raw binary data to encode.

    Returns:
        Base64-encoded string representation of *data*.
    """
    return base64.b64encode(data).decode("ascii")


async def save_to_file(data: bytes, path: str) -> dict[str, Any]:
    """Save bytes to a file and return a metadata dictionary.

    Parent directories are created automatically if they do not exist.
    The actual disk write is offloaded to a thread so the event loop
    is not blocked.

    Args:
        data: Raw binary data to write.
        path: Destination file path.

    Returns:
        A dict with ``"path"`` and ``"size_bytes"`` keys.
    """
    p = secure_output_path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    await asyncio.to_thread(p.write_bytes, data)
    return {"path": str(p), "size_bytes": len(data)}


def format_json_response(data: object) -> str:
    """Serialize arbitrary data as a JSON string.

    Args:
        data: JSON-serializable Python object.

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

    _logger.exception("Tool %s failed: %s", tool, error)
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
