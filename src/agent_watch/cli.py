from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated

import typer

from agent_watch.config import load_config
from agent_watch.ranking import rank_items
from agent_watch.rendering import MarkdownRenderer
from agent_watch.sources import fetch_items
from agent_watch.state import StateStore
from agent_watch.summarization import Summarizer
from agent_watch.templates import DEFAULT_CONFIG, MARKDOWN_TEMPLATE, OBSIDIAN_TEMPLATE

app = typer.Typer(help="Track AI agent technology updates and archive them as Markdown.")


@app.command()
def init(
    output_dir: Annotated[Path, typer.Option("--output-dir", "-o")] = Path("."),
) -> None:
    """Create a reusable starter config and Markdown templates."""

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "templates").mkdir(exist_ok=True)
    _write_if_missing(output_dir / "agent-watch.yaml", DEFAULT_CONFIG)
    _write_if_missing(output_dir / "templates" / "obsidian_month.md.j2", OBSIDIAN_TEMPLATE)
    _write_if_missing(output_dir / "templates" / "markdown_month.md.j2", MARKDOWN_TEMPLATE)
    typer.echo(f"Created starter files in {output_dir}")


@app.command()
def update(
    config: Annotated[Path, typer.Option("--config", "-c")] = Path("agent-watch.yaml"),
    dry_run: Annotated[bool, typer.Option("--dry-run")] = False,
    month: Annotated[str | None, typer.Option("--month")] = None,
) -> None:
    """Collect, rank, summarize, and write the configured monthly Markdown report."""

    watch_config = load_config(config)
    target_month = month or datetime.now(UTC).strftime("%Y-%m")
    raw_items = fetch_items(watch_config.sources)
    store: StateStore | None = None
    if dry_run:
        new_items = raw_items
    else:
        store = StateStore(watch_config.state.path)
        new_items = [item for item in raw_items if not store.has_seen(item)]
    ranked = rank_items(new_items, watch_config.keywords.include)
    summaries = Summarizer(watch_config.llm, language=watch_config.language).summarize(ranked)
    renderer = MarkdownRenderer(
        preset=watch_config.sinks.default.type,
        language=watch_config.language,
    )
    rendered = renderer.write_month(
        watch_config.output_path(target_month),
        month=target_month,
        summaries=summaries,
        dry_run=dry_run,
    )
    if dry_run:
        typer.echo(rendered)
        return
    if store is None:
        store = StateStore(watch_config.state.path)
    for summary in summaries:
        store.mark_seen(summary.item)
    typer.echo(f"Wrote {len(summaries)} items to {watch_config.output_path(target_month)}")


@app.command("synthesize-month")
def synthesize_month(
    month: Annotated[str, typer.Option("--month")],
    config: Annotated[Path, typer.Option("--config", "-c")] = Path("agent-watch.yaml"),
    dry_run: Annotated[bool, typer.Option("--dry-run")] = False,
) -> None:
    """Refresh the monthly report structure when no new fetch is needed."""

    watch_config = load_config(config)
    renderer = MarkdownRenderer(
        preset=watch_config.sinks.default.type,
        language=watch_config.language,
    )
    rendered = renderer.write_month(
        watch_config.output_path(month),
        month=month,
        summaries=[],
        dry_run=dry_run,
    )
    if dry_run:
        typer.echo(rendered)
        return
    typer.echo(f"Refreshed {watch_config.output_path(month)}")


def _write_if_missing(path: Path, content: str) -> None:
    if path.exists():
        return
    path.write_text(content, encoding="utf-8")


if __name__ == "__main__":
    app()
