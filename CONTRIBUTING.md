# Contributing to WaveXisMCP

Thank you for your interest in contributing! This document covers setup, testing, and the PR process.

## Development Setup

```bash
git clone https://github.com/MathiasPaulenko/wavexis-mcp.git
cd wavexis-mcp
pip install -e ".[dev]"
```

This installs WaveXisMCP with dev dependencies and the CDP backend (cdpwave).

## Running Tests

```bash
# Unit tests (no browser needed)
pytest tests/unit/ -v

# Integration tests (requires Chrome)
pytest tests/integration/ -v -m integration

# Linting
ruff check .

# Type checking
mypy src/wavexis_mcp/
```

## Project Structure

```
src/wavexis_mcp/
├── __init__.py
├── server.py          # FastMCP server, tool registration, main()
├── session.py          # SessionManager, BrowserSession
├── caps.py             # CapsManager, TIER_MAP
├── models.py           # Pydantic input models
├── formatter.py        # Response formatting helpers
├── errors.py           # Exception classes
├── convenience.py      # Composite tools (fill_form, check/uncheck)
└── tools/              # Tool implementations by category
    ├── session.py
    ├── navigation.py
    ├── capture.py
    ├── javascript.py
    ├── dom.py
    ├── input.py
    ├── cookies.py
    ├── tabs.py
    └── utility.py
```

## Adding a New Tool

1. Add the Pydantic input model to `models.py`
2. Implement the tool in the appropriate `tools/` module
3. Set tool annotations per the API design
4. Add unit tests with a mock backend
5. Update the tool count in README if needed

## Pull Request Process

1. Fork the repo and create a feature branch
2. Run `ruff check .` and `mypy src/wavexis_mcp/` — both must pass
3. Run `pytest tests/unit/ -v` — all tests must pass
4. Write a clear PR description referencing any related issues
5. Ensure your commits follow [conventional commits](https://www.conventionalcommits.org/)

## Code Style

- Python 3.11+ with type hints on all parameters and return types
- Line length: 100 characters (enforced by ruff)
- Ruff rules: E, F, I, N, UP, B, SIM, ASYNC
- No redundant comments
- English for all code, variable names, and technical docs
