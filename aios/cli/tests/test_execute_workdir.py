"""Tests for the work-dir + confirm flow of `aiagent execute` (TASK-224)."""

from __future__ import annotations

from pathlib import Path

import pytest

from aios.cli.workflow_cli import _cmd_execute


def _args(file: str, work_dir=None, yes=False, simulate=False, timeout=30.0):
    return type(
        "A", (), {"file": file, "work_dir": work_dir, "yes": yes,
                  "simulate": simulate, "timeout": timeout}
    )()


def _write_plan(path: Path) -> None:
    path.write_text(
        "workflow:\n"
        "  name: wd-plan\n"
        "  version: 0.1.0\n"
        "  permissions: [process.execute]\n"
        "  nodes:\n"
        "    - id: s1\n"
        "      type: task\n"
        "      command: echo inside-workdir\n",
        encoding="utf-8",
    )


def test_workdir_created_and_plan_inside(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("AIOS_REAL_EXECUTION_ENABLED", "1")
    wd = tmp_path / "20260824-webno1"
    plan = tmp_path / "plan.yaml"
    _write_plan(plan)
    rc = _cmd_execute(_args(str(plan), work_dir=str(wd), yes=True))
    assert rc == 0
    assert wd.is_dir()
    assert (wd / "plan.yaml").exists()
    out = capsys.readouterr().out
    assert "inside-workdir" in out


def test_workdir_confines_cwd(tmp_path, monkeypatch):
    monkeypatch.setenv("AIOS_REAL_EXECUTION_ENABLED", "1")
    wd = tmp_path / "20260824-x"
    wd.mkdir()
    # A plan whose node requests a cwd OUTSIDE the allowed work dir must be denied.
    plan = tmp_path / "plan.yaml"
    plan.write_text(
        "workflow:\n"
        "  name: escape\n"
        "  version: 0.1.0\n"
        "  permissions: [process.execute]\n"
        "  nodes:\n"
        "    - id: s1\n"
        "      type: task\n"
        "      command: echo escaped\n"
        "      cwd: " + str(tmp_path / "outside") + "\n",
        encoding="utf-8",
    )
    # Should be denied because the node cwd escapes the allowed work dir.
    rc = _cmd_execute(_args(str(plan), work_dir=str(wd), yes=True))
    assert rc != 0


def test_yes_flag_skips_prompt(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("AIOS_REAL_EXECUTION_ENABLED", "1")
    wd = tmp_path / "20260824-y"
    plan = tmp_path / "plan.yaml"
    _write_plan(plan)
    rc = _cmd_execute(_args(str(plan), work_dir=str(wd), yes=True))
    assert rc == 0
    out = capsys.readouterr().out
    assert "Aborted" not in out


def test_no_yes_prompts_and_aborts(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("AIOS_REAL_EXECUTION_ENABLED", "1")
    wd = tmp_path / "20260824-n"
    plan = tmp_path / "plan.yaml"
    _write_plan(plan)
    monkeypatch.setattr("builtins.input", lambda *a, **k: "n")
    rc = _cmd_execute(_args(str(plan), work_dir=str(wd), yes=False))
    assert rc == 3
    assert "Aborted" in capsys.readouterr().out
