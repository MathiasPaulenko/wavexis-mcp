# Contributing

Contributions are welcome! This page covers the development workflow.

## Development setup

```bash
git clone https://github.com/MathiasPaulenko/wavexis-mcp.git
cd wavexis-mcp
python -m venv .venv-dev
.\.venv-dev\Scripts\Activate.ps1  # Windows
# source .venv-dev/bin/activate   # Unix
pip install -e ".[dev]"
```

## Running tests

```bash
python -m pytest tests/unit -q
```

## Linting and formatting

```bash
ruff check wavexis_mcp tests
ruff format --check
mypy wavexis_mcp
```

## Regenerating tool docs

When you add or modify tools, regenerate the documentation:

```bash
python scripts/generate_tool_docs.py
```

## Project structure

```
wavexis-mcp/
  wavexis_mcp/
    __init__.py
    server.py          # FastMCP server + tool registration
    session.py         # SessionManager
    models.py          # Pydantic input models
    formatter.py       # Response formatting
    security.py        # SSRF protection, path sandboxing
    tools/
      session.py       # Session management tools
      navigation.py    # Navigation tools
      capture.py       # Screenshot/PDF tools
      dom.py           # DOM tools
      input.py         # Input interaction tools
      javascript.py    # JS evaluation tools
      cookies.py       # Cookie tools
      tabs.py          # Tab management tools
      network.py       # Network tools
      storage.py       # Storage tools
      emulation.py     # Emulation tools
      a11y.py          # Accessibility tools
      interactions.py  # Dialog/permission tools
      devtools.py      # DevTools tools
      vision.py        # Lighthouse/WebAuthn tools
      video.py         # Video recording tools
      testing.py       # Testing tools
      workflows.py     # Multi-action YAML tools
      data.py          # Data extraction tools
      experimental.py  # Raw protocol tools
      utility.py       # Utility tools
      playwright_parity.py  # Playwright-parity tools
  tests/
    unit/              # Unit tests
    integration/       # Integration tests
  docs/                # MkDocs documentation
  scripts/             # Helper scripts
```

## PR workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feat/my-feature`)
3. Make your changes
4. Run tests and linting
5. Commit with a clear message
6. Open a pull request

## Good first issues

Check issues labeled [`good first issue`](https://github.com/MathiasPaulenko/wavexis-mcp/labels/good%20first%20issue) for beginner-friendly tasks.

## Full contributing guide

See [CONTRIBUTING.md](https://github.com/MathiasPaulenko/wavexis-mcp/blob/main/CONTRIBUTING.md) for the complete guide.
