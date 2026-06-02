from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from agent_watch.models import RankedItem, SummaryResult
from agent_watch.rendering import MarkdownRenderer


def test_obsidian_renderer_writes_monthly_research_report(tmp_path: Path) -> None:
    item = RankedItem(
        title="Building self-improving coding agents",
        url="https://example.com/coding-agents",
        source_name="OpenAI",
        source_type="rss",
        summary="An official engineering post about coding agents.",
        published_at=datetime(2026, 6, 1, tzinfo=UTC),
        score=8.5,
        confidence="high",
        tags=["engineering", "agent"],
    )
    summary = SummaryResult(
        item=item,
        takeaway="这篇文章说明智能体正在从辅助编程走向可评估、可迭代的工程系统。",
        why_it_matters="它把代码智能体的价值从一次性生成推进到持续改进。",
        category="engineering",
        evidence_urls=[item.url],
    )

    renderer = MarkdownRenderer(preset="obsidian", language="zh")
    output_path = tmp_path / "2026-06-agent-watch.md"
    renderer.write_month(output_path, month="2026-06", summaries=[summary], dry_run=False)

    text = output_path.read_text(encoding="utf-8")
    assert "title: 2026-06 智能体技术与产业月报" in text
    assert "# 2026-06 智能体技术与产业月报" in text
    assert "## 本月判断" in text
    assert "Building self-improving coding agents" in text
    assert "https://example.com/coding-agents" in text


def test_markdown_renderer_dry_run_does_not_write(tmp_path: Path) -> None:
    renderer = MarkdownRenderer(preset="markdown", language="en")
    output_path = tmp_path / "report.md"

    rendered = renderer.write_month(output_path, month="2026-06", summaries=[], dry_run=True)

    assert not output_path.exists()
    assert "# 2026-06 AI Agent Technology and Industry Report" in rendered

