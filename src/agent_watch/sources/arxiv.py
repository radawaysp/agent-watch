from __future__ import annotations

from urllib.parse import urlencode

import httpx

from agent_watch.config import SourceConfig
from agent_watch.models import WatchItem
from agent_watch.sources.rss import parse_rss_document

ARXIV_API_URL = "https://export.arxiv.org/api/query"


def fetch_arxiv(source: SourceConfig, client: httpx.Client) -> list[WatchItem]:
    query = source.query or "cat:cs.AI OR cat:cs.CL"
    params = urlencode(
        {
            "search_query": query,
            "start": 0,
            "max_results": source.limit,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        }
    )
    response = client.get(f"{ARXIV_API_URL}?{params}")
    response.raise_for_status()
    items = parse_rss_document(response.text, source_name=source.name, limit=source.limit)
    return [
        WatchItem.model_validate({**item.model_dump(), "source_type": "arxiv"})
        for item in items
    ]

