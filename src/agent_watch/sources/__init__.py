from __future__ import annotations

from collections.abc import Iterable

import httpx

from agent_watch.config import SourceConfig
from agent_watch.models import WatchItem
from agent_watch.sources.arxiv import fetch_arxiv
from agent_watch.sources.github import fetch_github
from agent_watch.sources.hackernews import fetch_hackernews
from agent_watch.sources.rss import fetch_rss
from agent_watch.sources.semantic_scholar import fetch_semantic_scholar


def fetch_items(sources: Iterable[SourceConfig]) -> list[WatchItem]:
    items: list[WatchItem] = []
    with httpx.Client(timeout=20.0, follow_redirects=True) as client:
        for source in sources:
            items.extend(fetch_source(source, client))
    return items


def fetch_source(source: SourceConfig, client: httpx.Client) -> list[WatchItem]:
    if source.type == "rss":
        return fetch_rss(source, client)
    if source.type == "arxiv":
        return fetch_arxiv(source, client)
    if source.type == "semantic_scholar":
        return fetch_semantic_scholar(source, client)
    if source.type == "github":
        return fetch_github(source, client)
    if source.type == "hackernews":
        return fetch_hackernews(source, client)
    raise ValueError(f"Unsupported source type: {source.type}")

