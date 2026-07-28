"""Unit tests for CapsManager."""

from __future__ import annotations

import pytest

from wavexis_mcp.caps import ALL_TIERS, CapsManager


def test_core_always_enabled() -> None:
    caps = CapsManager("core")
    assert caps.is_enabled("core")
    assert caps.enabled_tiers() == ["core"]


def test_all_enables_all_tiers() -> None:
    caps = CapsManager("all")
    assert set(caps.enabled_tiers()) == set(ALL_TIERS)


def test_specific_tiers() -> None:
    caps = CapsManager("core,network,storage")
    assert caps.is_enabled("core")
    assert caps.is_enabled("network")
    assert caps.is_enabled("storage")
    assert not caps.is_enabled("devtools")


def test_invalid_tier_ignored() -> None:
    with pytest.warns(UserWarning, match="unknown capability tier 'invalid'"):
        caps = CapsManager("core,invalid,network")
    assert caps.is_enabled("core")
    assert caps.is_enabled("network")
    assert not caps.is_enabled("invalid")


def test_empty_string_defaults_to_core() -> None:
    caps = CapsManager("")
    assert caps.is_enabled("core")
    assert len(caps.enabled_tiers()) == 1


def test_none_string_defaults_to_core() -> None:
    """The value 'none' should silently default to core-only."""
    caps = CapsManager("none")
    assert caps.is_enabled("core")
    assert caps.enabled_tiers() == ["core"]


def test_duplicate_tier_warned() -> None:
    """Duplicate tiers should trigger a warning and be deduplicated."""
    with pytest.warns(UserWarning, match="duplicate capability tier 'network' ignored"):
        caps = CapsManager("core,network,network")
    assert caps.enabled_tiers() == ["core", "network"]


def test_enabled_tiers_preserves_order() -> None:
    """enabled_tiers() should preserve the user-specified order."""
    caps = CapsManager("network,storage,a11y")
    tiers = caps.enabled_tiers()
    assert tiers[0] == "core"  # core always first
    assert tiers[1:] == ["network", "storage", "a11y"]
