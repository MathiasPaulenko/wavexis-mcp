## Summary

<!-- One or two sentences describing what this PR does and why. -->

## Type of change

<!-- Check all that apply -->
- [ ] Bug fix
- [ ] New tool(s)
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation
- [ ] Refactor / cleanup
- [ ] Dependencies

## Changes

<!-- List the specific changes made. For code changes, mention the files/modules affected. -->
-

## Verification

<!-- For code changes, run ALL checks and tick the boxes. For docs-only changes, tick the docs-only section. -->

### Code changes
- [ ] `ruff check wavexis_mcp tests` passes
- [ ] `ruff format --check` passes
- [ ] `mypy wavexis_mcp` passes
- [ ] `python -m bandit -r wavexis_mcp` passes
- [ ] `pytest tests/unit -v` passes
- [ ] `python -m build` and `twine check dist/*` pass
- [ ] Integration tests pass (if applicable)

### Docs-only changes
- [ ] `NO_MKDOCS_2_WARNING=1 python -m mkdocs build -q` passes
- [ ] No broken links in nav or cross-references
- [ ] Code blocks use correct language tags (`text` for tool-call examples, `json`/`bash`/`python` as appropriate)

## Related issues

Closes #...
