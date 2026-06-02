# Contributing

Thank you for helping improve Agent Watch. The project aims to stay small, testable, and useful for people who want durable Markdown research notes rather than another noisy news feed.

Before opening a pull request, run:

```powershell
python -m ruff check .
python -m mypy src
python -m pytest
```

When adding a source adapter, keep network parsing separate from normalization so tests can run with fixtures. When changing Markdown output, add or update rendering tests because downstream users may rely on a stable monthly structure.

Do not commit API keys, generated notes, local SQLite state, or personal Obsidian vault paths. Use environment variables and example configs instead.

