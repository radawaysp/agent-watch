from __future__ import annotations

import time
from collections.abc import Callable, Iterable
from dataclasses import dataclass

import httpx

from agent_watch.config import SourceConfig
from agent_watch.models import WatchItem
from agent_watch.sources.arxiv import fetch_arxiv
from agent_watch.sources.github import fetch_github
from agent_watch.sources.hackernews import fetch_hackernews
from agent_watch.sources.rss import fetch_rss
from agent_watch.sources.semantic_scholar import fetch_semantic_scholar


@dataclass(frozen=True)
class FetchError:
    source_name: str
    source_type: str
    attempts: int
    message: str


@dataclass(frozen=True)
class FetchReport:
    items: list[WatchItem]
    errors: list[FetchError]


Sleeper = Callable[[float], None]


def fetch_items(sources: Iterable[SourceConfig]) -> list[WatchItem]:
    return fetch_items_with_report(sources).items


def fetch_items_with_report(
    sources: Iterable[SourceConfig],
    *,
    sleeper: Sleeper = time.sleep,
) -> FetchReport:
    items: list[WatchItem] = []
    errors: list[FetchError] = []
    for source in sources:
        attempts = source.retries + 1
        for attempt in range(attempts):
            try:
                with httpx.Client(
                    timeout=source.timeout_seconds,
                    follow_redirects=True,
                ) as client:
                    items.extend(fetch_source(source, client))
                break
            except httpx.HTTPError as exc:
                if attempt < attempts - 1:
                    delay = source.retry_backoff_seconds * (2**attempt)
                    if delay > 0:
                        sleeper(delay)
                    continue
                if not source.continue_on_error:
                    raise
                errors.append(
                    FetchError(
                        source_name=source.name,
                        source_type=source.type,
                        attempts=attempts,
                        message=_format_http_error(exc),
                    )
                )
    return FetchReport(items=items, errors=errors)


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


def _format_http_error(exc: httpx.HTTPError) -> str:
    if isinstance(exc, httpx.HTTPStatusError):
        return f"HTTP {exc.response.status_code}: {exc}"
    return str(exc)
