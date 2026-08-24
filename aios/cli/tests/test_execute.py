"""Integration tests for the `aiagent execute` CLI command (TASK-222)."""

from __future__ import annotations

from pathlib import Path

import pytest

from aios.cli.workflow_cli import _cmd_execute


def _args(file: str, simulate: bool = False, timeout: float = 30.0):
    return type("A", (), {"file": file, "simulate": simulate, "timeout": timeout})()


def _write_yaml_plan(path: Path) -> None:
    path.write_text(
        "workflow:\n"
        "  name: sample\n"
        "  version: 0.1.0\n"
        "  permissions: [process.execute]\n"
        "  nodes:\n"
        "    - id: s1\n"
        "      type: task\n"
        "      command: echo hello-from-aios\n"
        "    - id: s2\n"
        "      type: task\n"
        "      command: echo second-step\n",
        encoding="utf-8",
    )


def test_execute_disabled_returns_2(tmp_path, monkeypatch):
    monkeypatch.setenv("AIOS_REAL_EXECUTION_ENABLED", "0")
    plan = tmp_path / "sample.yaml"
    _write_yaml_plan(plan)
    assert _cmd_execute(_args(str(plan), simulate=False)) == 2


def test_execute_simulate_markdown(tmp_path, capsys):
    plan = tmp_path / "sample.md"
    plan.write_text("# My Plan\n- [ ] echo hi\n- [ ] echo bye\n", encoding="utf-8")
    assert _cmd_execute(_args(str(plan), simulate=True)) == 0
    out = capsys.readouterr().out
    assert "SIMULATE" in out
    assert "echo hi" in out
    assert "echo bye" in out


def test_execute_real_runs_plan(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("AIOS_REAL_EXECUTION_ENABLED", "1")
    plan = tmp_path / "sample.yaml"
    _write_yaml_plan(plan)
    rc = _cmd_execute(_args(str(plan), simulate=False))
    assert rc == 0
    out = capsys.readouterr().out
    assert "hello-from-aios" in out
    assert "second-step" in out
    assert "[PASS]" in out
