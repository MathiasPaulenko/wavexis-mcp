"""Capability tier for WaveXisMCP.

This module defines the 13 capability tiers and provides a
``CapsManager`` to parse the ``--caps`` CLI flag and query which
tiers are enabled at runtime.  The *core* tier is always enabled
regardless of the user's selection.
"""

from __future__ import annotations

ALL_TIERS: frozenset[str] = frozenset({
    "core",
    "network",
    "storage",
    "emulation",
    "a11y",
    "interactions",
    "devtools",
    "vision",
    "video",
    "testing",
    "workflows",
    "data",
    "experimental",
})

TIER_MAP: dict[str, set[str]] = {
    "core": {"core"},
    "network": {"network"},
    "storage": {"storage"},
    "emulation": {"emulation"},
    "a11y": {"a11y"},
    "interactions": {"interactions"},
    "devtools": {"devtools"},
    "vision": {"vision"},
    "video": {"video"},
    "testing": {"testing"},
    "workflows": {"workflows"},
    "data": {"data"},
    "experimental": {"experimental"},
}


class CapsManager:
    """Manages which capability tiers are enabled.

    Core is always enabled regardless of the --caps value.
    """

    def __init__(self, caps: str = "core") -> None:
        """Initialize the manager with a comma-separated caps string.

        Args:
            caps: Comma-separated tier names (e.g. ``"core,network"``)
                or the special value ``"all"`` to enable every tier.
                Defaults to ``"core"``.
        """
        self._enabled: set[str] = self._parse(caps)

    @staticmethod
    def _parse(caps: str) -> set[str]:
        """Parse a caps string into a set of valid tier names.

        Invalid tier names are warned about on stderr and skipped.

        Args:
            caps: Raw caps string from the CLI.

        Returns:
            A set of validated tier names.  Always includes ``"core"``.
        """
        if caps.strip().lower() == "all":
            return set(ALL_TIERS)

        parts = [p.strip().lower() for p in caps.split(",") if p.strip()]
        valid: set[str] = set()
        for p in parts:
            if p in ALL_TIERS:
                valid.add(p)
            else:
                import sys

                print(
                    f"Warning: unknown capability tier '{p}'. "
                    f"Valid tiers: {', '.join(sorted(ALL_TIERS))}.",
                    file=sys.stderr,
                )
        valid.add("core")
        return valid

    def is_enabled(self, tier: str) -> bool:
        """Check whether a capability tier is enabled.

        Args:
            tier: Tier name to check.

        Returns:
            ``True`` if the tier is enabled.
        """
        return tier in self._enabled

    def enabled_tiers(self) -> set[str]:
        """Return a copy of the set of enabled tier names.

        Returns:
            Set of enabled tier names.
        """
        return set(self._enabled)
