from __future__ import annotations

import httpx

from agent_watch.config import SourceConfig
from agent_watch.models import WatchItem
from agent_watch.utils import clean_html, parse_datetime

HN_SEARCH_URL = "https://hn.algolia.com/api/v1/search_by_date"


def fetch_hackernews(source: SourceConfig, client: httpx.Client) -> list[WatchItem]:
    query = source.query or "ai agent"
    response = client.get(HN_SEARCH_URL, params={"query": query, "hitsPerPage": source.limit})
    response.raise_for_status()
    data = response.json()
    items: list[WatchItem] = []
    for hit in data.get("hits", []):
        url = str(hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID')}")
        title = str(hit.get("title") or hit.get("story_title") or url)
        points = int(hit.get("points") or 0)
        comments = int(hit.get("num_comments") or 0)
        items.append(
            WatchItem(
                title=clean_html(title),
                url=url,
                source_name=source.name,
                source_type="hackernews",
                summary=f"Community signal. Points: {points}; comments: {comments}.",
                published_at=parse_datetime(str(hit.get("created_at") or "")),
                metadata={"points": points, "comments": comments},
            )
        )
    return items

