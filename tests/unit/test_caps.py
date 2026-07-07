"""Unit tests for CapsManager."""

from __future__ import annotations

from wavexis_mcp.caps import ALL_TIERS, CapsManager


def test_core_always_enabled() -> None:
    caps = CapsManager("core")
    assert caps.is_enabled("core")
    assert caps.enabled_tiers() == {"core"}


def test_all_enables_all_tiers() -> None:
    caps = CapsManager("all")
    assert caps.enabled_tiers() == set(ALL_TIERS)


def test_specific_tiers() -> None:
    caps = CapsManager("core,network,storage")
    assert caps.is_enabled("core")
    assert caps.is_enabled("network")
    assert caps.is_enabled("storage")
    assert not caps.is_enabled("devtools")


def test_invalid_tier_ignored() -> None:
    caps = CapsManager("core,invalid,network")
    assert caps.is_enabled("core")
    assert caps.is_enabled("network")
    assert not caps.is_enabled("invalid")


def test_empty_string_defaults_to_core() -> None:
    caps = CapsManager("")
    assert caps.is_enabled("core")
    assert len(caps.enabled_tiers()) == 1
