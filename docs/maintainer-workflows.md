# Maintainer Workflows

Agent Watch is designed for maintainers who need to follow a fast-moving AI agent ecosystem while still keeping their own repository work grounded in evidence. The project is intentionally small, testable, and automation-friendly so review and release work can stay repeatable.

## Pull Request Review

Maintainers can review changes to source adapters, ranking behavior, Markdown rendering, and configuration validation against a stable set of expectations. A typical review checks whether new adapters preserve source URLs, publication dates, confidence values, and deterministic fixture tests.

## Issue Triage

Incoming issues should be grouped into configuration problems, source adapter failures, rendering defects, documentation requests, and feature proposals. Agent Watch keeps clear boundaries between adapters, state, ranking, summarization, and rendering, which makes issue triage easier to route.

## Release Validation

Before a release, maintainers should compare the changelog, roadmap, tests, examples, and README against the actual diff. The release workflow should verify that generated notes and local SQLite state are not committed, that dry-run remains side-effect free, and that public documentation still explains what the tool does within the first screen.

## Source Adapter Regression Tests

Source adapters are the most likely area to break because external feeds and APIs evolve. Maintainer automation should use saved fixtures to check whether RSS, arXiv, Semantic Scholar, GitHub, and Hacker News items still normalize into the same `WatchItem` shape.

## Summary Quality Regression

Agent Watch uses structured LLM output when available and falls back to deterministic summaries when unavailable. Summary quality checks should confirm that generated summaries keep the evidence URL, avoid treating community signals as primary facts, and preserve the distinction between research, open-source, industry, and community categories.

## Release Automation

The long-term maintenance workflow is to let GitHub Actions run Agent Watch on a schedule, open a draft monthly report PR, and apply automated checks for traceability, duplication, and source policy consistency. This keeps the project focused on reliable reports rather than ad hoc link collection.
