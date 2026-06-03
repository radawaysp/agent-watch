from __future__ import annotations

from pathlib import Path

import httpx

from agent_watch.config import SourceConfig
from agent_watch.models import WatchItem
from agent_watch.sources import fetch_items_with_report
from agent_watch.sources.rss import parse_rss_document


def test_parse_rss_document_normalizes_items() -> None:
    xml = Path("tests/fixtures/rss_sample.xml").read_text(encoding="utf-8")

    items = parse_rss_document(xml, source_name="Example Feed")

    assert len(items) == 1
    assert items[0].title == "Building workflows for agents with skills"
    assert items[0].url == "https://example.com/agent-workflows"
    assert items[0].source_type == "rss"


def test_fetch_items_continues_after_source_error(
    monkeypatch,
) -> None:
    sources = [
        SourceConfig(name="Slow arXiv", type="arxiv", query="agent", limit=1),
        SourceConfig(name="Working RSS", type="rss", url="https://example.com/rss.xml", limit=1),
    ]
    item = WatchItem(
        title="Working item",
        url="https://example.com/item",
        source_name="Working RSS",
        source_type="rss",
        summary="A working item.",
    )

    def fake_fetch_source(source: SourceConfig, client: httpx.Client) -> list[WatchItem]:
        if source.name == "Slow arXiv":
            request = httpx.Request("GET", "https://export.arxiv.org/api/query")
            raise httpx.ReadTimeout("read timed out", request=request)
        return [item]

    monkeypatch.setattr("agent_watch.sources.fetch_source", fake_fetch_source)

    report = fetch_items_with_report(sources, sleeper=lambda _: None)

    assert report.items == [item]
    assert len(report.errors) == 1
    assert report.errors[0].source_name == "Slow arXiv"
    assert "read timed out" in report.errors[0].message


def test_fetch_items_retries_transient_source_error(
    monkeypatch,
) -> None:
    source = SourceConfig(
        name="Retry RSS",
        type="rss",
        url="https://example.com/rss.xml",
        limit=1,
        retries=1,
        retry_backoff_seconds=0,
    )
    item = WatchItem(
        title="Retried item",
        url="https://example.com/retried",
        source_name="Retry RSS",
        source_type="rss",
        summary="A retried item.",
    )
    attempts = 0

    def fake_fetch_source(source: SourceConfig, client: httpx.Client) -> list[WatchItem]:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            request = httpx.Request("GET", "https://example.com/rss.xml")
            raise httpx.ReadTimeout("temporary timeout", request=request)
        return [item]

    monkeypatch.setattr("agent_watch.sources.fetch_source", fake_fetch_source)

    report = fetch_items_with_report([source], sleeper=lambda _: None)

    assert attempts == 2
    assert report.items == [item]
    assert report.errors == []
