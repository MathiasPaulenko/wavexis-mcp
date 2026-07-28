"""Unit tests for convenience composite helpers."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from wavexis_mcp.convenience import fill_form_composite
from wavexis_mcp.models import FormField


@pytest.mark.unit
async def test_fill_form_composite_fills_all_fields(mock_backend: AsyncMock) -> None:
    """All fields are filled when backend.fill succeeds for every selector."""
    fields = [
        FormField(selector="#name", value="Alice"),
        FormField(selector="#email", value="a@b.com"),
    ]
    count = await fill_form_composite(mock_backend, fields)
    assert count == 2
    assert mock_backend.fill.await_count == 2


@pytest.mark.unit
async def test_fill_form_composite_skips_failed_fields(mock_backend: AsyncMock) -> None:
    """Failed fields are skipped but remaining fields are still attempted."""
    mock_backend.fill = AsyncMock(side_effect=[RuntimeError("element not found"), None, None])
    fields = [
        FormField(selector="#missing", value="x"),
        FormField(selector="#name", value="Alice"),
        FormField(selector="#email", value="a@b.com"),
    ]
    count = await fill_form_composite(mock_backend, fields)
    assert count == 2
    assert mock_backend.fill.await_count == 3


@pytest.mark.unit
async def test_fill_form_composite_empty_list(mock_backend: AsyncMock) -> None:
    """An empty field list returns zero without calling the backend."""
    count = await fill_form_composite(mock_backend, [])
    assert count == 0
    assert mock_backend.fill.await_count == 0


@pytest.mark.unit
async def test_fill_form_composite_all_fail(mock_backend: AsyncMock) -> None:
    """When every field fails, the count is zero and no exception is raised."""
    mock_backend.fill = AsyncMock(side_effect=RuntimeError("boom"))
    fields = [
        FormField(selector="#a", value="1"),
        FormField(selector="#b", value="2"),
    ]
    count = await fill_form_composite(mock_backend, fields)
    assert count == 0
    assert mock_backend.fill.await_count == 2
