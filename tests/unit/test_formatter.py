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
