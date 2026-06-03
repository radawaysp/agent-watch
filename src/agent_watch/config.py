from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class KeywordsConfig(BaseModel):
    include: list[str] = Field(default_factory=lambda: ["agent", "ai agent", "智能体"])
    exclude: list[str] = Field(default_factory=list)


class SourceConfig(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: str
    type: Literal["rss", "arxiv", "semantic_scholar", "github", "hackernews"]
    url: str | None = None
    query: str | None = None
    limit: int = Field(default=20, gt=0)
    api_key_env: str | None = None
    timeout_seconds: float = Field(default=20.0, gt=0)
    retries: int = Field(default=0, ge=0)
    retry_backoff_seconds: float = Field(default=1.0, ge=0)
    continue_on_error: bool = True


class SinkConfig(BaseModel):
    type: Literal["markdown", "obsidian"] = "markdown"
    output_dir: Path = Path("notes")
    filename_template: str = "{month}-agent-watch.md"
    template: str | None = None

    @field_validator("output_dir", mode="before")
    @classmethod
    def expand_output_dir(cls, value: str | Path) -> Path:
        if isinstance(value, Path):
            return value
        return Path(os.path.expandvars(value)).expanduser()


class SinksConfig(BaseModel):
    default: SinkConfig = Field(default_factory=SinkConfig)


class ScheduleConfig(BaseModel):
    cadence: str = "weekly"
    timezone: str = "Asia/Shanghai"


class LLMConfig(BaseModel):
    provider: Literal["none", "openai"] = "openai"
    model: str = "gpt-5-mini"
    structured_output: bool = True
    max_items_per_run: int = 12
    max_cost_usd: float | None = None


class StateConfig(BaseModel):
    path: Path = Path("data/state.sqlite")

    @field_validator("path", mode="before")
    @classmethod
    def expand_path(cls, value: str | Path) -> Path:
        if isinstance(value, Path):
            return value
        return Path(os.path.expandvars(value)).expanduser()


class WatchConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    language: Literal["zh", "en"] = "zh"
    keywords: KeywordsConfig = Field(default_factory=KeywordsConfig)
    sources: list[SourceConfig]
    sinks: SinksConfig = Field(default_factory=SinksConfig)
    schedule: ScheduleConfig = Field(default_factory=ScheduleConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    state: StateConfig = Field(default_factory=StateConfig)

    @model_validator(mode="after")
    def require_sources(self) -> WatchConfig:
        if not self.sources:
            raise ValueError("configuration must define at least one source")
        return self

    def output_filename(self, month: str) -> str:
        return self.sinks.default.filename_template.format(month=month)

    def output_path(self, month: str) -> Path:
        return self.sinks.default.output_dir / self.output_filename(month)


def load_config(path: str | Path) -> WatchConfig:
    config_path = Path(path)
    raw = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    expanded = _expand_env(raw)
    return WatchConfig.model_validate(expanded)


def _expand_env(value: Any) -> Any:
    if isinstance(value, str):
        return os.path.expandvars(value)
    if isinstance(value, list):
        return [_expand_env(item) for item in value]
    if isinstance(value, dict):
        return {key: _expand_env(item) for key, item in value.items()}
    return value
