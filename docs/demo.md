# Demo

This demo shows the public maintainer-facing flow without requiring API keys or live network access.

## Initialize

```powershell
agent-watch init --output-dir .
```

This creates `agent-watch.yaml` plus editable Markdown templates. The starter config uses environment variables for secrets and personal paths, so it can be committed as an example without leaking local state.

## Dry Run

```powershell
agent-watch update --config agent-watch.yaml --dry-run
```

Dry-run mode fetches and renders candidate items without writing notes or creating `data/state.sqlite`. That behavior is covered by tests because public users should be able to preview the report safely before committing to a local note path.

Example output shape:

```markdown
# 2026-06 AI Agent Technology and Industry Report

## Monthly Read

The most notable item in this run is 'Building workflows for agents with skills'. Agent workflows combine tools, memory, and evaluators.

## Trend Overview

| Category | Count |
| --- | --- |
| industry | 1 |

## Source Index

| Title | Source | Published | Fetched | Confidence | URL |
| --- | --- | --- | --- | --- | --- |
| Building workflows for agents with skills | Fixture | 2026-06-01 | 2026-06-02 | high | https://example.com/agent-workflows |
```

The report deliberately keeps the source index next to the narrative sections. Maintainers can read the short synthesis, then immediately inspect evidence and confidence without chasing a separate database.

## Obsidian Preset

The Obsidian preset writes normal Markdown with frontmatter, tags, and source tables:

```yaml
sinks:
  default:
    type: obsidian
    output_dir: "${OBSIDIAN_VAULT_PATH}/技术学习/智能体/月度追踪"
```

Generated monthly files are ignored by default when they live under `notes/`, but users can choose to publish reports intentionally if their project wants public ecosystem notes.

