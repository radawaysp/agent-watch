from __future__ import annotations

import os

import httpx

from agent_watch.config import SourceConfig
from agent_watch.models import WatchItem
from agent_watch.utils import clean_html, parse_datetime

GITHUB_SEARCH_URL = "https://api.github.com/search/repositories"


def fetch_github(source: SourceConfig, client: httpx.Client) -> list[WatchItem]:
    query = source.query or "ai-agent OR llm-agent"
    headers = {"Accept": "application/vnd.github+json"}
    token = os.getenv(source.api_key_env or "GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    response = client.get(
        GITHUB_SEARCH_URL,
        params={"q": query, "sort": "updated", "order": "desc", "per_page": source.limit},
        headers=headers,
    )
    response.raise_for_status()
    data = response.json()
    items: list[WatchItem] = []
    for repo in data.get("items", []):
        url = str(repo.get("html_url", ""))
        if not url:
            continue
        stars = int(repo.get("stargazers_count", 0))
        description = clean_html(str(repo.get("description") or ""))
        items.append(
            WatchItem(
                title=str(repo.get("full_name", url)),
                url=url,
                source_name=source.name,
                source_type="github",
                summary=f"{description} Stars: {stars}",
                published_at=parse_datetime(str(repo.get("updated_at") or "")),
                metadata={"stars": stars},
            )
        )
    return items

