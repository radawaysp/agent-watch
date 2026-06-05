# Changelog

All notable changes to Agent Watch will be documented in this file.

## Unreleased

## 0.1.1 - 2026-06-05

Added `agent-watch doctor`, a no-network configuration diagnostics command for checking local config files, output paths, templates, state path setup, and optional LLM environment warnings.

Added per-source HTTP timeout, retry, backoff, and continue-on-error behavior so temporary failures in one source do not block successful sources from being collected.

Changed `agent-watch update` to leave an existing monthly report untouched when there are no new items to write, preventing scheduled runs from overwriting a report with an empty update.

Added Docker deployment documentation and a reusable Dockerfile for isolated Linux and cron-based deployments.

Added offline fixture coverage for arXiv and Semantic Scholar adapters, including Semantic Scholar rate-limit reporting.

Updated the scheduled GitHub Actions example to use `actions/checkout@v6` and `actions/setup-python@v6`.

Improved local test discovery by adding the `src/` package path to pytest configuration, so `python -m pytest` works in a fresh checkout before editable installation.

## 0.1.0 - 2026-06-02

Initial public release candidate.

This release introduces the `agent-watch` CLI, source adapters for RSS, arXiv, Semantic Scholar, GitHub, and Hacker News, ranking and confidence scoring, SQLite-based deduplication, Markdown and Obsidian report rendering, structured LLM summarization with fallback behavior, CI, tests, and open-source project documentation.

The release establishes the first maintainable baseline for public development, release validation, and future source adapter expansion.
