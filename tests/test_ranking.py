from __future__ import annotations

from agent_watch.models import WatchItem
from agent_watch.ranking import rank_items


def test_rank_items_scores_keywords_and_community_penalty() -> None:
    technical = WatchItem(
        title="New agent benchmark for tool use",
        url="https://example.com/benchmark",
        source_name="Research",
        source_type="rss",
        summary="Evaluation for AI agent planning and tool execution.",
    )
    community = WatchItem(
        title="HN discussion about AI agents",
        url="https://news.ycombinator.com/item?id=1",
        source_name="Hacker News",
        source_type="hackernews",
        summary="A discussion thread.",
    )

    ranked = rank_items([community, technical], include_keywords=["agent", "benchmark"])

    assert ranked[0].url == technical.url
    assert ranked[0].score > ranked[1].score
    assert ranked[1].confidence == "low"

