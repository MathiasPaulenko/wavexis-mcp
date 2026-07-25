"""Unit tests for Pydantic models."""

from __future__ import annotations

from typing import Any

import pytest
from pydantic import ValidationError

from wavexis_mcp.models import (
    AssertTextVisibleInput,
    ClickInput,
    CookiesSetInput,
    FillFormInput,
    FormField,
    NavigateInput,
    ScreenshotInput,
    SessionOpenInput,
    _limit_input_size,
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


@pytest.mark.unit
def test_limit_input_size_handles_deep_nesting() -> None:
    """Deeply nested payloads must not blow the Python recursion limit."""
    data: dict[str, Any] = {}
    current: dict[str, Any] = data
    for _ in range(1500):
        current["child"] = {}
        current = current["child"]
    result = _limit_input_size(data)
    assert result is data


@pytest.mark.unit
def test_assert_text_visible_rejects_empty_text() -> None:
    with pytest.raises(ValidationError):
        AssertTextVisibleInput(text="", session_id="sid")


@pytest.mark.unit
def test_cookie_set_rejects_empty_fields() -> None:
    with pytest.raises(ValidationError):
        CookiesSetInput(name="", value="v", domain="d.com", session_id="sid")
    with pytest.raises(ValidationError):
        CookiesSetInput(name="n", value="", domain="d.com", session_id="sid")
    with pytest.raises(ValidationError):
        CookiesSetInput(name="n", value="v", domain="", session_id="sid")
