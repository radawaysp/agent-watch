from __future__ import annotations

import json
from importlib import import_module
from typing import Any

from pydantic import BaseModel, Field

from agent_watch.config import LLMConfig
from agent_watch.models import RankedItem, SummaryResult


class StructuredSummary(BaseModel):
    takeaway: str = Field(min_length=1)
    why_it_matters: str = Field(min_length=1)
    category: str = Field(min_length=1)


SUMMARY_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "takeaway": {"type": "string"},
        "why_it_matters": {"type": "string"},
        "category": {"type": "string"},
    },
    "required": ["takeaway", "why_it_matters", "category"],
    "additionalProperties": False,
}


class Summarizer:
    def __init__(self, config: LLMConfig, language: str = "zh") -> None:
        self.config = config
        self.language = language

    def summarize(self, items: list[RankedItem]) -> list[SummaryResult]:
        limited = items[: self.config.max_items_per_run]
        if self.config.provider == "openai":
            return [self._summarize_with_fallback(item) for item in limited]
        return [self._heuristic_summary(item) for item in limited]

    def _summarize_with_fallback(self, item: RankedItem) -> SummaryResult:
        try:
            structured = self._openai_summary(item)
            return SummaryResult(
                item=item,
                takeaway=structured.takeaway,
                why_it_matters=structured.why_it_matters,
                category=structured.category,
                evidence_urls=[item.url],
            )
        except Exception:
            return self._heuristic_summary(item)

    def _openai_summary(self, item: RankedItem) -> StructuredSummary:
        openai_module = import_module("openai")
        client = openai_module.OpenAI()
        prompt = self._prompt(item)
        response = client.responses.create(
            model=self.config.model,
            input=prompt,
            text={
                "format": {
                    "type": "json_schema",
                    "name": "agent_watch_summary",
                    "schema": SUMMARY_SCHEMA,
                    "strict": True,
                }
            },
        )
        raw_text = getattr(response, "output_text", "")
        parsed = json.loads(raw_text)
        return StructuredSummary.model_validate(parsed)

    def _heuristic_summary(self, item: RankedItem) -> SummaryResult:
        if self.language == "zh":
            takeaway = item.summary or f"{item.title} 是一条与智能体相关的新增来源。"
            why = (
                "这条内容值得纳入跟踪，因为它和当前配置的智能体关键词匹配，"
                f"来源可信度为 {item.confidence}。"
            )
        else:
            takeaway = item.summary or f"{item.title} is a new AI-agent-related source item."
            why = (
                "This item is worth tracking because it matches the configured agent keywords "
                f"with {item.confidence} confidence."
            )
        return SummaryResult(
            item=item,
            takeaway=takeaway,
            why_it_matters=why,
            category=self._category(item),
            evidence_urls=[item.url],
        )

    def _prompt(self, item: RankedItem) -> str:
        target_language = "Chinese" if self.language == "zh" else "English"
        return (
            f"Summarize this AI agent technology update in {target_language}. "
            "Return only JSON that matches the provided schema.\n\n"
            f"Title: {item.title}\n"
            f"Source: {item.source_name} ({item.source_type})\n"
            f"URL: {item.url}\n"
            f"Summary: {item.summary}\n"
        )

    def _category(self, item: RankedItem) -> str:
        if item.source_type in {"arxiv", "semantic_scholar"}:
            return "research"
        if item.source_type == "github":
            return "open-source"
        if item.source_type == "hackernews":
            return "community-signal"
        return "industry"
