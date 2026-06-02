# Changelog

All notable changes to Agent Watch will be documented in this file.

## Unreleased

Added `agent-watch doctor`, a no-network configuration diagnostics command for checking local config files, output paths, templates, state path setup, and optional LLM environment warnings.

Improved local test discovery by adding the `src/` package path to pytest configuration, so `python -m pytest` works in a fresh checkout before editable installation.

## 0.1.0 - 2026-06-02

Initial public release candidate.

This release introduces the `agent-watch` CLI, source adapters for RSS, arXiv, Semantic Scholar, GitHub, and Hacker News, ranking and confidence scoring, SQLite-based deduplication, Markdown and Obsidian report rendering, structured LLM summarization with fallback behavior, CI, tests, and open-source project documentation.

The release establishes the first maintainable baseline for public development, release validation, and future source adapter expansion.
