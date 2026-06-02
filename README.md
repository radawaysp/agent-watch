# Agent Watch

Agent Watch is a small CLI for tracking AI agent technology and industry updates. It collects source items, removes duplicates, ranks relevance, summarizes the most useful items, and writes a monthly Markdown report. Obsidian is supported as a preset, but the default architecture works with any Markdown folder.

The project is designed for public reuse: personal paths live in environment variables, generated state is ignored by git, tests run without network access, and the LLM path falls back to a source-index style summary when structured generation fails.

## Quick Start

```powershell
python -m pip install -e ".[dev,llm]"
agent-watch init
agent-watch update --config agent-watch.yaml --dry-run
```

For a first real run, copy `.env.example`, set `OPENAI_API_KEY`, and set `OBSIDIAN_VAULT_PATH` only if you use the Obsidian preset. Then run:

```powershell
agent-watch update --config agent-watch.yaml
```

The default monthly output path is controlled by the sink configuration. A plain Markdown sink writes files like `notes/2026-06-agent-watch.md`; the Obsidian example writes into `${OBSIDIAN_VAULT_PATH}/技术学习/智能体/月度追踪`.

## CLI

```powershell
agent-watch init --output-dir .
agent-watch update --config agent-watch.yaml
agent-watch update --config agent-watch.yaml --dry-run
agent-watch synthesize-month --config agent-watch.yaml --month 2026-06
```

`init` creates a starter config and editable templates. `update` fetches configured sources, deduplicates against `data/state.sqlite`, ranks items, summarizes them, and writes the monthly Markdown file. `synthesize-month` refreshes the report structure when you want a month file without fetching new items.

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
python -m ruff check .
python -m mypy src
python -m pytest
```

