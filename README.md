# Sabermind

Baseball betting trading research and execution tooling. The repository currently
contains the Python CLI and developer tooling. Data providers, strategies, risk
controls, and paper execution are planned for Milestone 2 and beyond.

## Development setup

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) and Git, then:

```bash
git clone https://github.com/LinusJacobsson/sabermind.git
cd sabermind
uv python install
uv sync --locked
uv run pre-commit install
uv run sabermind
```

Python 3.13 is the development baseline, selected by `.python-version`. Commit
`pyproject.toml` and `uv.lock` together when dependencies change. Do not edit the
lockfile by hand. CI currently uses uv 0.9.7; validate changes to that version.

## Checks

```bash
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked mypy
uv run --locked pytest --cov --cov-report=term-missing
uv run --locked pip-audit --skip-editable
uv build
```

For automatic fixes, run `uv run ruff check --fix .` and `uv run ruff format .`.
Run `uv run pre-commit run --all-files` before opening a PR. The checks above
become available as the Milestone 1 setup PRs merge.

## VS Code

Open this folder, install the recommended extensions, and run **Python: Select
Interpreter** to select `.venv`. Ruff formats and sorts imports on save. Use the
Testing sidebar for pytest and the **Sabermind CLI** debug configuration for
breakpoints. Pylance provides navigation; mypy supplies the strict type checks.

## Project layout

- `src/sabermind/`: installed application package and CLI.
- `tests/unit/`: deterministic tests without external services.
- `tests/integration/`: future provider and database integration tests.
- `.github/workflows/`: automated quality, test, build, and audit checks.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the contribution and review workflow.
