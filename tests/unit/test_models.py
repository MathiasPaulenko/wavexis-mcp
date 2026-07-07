"""Unit tests for Pydantic models."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from wavexis_mcp.models import (
    ClickInput,
    FillFormInput,
    FormField,
    NavigateInput,
    ScreenshotInput,
    SessionOpenInput,
)


@pytest.mark.unit
def test_session_open_defaults() -> None:
    m = SessionOpenInput()
    assert m.backend == "cdp"
    assert m.headless is True
    assert m.width == 1280
    assert m.height == 800
    assert m.timeout == 30000


@pytest.mark.unit
def test_session_open_width_validation() -> None:
    with pytest.raises(ValidationError):
        SessionOpenInput(width=100)
    with pytest.raises(ValidationError):
        SessionOpenInput(width=5000)


@pytest.mark.unit
def test_navigate_required_url() -> None:
    with pytest.raises(ValidationError):
        NavigateInput()
    m = NavigateInput(url="https://example.com")
    assert m.url == "https://example.com"
    assert m.wait_strategy == "load"


@pytest.mark.unit
def test_screenshot_defaults() -> None:
    m = ScreenshotInput()
    assert m.full_page is True
    assert m.format == "png"
    assert m.quality == 80


@pytest.mark.unit
def test_click_defaults() -> None:
    m = ClickInput(selector="button")
    assert m.button == "left"
    assert m.click_count == 1


@pytest.mark.unit
def test_fill_form_requires_fields() -> None:
    with pytest.raises(ValidationError):
        FillFormInput()
    m = FillFormInput(fields=[FormField(selector="#a", value="1")])
    assert len(m.fields) == 1
