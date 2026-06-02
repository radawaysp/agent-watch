# Development

Agent Watch uses a standard `src/` Python package layout and `pyproject.toml` for project metadata, dependencies, linting, typing, and tests.

## Setup

```powershell
python -m pip install -e ".[dev,llm]"
```

The `llm` extra installs the OpenAI client. Tests do not require a real API key because LLM-dependent behavior has a fallback path.

## Checks

```powershell
python -m ruff check .
python -m mypy src
python -m pytest
```

Source adapter tests should use local fixtures or HTTP mocks. Do not make CI depend on live external services.

## Release Notes

Before tagging a release, run the full checks on Windows and Ubuntu through GitHub Actions. Also run `agent-watch init` in a temporary directory and inspect the generated config for personal paths or secrets.

