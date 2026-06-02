from __future__ import annotations

from datetime import UTC, datetime

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field, field_serializer


class WatchItem(BaseModel):
    """A normalized source item before ranking and summarization."""

    model_config = ConfigDict(extra="forbid")

    title: str
    url: str
    source_name: str
    source_type: str
    summary: str = ""
    published_at: datetime | None = None
    fetched_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, str | int | float | bool] = Field(default_factory=dict)

    @field_serializer("published_at", "fetched_at")
    def serialize_datetime(self, value: datetime | None) -> str | None:
        return value.isoformat() if value is not None else None


class RankedItem(WatchItem):
    """A source item with relevance and trust signals."""

    score: float = 0.0
    confidence: str = "medium"
    tags: list[str] = Field(default_factory=list)


class SummaryResult(BaseModel):
    """A Markdown-ready summary for one ranked item."""

    model_config = ConfigDict(extra="forbid")

    item: RankedItem
    takeaway: str
    why_it_matters: str
    category: str
    evidence_urls: list[str | AnyHttpUrl]

