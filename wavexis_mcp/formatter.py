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
import socket
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
        ValueError: If the resolved path escapes the allowed base directory
            or if any path component is a symlink.
    """
    if base_dir is not None:
        base = Path(base_dir).resolve()
    else:
        base = Path(os.environ.get("WAVEXIS_MCP_OUTPUT_DIR", Path.cwd())).resolve()
    target = Path(path)
    candidate = target if target.is_absolute() else base / target

    # Reject any symlink in the path.  resolve() already follows symlinks and
    # would reject targets that escape the base, but checking explicitly makes
    # the intent clear and mitigates obvious symlink-based sandbox bypasses.
    for part in [candidate, *candidate.parents]:
        if part == base:
            break
        if part.is_symlink():
            raise ValueError(f"Symlinks are not allowed in output path: {path!r}")

    resolved = candidate.resolve()
    try:
        resolved.relative_to(base)
    except ValueError as exc:
        raise ValueError(
            f"Output path {path!r} is outside the allowed output directory {base}"
        ) from exc
    return resolved


def _validate_header_value(name: str, value: str) -> None:
    """Validate that a header value does not contain injection characters.

    Args:
        name: Header name (used in error messages).
        value: Header value to validate.

    Raises:
        ValueError: If *value* contains a carriage return, line feed, or null byte.
    """
    if "\r" in value or "\n" in value or "\x00" in value:
        raise ValueError(f"Header value for {name!r} contains forbidden characters (CRLF or null)")


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

    hostname = (parsed.hostname or "").lower().strip()
    if not hostname:
        raise ValueError(f"URL has no host: {url}")

    if hostname in _BLOCKED_HOSTS:
        raise ValueError(f"URL host {hostname!r} is blocked: {url}")

    try:
        addr = ipaddress.ip_address(hostname)
    except ValueError:
        # ``ipaddress`` only accepts the canonical dotted-decimal/hex IPv6 forms.
        # Browsers and lower-level libc parsers also accept hex, octal, and
        # shorthand IPv4 forms (e.g. ``0x7f.0.0.1``, ``0177.0.0.1``, ``127.1``)
        # which can be used to bypass the blocklist above.  Normalize through
        # ``socket`` so those alternate forms are caught and checked.
        try:
            packed = socket.inet_aton(hostname)
            normalized = socket.inet_ntoa(packed)
            addr = ipaddress.ip_address(normalized)
        except (OSError, ValueError):
            try:
                packed = socket.inet_pton(socket.AF_INET6, hostname)
                normalized = socket.inet_ntop(socket.AF_INET6, packed)
                addr = ipaddress.ip_address(normalized)
            except (OSError, ValueError):
                # Hostname is not an IP literal; further checks are not possible
                # without DNS resolution, which introduces TOCTOU concerns.
                # Non-IP hostnames are accepted unless they match the blocklist.
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


def _write_bytes_sync(path: str, data: bytes) -> tuple[str, int]:
    """Resolve, validate, and write bytes to disk (run in a thread).

    Args:
        path: Destination file path.
        data: Raw binary data to write.

    Returns:
        Tuple of ``(resolved_path, size_bytes)``.
    """
    p = secure_output_path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(data)
    return str(p), len(data)


async def save_to_file(data: bytes, path: str) -> dict[str, Any]:
    """Save bytes to a file and return a metadata dictionary.

    Parent directories are created automatically if they do not exist.
    The whole operation is offloaded to a thread so the event loop is
    not blocked.

    Args:
        data: Raw binary data to write.
        path: Destination file path.

    Returns:
        A dict with ``"path"`` and ``"size_bytes"`` keys.
    """
    resolved, size = await asyncio.to_thread(_write_bytes_sync, path, data)
    return {"path": resolved, "size_bytes": size}


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

    safe_message = str(error).replace("\r", "").replace("\n", " ")
    _logger.exception("Tool %s failed: %s", tool, safe_message)
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
