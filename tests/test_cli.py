from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest
from typer.testing import CliRunner

from agent_watch.cli import app


def _write_doctor_config(
    path: Path,
    notes_dir: Path,
    state_path: Path,
    *,
    template: Path | None = None,
    llm_provider: str = "none",
) -> None:
    template_text = f'\n    template: "{template.as_posix()}"' if template is not None else ""
    path.write_text(
        f"""
language: zh
keywords:
  include: ["agent", "智能体"]
sinks:
  default:
    type: markdown
    output_dir: "{notes_dir.as_posix()}"
    filename_template: "{{month}}-agent-watch.md"{template_text}
sources:
  - name: Fixture
    type: rss
    url: "file:///tmp/feed.xml"
llm:
  provider: {llm_provider}
state:
  path: "{state_path.as_posix()}"
""",
        encoding="utf-8",
    )


def test_init_creates_example_config_without_personal_paths(tmp_path: Path) -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["init", "--output-dir", str(tmp_path)])

    assert result.exit_code == 0
    config_text = (tmp_path / "agent-watch.yaml").read_text(encoding="utf-8")
    assert "OBSIDIAN_VAULT_PATH" in config_text
    assert "D:\\" not in config_text
    assert (tmp_path / "templates" / "obsidian_month.md.j2").exists()


def test_update_dry_run_uses_fixture_without_writing_notes(tmp_path: Path) -> None:
    fixture = Path("tests/fixtures/rss_sample.xml").resolve()
    config_path = tmp_path / "agent-watch.yaml"
    notes_dir = tmp_path / "notes"
    state_path = tmp_path / "data" / "state.sqlite"
    config_path.write_text(
        f"""
language: zh
keywords:
  include: ["agent", "workflow", "智能体"]
sinks:
  default:
    type: markdown
    output_dir: "{notes_dir.as_posix()}"
sources:
  - name: Fixture
    type: rss
    url: "file:///{fixture.as_posix()}"
llm:
  provider: none
state:
  path: "{state_path.as_posix()}"
""",
        encoding="utf-8",
    )
    runner = CliRunner()

    result = runner.invoke(app, ["update", "--config", str(config_path), "--dry-run"])

    assert result.exit_code == 0
    assert "Building workflows for agents with skills" in result.stdout
    assert not notes_dir.exists()
    assert not state_path.exists()


def test_doctor_accepts_valid_local_config(tmp_path: Path) -> None:
    config_path = tmp_path / "agent-watch.yaml"
    notes_dir = tmp_path / "notes"
    state_path = tmp_path / "data" / "state.sqlite"
    template_path = tmp_path / "templates" / "month.md.j2"
    template_path.parent.mkdir()
    template_path.write_text("# {{ month }}", encoding="utf-8")
    _write_doctor_config(config_path, notes_dir, state_path, template=template_path)
    runner = CliRunner()

    result = runner.invoke(app, ["doctor", "--config", str(config_path)])

    assert result.exit_code == 0
    assert "Configuration OK" in result.stdout
    assert "1 source" in result.stdout
    assert not notes_dir.exists()
    assert not state_path.exists()


def test_doctor_rejects_missing_config(tmp_path: Path) -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["doctor", "--config", str(tmp_path / "missing.yaml")])

    assert result.exit_code != 0
    assert "Config file not found" in result.stdout


def test_doctor_warns_when_openai_key_is_missing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    config_path = tmp_path / "agent-watch.yaml"
    notes_dir = tmp_path / "notes"
    state_path = tmp_path / "data" / "state.sqlite"
    _write_doctor_config(config_path, notes_dir, state_path, llm_provider="openai")
    runner = CliRunner()

    result = runner.invoke(app, ["doctor", "--config", str(config_path)])

    assert result.exit_code == 0
    assert "Warning" in result.stdout
    assert "OPENAI_API_KEY" in result.stdout


def test_doctor_rejects_missing_template(tmp_path: Path) -> None:
    config_path = tmp_path / "agent-watch.yaml"
    notes_dir = tmp_path / "notes"
    state_path = tmp_path / "data" / "state.sqlite"
    _write_doctor_config(
        config_path,
        notes_dir,
        state_path,
        template=tmp_path / "templates" / "missing.md.j2",
    )
    runner = CliRunner()

    result = runner.invoke(app, ["doctor", "--config", str(config_path)])

    assert result.exit_code != 0
    assert "Template not found" in result.stdout


def test_python_module_entrypoint_shows_help() -> None:
    env = {**os.environ, "PYTHONPATH": "src"}

    result = subprocess.run(
        [sys.executable, "-m", "agent_watch.cli", "--help"],
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )

    assert result.returncode == 0
    assert "Track AI agent technology updates" in result.stdout
