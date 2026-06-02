# Obsidian Setup

The Obsidian preset writes normal Markdown with frontmatter, tags, and traceable source tables. It does not require an Obsidian plugin.

Set the vault path in your environment:

```powershell
$env:OBSIDIAN_VAULT_PATH = "C:\path\to\your\vault"
```

Then configure the sink:

```yaml
sinks:
  default:
    type: obsidian
    output_dir: "${OBSIDIAN_VAULT_PATH}/技术学习/智能体/月度追踪"
    filename_template: "{month}-agent-watch.md"
```

The generated note includes a short monthly judgement, a trend overview table, weekly narrative updates, a source index, and a next-month watchlist. The table sections include explanatory text before and after the table so the visual element does not stand alone without interpretation.

For public repositories, keep the Obsidian vault path in `OBSIDIAN_VAULT_PATH`. Do not commit generated monthly notes unless your repository is intentionally publishing the report contents.

