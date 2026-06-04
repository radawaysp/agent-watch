from __future__ import annotations

from pathlib import Path

import httpx

from agent_watch.config import SourceConfig
from agent_watch.models import WatchItem
from agent_watch.sources import fetch_items_with_report
from agent_watch.sources.arxiv import ARXIV_API_URL, fetch_arxiv
from agent_watch.sources.rss import parse_rss_document
from agent_watch.sources.semantic_scholar import (
    SEMANTIC_SCHOLAR_SEARCH_URL,
    fetch_semantic_scholar,
)


def test_parse_rss_document_normalizes_items() -> None:
    xml = Path("tests/fixtures/rss_sample.xml").read_text(encoding="utf-8")

    items = parse_rss_document(xml, source_name="Example Feed")

    assert len(items) == 1
    assert items[0].title == "Building workflows for agents with skills"
    assert items[0].url == "https://example.com/agent-workflows"
    assert items[0].source_type == "rss"


def test_fetch_arxiv_parses_fixture_and_applies_limit() -> None:
    xml = Path("tests/fixtures/arxiv_sample.xml").read_text(encoding="utf-8")
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, text=xml, request=request)

    source = SourceConfig(
        name="arXiv Fixture",
        type="arxiv",
        query="cat:cs.AI AND agent",
        limit=1,
    )

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        items = fetch_arxiv(source, client)

    assert len(items) == 1
    assert items[0].title == "Evaluating Tool Use in AI Agents"
    assert items[0].url == "https://arxiv.org/abs/2606.00001"
    assert items[0].source_type == "arxiv"
    assert items[0].published_at is not None
    assert str(requests[0].url).startswith(ARXIV_API_URL)
    assert requests[0].url.params["max_results"] == "1"
    assert requests[0].url.params["sortBy"] == "submittedDate"


def test_fetch_semantic_scholar_parses_fixture_and_api_key(
    monkeypatch,
) -> None:
    payload = Path("tests/fixtures/semantic_scholar_sample.json").read_text(
        encoding="utf-8"
    )
    requests: list[httpx.Request] = []
    monkeypatch.setenv("SEMANTIC_SCHOLAR_API_KEY", "test-token")

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, text=payload, request=request)

    source = SourceConfig(
        name="Semantic Scholar Fixture",
        type="semantic_scholar",
        query="agent evaluation",
        limit=2,
    )

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        items = fetch_semantic_scholar(source, client)

    assert len(items) == 1
    assert items[0].title == "Traceable Evaluation for AI Agents"
    assert items[0].url == "https://www.semanticscholar.org/paper/paper-1"
    assert items[0].summary == "A study of traceable evaluation for AI agents."
    assert items[0].metadata == {"citations": 42}
    assert items[0].published_at is not None
    assert str(requests[0].url).startswith(SEMANTIC_SCHOLAR_SEARCH_URL)
    assert requests[0].url.params["limit"] == "2"
    assert requests[0].headers["x-api-key"] == "test-token"


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


def test_fetch_items_reports_rate_limit_after_retries(
    monkeypatch,
) -> None:
    source = SourceConfig(
        name="Limited Semantic Scholar",
        type="semantic_scholar",
        query="agent evaluation",
        limit=1,
        retries=1,
        retry_backoff_seconds=0,
    )
    attempts = 0

    def fake_fetch_source(source: SourceConfig, client: httpx.Client) -> list[WatchItem]:
        nonlocal attempts
        attempts += 1
        request = httpx.Request("GET", SEMANTIC_SCHOLAR_SEARCH_URL)
        response = httpx.Response(429, request=request, text="rate limited")
        raise httpx.HTTPStatusError("rate limited", request=request, response=response)

    monkeypatch.setattr("agent_watch.sources.fetch_source", fake_fetch_source)

    report = fetch_items_with_report([source], sleeper=lambda _: None)

    assert attempts == 2
    assert report.items == []
    assert len(report.errors) == 1
    assert report.errors[0].source_name == "Limited Semantic Scholar"
    assert report.errors[0].attempts == 2
    assert "HTTP 429" in report.errors[0].message


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
