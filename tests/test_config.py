from __future__ import annotations

from pathlib import Path

import pytest

from agent_watch.config import WatchConfig, load_config


def test_load_config_expands_env_and_defaults(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("NOTES_DIR", str(tmp_path / "vault"))
    config_path = tmp_path / "agent-watch.yaml"
    config_path.write_text(
        """
language: zh
keywords:
  include: ["agent", "智能体"]
sinks:
  default:
    type: obsidian
    output_dir: "${NOTES_DIR}/技术学习"
sources:
  - name: OpenAI
    type: rss
    url: https://openai.com/news/rss.xml
llm:
  provider: none
""",
        encoding="utf-8",
    )

    config = load_config(config_path)

    assert config.language == "zh"
    assert config.sources[0].name == "OpenAI"
    assert config.sinks.default.output_dir == tmp_path / "vault" / "技术学习"
    assert config.output_filename("2026-06") == "2026-06-agent-watch.md"


def test_config_rejects_empty_sources() -> None:
    with pytest.raises(ValueError, match="at least one source"):
        WatchConfig(sources=[])
