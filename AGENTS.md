# WaveXisMCP — Agent Notes

## Verification commands

Run from the repository root (PowerShell):

```powershell
python -m pytest tests/unit -q
ruff check wavexis_mcp tests
ruff format --check
mypy wavexis_mcp
python -m bandit -r wavexis_mcp
python -m build
python -m twine check dist/*
$env:NO_MKDOCS_2_WARNING=1; python -m mkdocs build -q
```

On Unix shells use the same commands with `twine` and:

```bash
NO_MKDOCS_2_WARNING=1 python -m mkdocs build -q
```

## Test environment

- Python 3.11+ is required; the test suite runs with `pytest` and `pytest-asyncio`.
- `asyncio_mode = "auto"` is configured in `pyproject.toml`.

## Output directory sandbox

All file-writing tools use `secure_output_path()`, which resolves paths under the
directory configured by the `WAVEXIS_MCP_OUTPUT_DIR` environment variable, or the
current working directory if unset. Paths that escape this base directory are
rejected. Tests set `WAVEXIS_MCP_OUTPUT_DIR` to a per-test `tmp_path` fixture
via `conftest.py`.

## Dependency pinning

- `mcp` is pinned to `>=1.0,<2`.
- `wavexis` is pinned to `>=2.18.0,<3.0`.

## Useful project files

- `pyproject.toml` — build, dependencies, ruff, mypy, pytest config.
- `CONTRIBUTING.md` — project structure and PR workflow.
- `SECURITY.md` — supported version table and vulnerability reporting.
- `scripts/generate_tool_docs.py` — regenerates `docs/tools/*.md` from registered MCP tools.
