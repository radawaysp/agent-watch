from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from typer.testing import CliRunner

from agent_watch.cli import app


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
