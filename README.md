# Agent Watch

[![CI](https://github.com/radawaysp/agent-watch/actions/workflows/ci.yml/badge.svg)](https://github.com/radawaysp/agent-watch/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](pyproject.toml)

Agent Watch is an open-source Python CLI that helps maintainers track fast-moving AI agent ecosystem changes from RSS, arXiv, Semantic Scholar, GitHub, and community signals, then produce traceable Markdown reports.

It is built for open-source maintainer workflows: every summary keeps its source URL, publication date, collection date, relevance confidence, and category, so maintainers can follow framework releases, research papers, repository activity, and product changes without losing evidence. Obsidian is supported as a preset, but the default output is plain Markdown.

The project is designed for public reuse. Personal paths live in environment variables, generated state is ignored by git, tests run without network access, and the LLM path falls back to a source-index style summary when structured generation fails.

## Why Maintainers Use It

AI agent projects change quickly across papers, vendor announcements, framework repositories, and community discussions. Agent Watch reduces the manual tracking burden by turning those sources into a monthly, source-linked report that can be reviewed during issue triage, release planning, adapter maintenance, and project roadmap updates.

This repository is also structured for maintainable automation. See [Maintainer Workflows](docs/maintainer-workflows.md) for practical PR review, issue triage, release validation, and regression-testing workflows.

## Quick Start

```powershell
python -m pip install -e ".[dev,llm]"
agent-watch init
agent-watch update --config agent-watch.yaml --dry-run
```

Example dry-run output:

```markdown
# 2026-06 AI Agent Technology and Industry Report

## Monthly Read

The most notable item in this run is 'Building workflows for agents with skills'.

## Source Index

| Title | Source | Published | Fetched | Confidence | URL |
| --- | --- | --- | --- | --- | --- |
| Building workflows for agents with skills | Fixture | 2026-06-01 | 2026-06-02 | high | https://example.com/agent-workflows |
```

For a first real run, copy `.env.example`, set `OPENAI_API_KEY`, and set `OBSIDIAN_VAULT_PATH` only if you use the Obsidian preset. Then run:

```powershell
agent-watch update --config agent-watch.yaml
```

The default monthly output path is controlled by the sink configuration. A plain Markdown sink writes files like `notes/2026-06-agent-watch.md`; the Obsidian example writes into `${OBSIDIAN_VAULT_PATH}/技术学习/智能体/月度追踪`.

## Project Readiness

Agent Watch keeps generated notes, local SQLite state, and secrets out of git. The project includes CI, Dependabot, tests with local fixtures, source documentation, Obsidian setup notes, and a roadmap. For a quick tour of how the project is maintained, start here:

- [Demo](docs/demo.md)
- [Maintainer Workflows](docs/maintainer-workflows.md)
- [Roadmap](ROADMAP.md)
- [Changelog](CHANGELOG.md)

## CLI

```powershell
agent-watch init --output-dir .
agent-watch doctor --config agent-watch.yaml
agent-watch update --config agent-watch.yaml
agent-watch update --config agent-watch.yaml --dry-run
agent-watch synthesize-month --config agent-watch.yaml --month 2026-06
```

`init` creates a starter config and editable templates. `doctor` checks local configuration, paths, templates, and optional environment variables without fetching sources or writing state. `update` fetches configured sources, deduplicates against `data/state.sqlite`, ranks items, summarizes them, and writes the monthly Markdown file. `synthesize-month` refreshes the report structure when you want a month file without fetching new items.

## Configuration Shape

```yaml
language: zh
keywords:
  include: ["agent", "ai agent", "智能体"]
sinks:
  default:
    type: obsidian
    output_dir: "${OBSIDIAN_VAULT_PATH}/技术学习/智能体/月度追踪"
sources:
  - name: OpenAI News
    type: rss
    url: https://openai.com/news/rss.xml
llm:
  provider: openai
  model: gpt-5-mini
```

Supported source types are `rss`, `arxiv`, `semantic_scholar`, `github`, and `hackernews`. Community sources such as Hacker News are treated as low-confidence signals and should not be cited as facts without a primary source.

## Scheduling

Agent Watch does not own scheduling. Run it weekly with the scheduler you already use.

Windows Task Scheduler command:

```powershell
pwsh -NoLogo -NoProfile -Command "Set-Location 'C:\path\to\agent-watch'; agent-watch update --config agent-watch.yaml"
```

cron example:

```cron
0 8 * * 1 cd /path/to/agent-watch && agent-watch update --config agent-watch.yaml
```

GitHub Actions can also run the CLI on a schedule. See `examples/github-actions-workflow.yml`.

## Quality Baseline

Every summary keeps the title, original URL, source name, publication date, collection date, and confidence. The SQLite state database and generated notes are ignored by git so a public repository does not leak private paths or reading history.

Run local checks before publishing changes:

```powershell
agent-watch doctor --config agent-watch.yaml
python -m ruff check .
python -m mypy src
python -m pytest
```

## Maintainer

Agent Watch is maintained by `radawaysp`. The repository is intended to be public and verifiable on GitHub at `https://github.com/radawaysp/agent-watch`.
