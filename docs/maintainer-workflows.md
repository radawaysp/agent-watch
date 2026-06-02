# Maintainer Workflows

Agent Watch is designed for maintainers who need to follow a fast-moving AI agent ecosystem while still keeping their own repository work grounded in evidence. The project is intentionally small, testable, and automation-friendly so Codex and API credits can be used for concrete open-source maintenance tasks rather than vague productivity claims.

## Pull Request Review

Codex can review changes to source adapters, ranking behavior, Markdown rendering, and configuration validation. A typical review checks whether new adapters preserve source URLs, publication dates, confidence values, and deterministic fixture tests. API credits can support automated review comments or summaries for pull requests that change source parsing or report generation.

## Issue Triage

Maintainers can use Codex to group incoming issues into configuration problems, source adapter failures, rendering defects, documentation requests, and feature proposals. Agent Watch already keeps clear boundaries between adapters, state, ranking, summarization, and rendering, which makes issue triage easier to route.

## Release Validation

Before a release, Codex can help compare the changelog, roadmap, tests, examples, and README against the actual diff. The release workflow should verify that generated notes and local SQLite state are not committed, that dry-run remains side-effect free, and that the public documentation still explains what the tool does within the first screen.

## Source Adapter Regression Tests

Source adapters are the most likely area to break because external feeds and APIs evolve. API credits can support maintainer automation that generates test cases from saved fixtures, proposes parser updates, and checks whether RSS, arXiv, Semantic Scholar, GitHub, and Hacker News items still normalize into the same `WatchItem` shape.

## Summary Quality Regression

Agent Watch uses structured LLM output when available and falls back to deterministic summaries when unavailable. Codex/API credits can help test summary quality against fixture items by checking whether generated summaries keep the evidence URL, avoid treating community signals as primary facts, and preserve the distinction between research, open-source, industry, and community categories.

## Release Automation

The long-term maintenance workflow is to let GitHub Actions run Agent Watch on a schedule, open a draft monthly report PR, and use Codex to review whether the generated report is traceable, non-duplicative, and consistent with the repository's source policy. This keeps the project aligned with the Codex for Open Source focus on PR review, maintainer automation, and release workflows.

