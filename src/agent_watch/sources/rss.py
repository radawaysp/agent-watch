from __future__ import annotations

from pathlib import Path
from urllib.parse import unquote, urlparse

import feedparser
import httpx

from agent_watch.config import SourceConfig
from agent_watch.models import WatchItem
from agent_watch.utils import canonicalize_url, clean_html, parse_datetime


def fetch_rss(source: SourceConfig, client: httpx.Client) -> list[WatchItem]:
    if source.url is None:
        raise ValueError(f"RSS source {source.name!r} requires url")
    if source.url.startswith("file://"):
        document = _read_file_url(source.url)
    else:
        response = client.get(source.url)
        response.raise_for_status()
        document = response.text
    return parse_rss_document(document, source_name=source.name, limit=source.limit)


def parse_rss_document(
    document: str,
    source_name: str,
    limit: int | None = None,
) -> list[WatchItem]:
    parsed = feedparser.parse(document)
    entries = parsed.entries[:limit] if limit is not None else parsed.entries
    items: list[WatchItem] = []
    for entry in entries:
        url = canonicalize_url(str(entry.get("link", "")))
        if not url:
            continue
        items.append(
            WatchItem(
                title=clean_html(str(entry.get("title", ""))) or url,
                url=url,
                source_name=source_name,
                source_type="rss",
                summary=clean_html(str(entry.get("summary", entry.get("description", "")))),
                published_at=parse_datetime(
                    str(entry.get("published", entry.get("updated", ""))) or None
                ),
            )
        )
    return items


def _read_file_url(url: str) -> str:
    parsed = urlparse(url)
    path = unquote(parsed.path)
    if path.startswith("/") and len(path) > 2 and path[2] == ":":
        path = path[1:]
    return Path(path).read_text(encoding="utf-8")
