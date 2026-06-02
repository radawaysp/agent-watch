from __future__ import annotations

from collections.abc import Iterable

from agent_watch.models import RankedItem, WatchItem

TRUSTED_SOURCE_BONUS = {
    "rss": 2.0,
    "arxiv": 2.0,
    "semantic_scholar": 1.8,
    "github": 1.2,
    "hackernews": -0.8,
}


def rank_items(items: Iterable[WatchItem], include_keywords: list[str]) -> list[RankedItem]:
    ranked = [_rank_item(item, include_keywords) for item in items]
    return sorted(
        ranked,
        key=lambda item: (item.score, item.published_at or item.fetched_at),
        reverse=True,
    )


def _rank_item(item: WatchItem, include_keywords: list[str]) -> RankedItem:
    haystack = f"{item.title} {item.summary}".lower()
    keyword_hits = [keyword for keyword in include_keywords if keyword.lower() in haystack]
    score = 1.0 + (len(keyword_hits) * 2.2) + TRUSTED_SOURCE_BONUS.get(item.source_type, 0.0)
    if item.published_at is not None:
        score += 0.5
    confidence = _confidence(item.source_type, score)
    tags = _tags(keyword_hits, item.source_type)
    return RankedItem.model_validate(
        {
            **item.model_dump(),
            "score": round(score, 2),
            "confidence": confidence,
            "tags": tags,
        }
    )


def _confidence(source_type: str, score: float) -> str:
    if source_type == "hackernews":
        return "low"
    if score >= 6:
        return "high"
    if score >= 3:
        return "medium"
    return "low"


def _tags(keyword_hits: list[str], source_type: str) -> list[str]:
    normalized = {keyword.lower().replace(" ", "-") for keyword in keyword_hits}
    normalized.add(source_type)
    return sorted(normalized)
