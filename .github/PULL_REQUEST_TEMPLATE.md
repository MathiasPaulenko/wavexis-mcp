## Summary

Brief description of the changes.

## Type of change

- [ ] Bug fix
- [ ] New tool(s)
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation
- [ ] Refactor / cleanup

## Changes

- Added `wavexis_...` tool to `tools/...py`
- Updated `models.py` with `...Input` model
- Added tests in `tests/unit/test_...py`

## Verification

- [ ] `ruff check wavexis_mcp tests` passes
- [ ] `ruff format --check` passes
- [ ] `mypy wavexis_mcp` passes
- [ ] `python -m bandit -r wavexis_mcp` passes
- [ ] `pytest tests/unit -v` passes
- [ ] `python -m build` and `twine check dist/*` pass
- [ ] Integration tests pass (if applicable)

## Related issues

Closes #...
