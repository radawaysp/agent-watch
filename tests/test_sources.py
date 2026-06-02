from __future__ import annotations

from pathlib import Path

from agent_watch.sources.rss import parse_rss_document


def test_parse_rss_document_normalizes_items() -> None:
    xml = Path("tests/fixtures/rss_sample.xml").read_text(encoding="utf-8")

    items = parse_rss_document(xml, source_name="Example Feed")

    assert len(items) == 1
    assert items[0].title == "Building workflows for agents with skills"
    assert items[0].url == "https://example.com/agent-workflows"
    assert items[0].source_type == "rss"

