"""Pytest configuration for integration tests.

Integration tests marked with ``chrome`` need a real Chrome/Chromium
binary.  If none is available they are skipped instead of failing.
"""

from __future__ import annotations

import pytest


def _chrome_available() -> bool:
    """Check if a Chrome browser is available via wavexis BackendManager."""
    try:
        from wavexis.backend.manager import BackendManager

        return "cdp" in BackendManager().list_available()
    except Exception:
        return False


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Skip chrome-marked integration tests when no Chrome binary exists."""
    if _chrome_available():
        return
    skip_marker = pytest.mark.skip(reason="Chrome/cdpwave not available")
    for item in items:
        if "chrome" in item.keywords:
            item.add_marker(skip_marker)
