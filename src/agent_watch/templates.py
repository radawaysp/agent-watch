from __future__ import annotations

DEFAULT_CONFIG = """# Agent Watch starter configuration.
# Keep personal paths and API keys in environment variables, not in this file.
language: zh

keywords:
  include:
    - agent
    - ai agent
    - llm agent
    - agentic
    - 智能体
    - 工具调用
  exclude: []

sinks:
  default:
    type: obsidian
    output_dir: "${OBSIDIAN_VAULT_PATH}/技术学习/智能体/月度追踪"
    filename_template: "{month}-agent-watch.md"
    template: templates/obsidian_month.md.j2

schedule:
  cadence: weekly
  timezone: Asia/Shanghai

llm:
  provider: openai
  model: gpt-5-mini
  structured_output: true
  max_items_per_run: 12
  max_cost_usd: 3.0

state:
  path: data/state.sqlite

sources:
  - name: OpenAI News
    type: rss
    url: https://openai.com/news/rss.xml
    limit: 20
  - name: arXiv AI Agents
    type: arxiv
    query: 'cat:cs.AI AND (agent OR agents OR tool)'
    limit: 20
  - name: Semantic Scholar Agents
    type: semantic_scholar
    query: AI agents tool use planning evaluation
    limit: 20
  - name: GitHub Agent Projects
    type: github
    query: 'ai-agent OR llm-agent OR agentic-ai stars:>100'
    limit: 20
  - name: Hacker News Agent Signal
    type: hackernews
    query: AI agent
    limit: 10
"""

OBSIDIAN_TEMPLATE = """---
title: {{ month }} 智能体技术与产业月报
month: {{ month }}
tags:
  - ai-agents
  - 技术学习
  - 月报
last_updated: {{ last_updated }}
status: active
---

# {{ month }} 智能体技术与产业月报

## 本月判断

用自然段写出本月最重要的判断，避免只堆砌项目符号。

## 趋势总览

在表格前解释它的阅读方式，说明哪些是事实来源，哪些只是热度信号。

## 每周更新

按周追加来源解读，每条内容保留原文链接、来源和置信度。

## 重点来源索引

在索引表格前后补充解释，方便读者理解表格不是结论本身。

## 下月关注

写出下月继续观察的技术问题、开源项目和产业采用线索。
"""

MARKDOWN_TEMPLATE = """# {{ month }} AI Agent Technology and Industry Report

## Monthly Read

Write a short narrative synthesis instead of a link dump.

## Trend Overview

Explain how to read the table before showing it.

## Weekly Updates

Append weekly updates with source URLs and confidence.

## Source Index

Keep traceability fields for later review.

## Next Month Watchlist

Capture follow-up questions and projects.
"""

