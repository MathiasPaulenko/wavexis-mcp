"""Unit tests for formatter helpers."""

from __future__ import annotations

import base64
import json
from pathlib import Path

import pytest

from wavexis_mcp.formatter import (
    encode_base64,
    format_error,
    format_json_response,
    save_to_file,
    secure_output_path,
    validate_url,
)


def test_encode_base64() -> None:
    data = b"hello world"
    result = encode_base64(data)
    assert result == base64.b64encode(data).decode("ascii")


async def test_save_to_file(tmp_path: Path) -> None:
    data = b"\x89PNG test data"
    path = tmp_path / "test.png"
    result = await save_to_file(data, str(path))
    assert result["size_bytes"] == len(data)
    assert path.read_bytes() == data


async def test_save_to_file_creates_parent_dirs(tmp_path: Path) -> None:
    data = b"payload"
    path = tmp_path / "deep" / "dir" / "file.bin"
    result = await save_to_file(data, str(path))
    assert result["size_bytes"] == len(data)
    assert path.read_bytes() == data


def test_format_error() -> None:
    result = format_error("wavexis_test", ValueError("bad input"))
    data = json.loads(result)
    assert data["tool"] == "wavexis_test"
    assert "bad input" in data["error"]


def test_format_json_response() -> None:
    result = format_json_response({"status": "ok", "count": 3})
    data = json.loads(result)
    assert data["status"] == "ok"
    assert data["count"] == 3


def test_validate_url_allows_https_public() -> None:
    validate_url("https://example.com/path")  # should not raise


def test_validate_url_rejects_non_http_scheme() -> None:
    with pytest.raises(ValueError):
        validate_url("file:///etc/passwd")


def test_validate_url_rejects_metadata_ip() -> None:
    with pytest.raises(ValueError):
        validate_url("http://169.254.169.254/latest/meta-data/")


def test_validate_url_rejects_localhost() -> None:
    with pytest.raises(ValueError):
        validate_url("http://localhost:8080/")


@pytest.mark.parametrize(
    ("url",),
    [
        ("http://192.168.1.1/",),
        ("http://10.0.0.1/",),
        ("http://172.16.0.1/",),
        ("http://172.31.255.255/",),
        ("http://127.0.0.1/",),
        ("http://169.254.169.254/latest/meta-data/",),
        ("http://metadata/",),
        ("http://metadata.google.internal/",),
        ("http://metadata.google/",),
    ],
)
def test_validate_url_rejects_private_and_blocked_hosts(url: str) -> None:
    with pytest.raises(ValueError):
        validate_url(url)


@pytest.mark.parametrize(
    ("url",),
    [
        ("http://0x7f.0.0.1/",),
        ("http://0177.0.0.1/",),
        ("http://127.1/",),
        ("http://0x7f000001/",),
        ("http://2130706433/",),
    ],
)
def test_validate_url_rejects_alternate_ipv4_literals(url: str) -> None:
    """Hex, octal, shorthand, and packed-integer IPv4 forms are rejected."""
    with pytest.raises(ValueError):
        validate_url(url)


def test_validate_url_allows_alternate_public_ipv4_literal() -> None:
    """Alternate forms of public IPs are still allowed."""
    validate_url("http://0x01020304/")  # 1.2.3.4


def test_validate_url_rejects_ipv6_fallback_loopback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The socket.inet_pton IPv6 fallback normalizes and blocks loopback addresses."""

    def _reject_ip(value: str) -> None:
        raise ValueError("blocked")

    monkeypatch.setattr("wavexis_mcp.formatter.ipaddress.ip_address", _reject_ip)
    with pytest.raises(ValueError):
        validate_url("http://[::1]/")


def test_validate_url_allows_internal_when_requested() -> None:
    validate_url("http://127.0.0.1/", allow_internal=True)  # should not raise


def test_validate_url_allows_internal_via_environment(monkeypatch) -> None:
    monkeypatch.setenv("WAVEXIS_MCP_ALLOW_INTERNAL_URLS", "1")
    validate_url("http://192.168.1.1/")  # should not raise


def test_validate_url_rejects_malformed_url() -> None:
    with pytest.raises(ValueError):
        validate_url("not-a-url")


def test_secure_output_path_resolves_within_base(tmp_path: Path) -> None:
    result = secure_output_path("subdir/file.txt", base_dir=tmp_path)
    assert result == (tmp_path / "subdir" / "file.txt").resolve()


def test_secure_output_path_rejects_traversal(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        secure_output_path("../../../etc/passwd", base_dir=tmp_path)


def test_secure_output_path_rejects_absolute_escape(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        secure_output_path("/etc/passwd", base_dir=tmp_path)


def test_secure_output_path_uses_wavexis_output_dir_env(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("WAVEXIS_MCP_OUTPUT_DIR", str(tmp_path))
    result = secure_output_path("file.txt")
    assert result == (tmp_path / "file.txt").resolve()


def test_secure_output_path_rejects_whitespace_host_url() -> None:
    # Hostname containing only whitespace must be rejected.
    with pytest.raises(ValueError, match="URL has no host"):
        validate_url("http://   /path")


def test_secure_output_path_rejects_symlink_escape(tmp_path: Path) -> None:
    # Creating symlinks may require privileges on Windows; skip if unsupported.
    outside = tmp_path / "outside.txt"
    outside.write_text("secret")
    link = tmp_path / "link.txt"
    try:
        link.symlink_to(outside)
    except OSError:
        pytest.skip("Unable to create symlink in test environment")

    with pytest.raises(ValueError, match="Symlinks"):
        secure_output_path("link.txt", base_dir=tmp_path)


def test_secure_output_path_rejects_symlink_dir_escape(tmp_path: Path) -> None:
    outside_dir = tmp_path / "outside"
    outside_dir.mkdir()
    (outside_dir / "file.txt").write_text("secret")
    link_dir = tmp_path / "linkdir"
    try:
        link_dir.symlink_to(outside_dir)
    except OSError:
        pytest.skip("Unable to create symlink in test environment")

    with pytest.raises(ValueError, match="Symlinks"):
        secure_output_path("linkdir/file.txt", base_dir=tmp_path)
