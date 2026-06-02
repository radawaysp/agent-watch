from __future__ import annotations

import os

import httpx

from agent_watch.config import SourceConfig
from agent_watch.models import WatchItem
from agent_watch.utils import clean_html, parse_datetime

SEMANTIC_SCHOLAR_SEARCH_URL = "https://api.semanticscholar.org/graph/v1/paper/search"


def fetch_semantic_scholar(source: SourceConfig, client: httpx.Client) -> list[WatchItem]:
    query = source.query or "AI agents tool use planning"
    headers: dict[str, str] = {}
    token = os.getenv(source.api_key_env or "SEMANTIC_SCHOLAR_API_KEY")
    if token:
        headers["x-api-key"] = token
    response = client.get(
        SEMANTIC_SCHOLAR_SEARCH_URL,
        params={
            "query": query,
            "limit": source.limit,
            "fields": "title,url,abstract,year,publicationDate,citationCount",
        },
        headers=headers,
    )
    response.raise_for_status()
    data = response.json()
    items: list[WatchItem] = []
    for paper in data.get("data", []):
        url = str(paper.get("url") or "")
        if not url:
            continue
        citations = int(paper.get("citationCount") or 0)
        items.append(
            WatchItem(
                title=clean_html(str(paper.get("title") or url)),
                url=url,
                source_name=source.name,
                source_type="semantic_scholar",
                summary=clean_html(str(paper.get("abstract") or "")),
                published_at=parse_datetime(str(paper.get("publicationDate") or "")),
                metadata={"citations": citations},
            )
        )
    return items

