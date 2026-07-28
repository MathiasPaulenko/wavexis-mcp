"""Capability tier for WaveXisMCP.

This module defines the 13 capability tiers and provides a
``CapsManager`` to parse the ``--caps`` CLI flag and query which
tiers are enabled at runtime.  The *core* tier is always enabled
regardless of the user's selection.
"""

from __future__ import annotations

import warnings

ALL_TIERS: frozenset[str] = frozenset(
    {
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
    }
)


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
        self._enabled: list[str] = self._parse(caps)

    @staticmethod
    def _parse(caps: str) -> list[str]:
        """Parse a caps string into an ordered list of valid tier names.

        Invalid tier names are warned about and skipped.  Duplicate tiers
        are warned about and deduplicated (preserving first occurrence order).

        Args:
            caps: Raw caps string from the CLI.

        Returns:
            An ordered list of validated tier names.  Always includes ``"core"``
            as the first element.
        """
        if caps.strip().lower() == "all":
            return sorted(ALL_TIERS)

        parts = [p.strip().lower() for p in caps.split(",") if p.strip()]
        valid: list[str] = []
        seen: set[str] = set()
        for p in parts:
            if p == "none" or p == "":
                continue
            if p in ALL_TIERS:
                if p in seen:
                    warnings.warn(
                        f"duplicate capability tier '{p}' ignored.",
                        stacklevel=2,
                    )
                    continue
                seen.add(p)
                valid.append(p)
            else:
                warnings.warn(
                    f"unknown capability tier '{p}'. Valid tiers: {', '.join(sorted(ALL_TIERS))}.",
                    stacklevel=2,
                )
        if "core" not in seen:
            valid.insert(0, "core")
        return valid

    def is_enabled(self, tier: str) -> bool:
        """Check whether a capability tier is enabled.

        Args:
            tier: Tier name to check.

        Returns:
            ``True`` if the tier is enabled.
        """
        return tier in self._enabled

    def enabled_tiers(self) -> list[str]:
        """Return a copy of the ordered list of enabled tier names.

        Returns:
            List of enabled tier names in the order they were specified.
        """
        return list(self._enabled)
