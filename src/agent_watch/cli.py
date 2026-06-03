from __future__ import annotations

import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated

import typer

from agent_watch.config import load_config
from agent_watch.ranking import rank_items
from agent_watch.rendering import MarkdownRenderer
from agent_watch.sources import fetch_items_with_report
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
    fetch_report = fetch_items_with_report(watch_config.sources)
    for error in fetch_report.errors:
        typer.echo(
            f"Warning: Source '{error.source_name}' ({error.source_type}) failed "
            f"after {error.attempts} attempt(s): {error.message}"
        )
    raw_items = fetch_report.items
    if fetch_report.errors and not raw_items:
        typer.echo("Error: All configured sources failed; no report was written.")
        raise typer.Exit(1)
    store: StateStore | None = None
    if dry_run:
        new_items = raw_items
    else:
        store = StateStore(watch_config.state.path)
        new_items = [item for item in raw_items if not store.has_seen(item)]
    skipped_items = len(raw_items) - len(new_items)
    ranked = rank_items(new_items, watch_config.keywords.include)
    summaries = Summarizer(watch_config.llm, language=watch_config.language).summarize(ranked)
    if not dry_run and not summaries:
        typer.echo(
            f"No new items to write to {watch_config.output_path(target_month)} "
            f"(fetched {len(raw_items)}, skipped {skipped_items})."
        )
        return
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
    typer.echo(
        f"Wrote {len(summaries)} items to {watch_config.output_path(target_month)} "
        f"(fetched {len(raw_items)}, skipped {skipped_items})."
    )


@app.command()
def doctor(
    config: Annotated[Path, typer.Option("--config", "-c")] = Path("agent-watch.yaml"),
) -> None:
    """Check local configuration without fetching sources or writing state."""

    if not config.is_file():
        typer.echo(f"Error: Config file not found: {config}")
        raise typer.Exit(1)

    try:
        watch_config = load_config(config)
    except Exception as exc:
        typer.echo(f"Error: Could not load config: {exc}")
        raise typer.Exit(1) from exc

    errors: list[str] = []
    warnings: list[str] = []
    sink = watch_config.sinks.default

    if sink.output_dir.exists() and not sink.output_dir.is_dir():
        errors.append(f"Output path is not a directory: {sink.output_dir}")
    errors.extend(_check_creatable_path(sink.output_dir, label="Output"))

    state_parent = watch_config.state.path.parent
    if state_parent.exists() and not state_parent.is_dir():
        errors.append(f"State parent path is not a directory: {state_parent}")
    errors.extend(_check_creatable_path(state_parent, label="State"))

    if sink.template is not None:
        template_path = Path(sink.template)
        if not template_path.is_absolute():
            template_path = config.parent / template_path
        if not template_path.is_file():
            errors.append(f"Template not found: {template_path}")

    if watch_config.llm.provider == "openai" and not os.environ.get("OPENAI_API_KEY"):
        warnings.append(
            "OPENAI_API_KEY is not set; OpenAI summaries will use the built-in fallback."
        )

    for source in watch_config.sources:
        if source.api_key_env and not os.environ.get(source.api_key_env):
            warnings.append(
                f"{source.api_key_env} is not set for source '{source.name}'."
            )

    for warning in warnings:
        typer.echo(f"Warning: {warning}")
    for error in errors:
        typer.echo(f"Error: {error}")
    if errors:
        raise typer.Exit(1)

    source_label = "source" if len(watch_config.sources) == 1 else "sources"
    typer.echo(
        f"Configuration OK: {len(watch_config.sources)} {source_label}, "
        f"{sink.type} sink, state path {watch_config.state.path}"
    )


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


def _check_creatable_path(path: Path, *, label: str) -> list[str]:
    probe = path if path.exists() else path.parent
    while not probe.exists() and probe != probe.parent:
        probe = probe.parent
    if not probe.exists():
        return [f"{label} parent path does not exist: {path.parent}"]
    if not probe.is_dir():
        return [f"{label} parent path is not a directory: {probe}"]
    if not os.access(probe, os.W_OK | os.X_OK):
        return [f"{label} parent path is not writable: {probe}"]
    return []


if __name__ == "__main__":
    app()
