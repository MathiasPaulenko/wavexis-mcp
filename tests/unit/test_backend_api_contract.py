"""Contract tests: every backend method called from wavexis_mcp must exist
on the real wavexis backend API.

Unit tests use ``AsyncMock`` backends, which accept any attribute — so a
call to a method that was renamed or removed upstream (e.g. the old
``set_cookies``) would silently pass.  This test statically extracts all
``backend.<name>(`` call sites and asserts each exists on
``AbstractBackend`` (or on a concrete backend for CDP/BiDi-specific
methods reached through ``getattr``).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

_PKG_DIR = Path(__file__).resolve().parent.parent.parent / "wavexis_mcp"
_CALL_RE = re.compile(r"backend\.([a-zA-Z_]\w*)\(")


def _called_backend_methods() -> set[str]:
    """Collect all ``backend.<name>(`` method call sites in the package."""
    names: set[str] = set()
    for path in _PKG_DIR.rglob("*.py"):
        names.update(_CALL_RE.findall(path.read_text(encoding="utf-8")))
    return {n for n in names if not n.startswith("_")}


def _backend_surface() -> set[str]:
    """Union of AbstractBackend plus concrete backend method names."""
    from wavexis.backend.base import AbstractBackend

    surface = set(dir(AbstractBackend))
    try:
        from wavexis.backend.cdp import CDPBackend

        surface |= set(dir(CDPBackend))
    except ImportError:
        pass
    try:
        from wavexis.backend.bidi import BiDiBackend

        surface |= set(dir(BiDiBackend))
    except ImportError:
        pass
    return surface


@pytest.mark.unit
def test_all_called_backend_methods_exist() -> None:
    """Every backend method invoked by wavexis_mcp must exist upstream."""
    called = _called_backend_methods()
    assert called, "no backend call sites found — regex or package layout broken"
    surface = _backend_surface()
    missing = sorted(called - surface)
    assert not missing, (
        "Backend methods called by wavexis_mcp but missing from wavexis "
        f"backends (API drift): {missing}"
    )
