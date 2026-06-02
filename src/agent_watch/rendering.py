from __future__ import annotations

from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path

from agent_watch.models import SummaryResult


class MarkdownRenderer:
    def __init__(self, preset: str = "markdown", language: str = "zh") -> None:
        if preset not in {"markdown", "obsidian"}:
            raise ValueError("preset must be 'markdown' or 'obsidian'")
        self.preset = preset
        self.language = language

    def write_month(
        self,
        output_path: Path,
        month: str,
        summaries: list[SummaryResult],
        dry_run: bool = False,
    ) -> str:
        rendered = self.render_month(month=month, summaries=summaries)
        if dry_run:
            return rendered
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered, encoding="utf-8")
        return rendered

    def render_month(self, month: str, summaries: list[SummaryResult]) -> str:
        if self.language == "zh":
            return self._render_zh(month, summaries)
        return self._render_en(month, summaries)

    def _render_zh(self, month: str, summaries: list[SummaryResult]) -> str:
        title = f"{month} 智能体技术与产业月报"
        sections = []
        if self.preset == "obsidian":
            sections.append(
                "\n".join(
                    [
                        "---",
                        f"title: {title}",
                        f"month: {month}",
                        "tags:",
                        "  - ai-agents",
                        "  - 技术学习",
                        "  - 月报",
                        f"last_updated: {datetime.now(UTC).date().isoformat()}",
                        "status: active",
                        "---",
                        "",
                    ]
                )
            )
        sections.append(f"# {title}\n")
        sections.append(
            "## 本月判断\n\n"
            + self._monthly_judgement_zh(summaries)
            + "\n"
        )
        sections.append(
            "## 趋势总览\n\n"
            "下表把本次采集到的内容按研究、工程、开源、产业和社区信号归类。"
            "表格用于快速定位来源，具体判断仍以每条内容后的解释为准。\n\n"
            + self._category_table(summaries)
            + "\n这些分类帮助后续回看时区分事实来源和热度来源，"
            "尤其要注意社区信号不能单独作为结论依据。\n"
        )
        sections.append("## 每周更新\n\n" + self._weekly_updates_zh(summaries) + "\n")
        sections.append(
            "## 重点来源索引\n\n"
            "下面的索引保留了原文链接、来源、发布时间、采集时间和置信度，"
            "方便在 Obsidian 或普通 Markdown 中追溯。\n\n"
            + self._source_table(summaries)
            + "\n保留这些字段是为了避免摘要脱离原文，也方便以后做去重、复盘和可信度校验。\n"
        )
        sections.append("## 下月关注\n\n" + self._next_month_zh(summaries) + "\n")
        return "\n".join(sections).rstrip() + "\n"

    def _render_en(self, month: str, summaries: list[SummaryResult]) -> str:
        title = f"{month} AI Agent Technology and Industry Report"
        sections = [f"# {title}\n"]
        sections.append(
            "## Monthly Read\n\n"
            + self._monthly_judgement_en(summaries)
            + "\n"
        )
        sections.append(
            "## Trend Overview\n\n"
            "The table groups collected items by category so readers can scan the source mix "
            "before reading the narrative notes.\n\n"
            + self._category_table(summaries)
            + "\nThe categories separate primary sources from community signals, "
            "which should not be treated as facts by themselves.\n"
        )
        sections.append("## Weekly Updates\n\n" + self._weekly_updates_en(summaries) + "\n")
        sections.append(
            "## Source Index\n\n"
            "This index keeps the original URL, source, publication date, collection time, "
            "and confidence for traceability.\n\n"
            + self._source_table(summaries)
            + "\nThese fields keep generated summaries anchored to their sources "
            "and make later review easier.\n"
        )
        sections.append("## Next Month Watchlist\n\n" + self._next_month_en(summaries) + "\n")
        return "\n".join(sections).rstrip() + "\n"

    def _monthly_judgement_zh(self, summaries: list[SummaryResult]) -> str:
        if not summaries:
            return (
                "本次运行没有发现新的高相关内容。"
                "建议检查关键词、来源配置，或等待下一轮自动更新。"
            )
        top = summaries[0]
        return (
            f"本次更新最值得关注的是《{top.item.title}》。{top.takeaway}"
            f"{top.why_it_matters}整体来看，智能体领域仍需要同时跟踪工程能力、评测方法、"
            "开源生态和产业采用速度，单一新闻不足以构成趋势判断。"
        )

    def _monthly_judgement_en(self, summaries: list[SummaryResult]) -> str:
        if not summaries:
            return (
                "This run found no new high-relevance items. Check the keywords and sources, "
                "or wait for the next scheduled update."
            )
        top = summaries[0]
        return (
            f"The most notable item in this run is '{top.item.title}'. {top.takeaway} "
            f"{top.why_it_matters} Overall, agent tracking should combine engineering capability, "
            "evaluation practice, open-source momentum, and industry adoption."
        )

    def _weekly_updates_zh(self, summaries: list[SummaryResult]) -> str:
        if not summaries:
            return "### 本周更新\n\n没有新增内容写入。"
        today = datetime.now(UTC).date().isoformat()
        paragraphs = [f"### {today} 更新"]
        for summary in summaries:
            paragraphs.append(
                "\n".join(
                    [
                        f"#### [{summary.item.title}]({summary.item.url})",
                        "",
                        f"{summary.takeaway}{summary.why_it_matters}",
                        "",
                        f"来源：{summary.item.source_name}；分类：{summary.category}；置信度：{summary.item.confidence}。",
                    ]
                )
            )
        return "\n\n".join(paragraphs)

    def _weekly_updates_en(self, summaries: list[SummaryResult]) -> str:
        if not summaries:
            return "### This Week\n\nNo new items were written."
        today = datetime.now(UTC).date().isoformat()
        paragraphs = [f"### {today} Update"]
        for summary in summaries:
            paragraphs.append(
                "\n".join(
                    [
                        f"#### [{summary.item.title}]({summary.item.url})",
                        "",
                        f"{summary.takeaway} {summary.why_it_matters}",
                        "",
                        f"Source: {summary.item.source_name}; category: {summary.category}; "
                        f"confidence: {summary.item.confidence}.",
                    ]
                )
            )
        return "\n\n".join(paragraphs)

    def _category_table(self, summaries: list[SummaryResult]) -> str:
        if not summaries:
            return "| Category | Count |\n| --- | --- |\n| none | 0 |"
        counts: dict[str, int] = defaultdict(int)
        for summary in summaries:
            counts[summary.category] += 1
        rows = ["| Category | Count |", "| --- | --- |"]
        rows.extend(f"| {category} | {count} |" for category, count in sorted(counts.items()))
        return "\n".join(rows)

    def _source_table(self, summaries: list[SummaryResult]) -> str:
        rows = [
            "| Title | Source | Published | Fetched | Confidence | URL |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
        if not summaries:
            rows.append("| No new item | - | - | - | - | - |")
            return "\n".join(rows)
        for summary in summaries:
            item = summary.item
            published = item.published_at.date().isoformat() if item.published_at else "-"
            fetched = item.fetched_at.date().isoformat()
            rows.append(
                f"| {self._escape(item.title)} | {self._escape(item.source_name)} | {published} | "
                f"{fetched} | {item.confidence} | {item.url} |"
            )
        return "\n".join(rows)

    def _next_month_zh(self, summaries: list[SummaryResult]) -> str:
        categories = sorted({summary.category for summary in summaries})
        if not categories:
            return (
                "下月先维持当前来源池，重点观察是否出现新的评测基准、"
                "主流框架版本更新和企业级落地案例。"
            )
        joined = "、".join(categories[:5])
        return f"下月建议继续围绕 {joined} 跟踪新增证据，并优先复核官方发布、论文和开源仓库。"

    def _next_month_en(self, summaries: list[SummaryResult]) -> str:
        categories = sorted({summary.category for summary in summaries})
        if not categories:
            return (
                "Keep the current source pool and watch for new benchmarks, "
                "framework releases, and enterprise adoption cases."
            )
        joined = ", ".join(categories[:5])
        return (
            f"Continue tracking new evidence around {joined}, with priority on official posts, "
            "papers, and repositories."
        )

    def _escape(self, value: str) -> str:
        return value.replace("|", "\\|").replace("\n", " ")
