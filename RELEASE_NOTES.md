# Release v1.6.6

> **Note**: For the latest changes, including unreleased work, see [CHANGELOG.md](CHANGELOG.md). This file is a frozen snapshot of the v1.6.6 release.

## Summary

- Reached **100% test coverage** across all `wavexis_mcp` modules.
- Full suite now passes: **425 tests** (395 unit + 30 integration).
- Added `wavexis_mcp/tools/playwright_parity.py` with text-based accessibility find tools.
- Added coverage-gap test files: `test_coverage_gaps.py`, `test_coverage_remaining.py`, and `test_network_extended.py`.
- Cleaned up repository artifacts (`__pycache__`, `.coverage`, `htmlcov/`, `dist/`, `site/`, caches, and `tmp_debug.py`).
- Fixed lint/format issues so `ruff check` and `ruff format --check` pass cleanly.
- Added missing `Any` imports in `tools/input.py` and `tools/workflows.py`.
