"""Integration tests for the `aiagent execute` CLI command (TASK-222)."""

from __future__ import annotations

from pathlib import Path

import pytest

from aios.cli.workflow_cli import _cmd_execute


def _args(file: str, simulate: bool = False, timeout: float = 30.0, yes: bool = True):
    return type("A", (), {"file": file, "simulate": simulate, "timeout": timeout, "yes": yes})()


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


# --------------------------------------------------------------------------- #
# TASK-229 — Unified Execution Entry-Point (governance-aware execute)
# --------------------------------------------------------------------------- #
def test_simulate_emits_evidence(tmp_path, capsys):
    plan = tmp_path / "sample.md"
    plan.write_text("# Sim Plan\n- [ ] echo a\n- [ ] echo b\n", encoding="utf-8")
    assert _cmd_execute(_args(str(plan), simulate=True)) == 0
    out = capsys.readouterr().out
    assert "SIMULATED evidence record(s) emitted" in out


def test_governance_precheck_denies_missing_permission():
    from aios.cli.workflow_cli import _governance_precheck
    from aios.core.planner import ExecutionPlan, Step
    from aios.runtime.kernel import RuntimeKernel
    from aios.runtime.permission import PermissionScope

    # Kernel with NO granted permissions -> pre-check must DENY.
    kernel = RuntimeKernel()
    step = Step(
        step_id="s1",
        action="echo x",
        metadata={"scope": PermissionScope.EXECUTE, "resource": "s1", "command": "echo x"},
    )
    plan = ExecutionPlan(plan_id="p1")
    plan.add_step(step)
    ok, reason = _governance_precheck(kernel, plan)
    assert ok is False
    assert "DENY" in reason


def test_governance_precheck_allows_granted(tmp_path, monkeypatch):
    from aios.cli.workflow_cli import _governance_precheck
    from aios.core.planner import ExecutionPlan, Step
    from aios.runtime.kernel import RuntimeKernel
    from aios.runtime.permission import Permission, PermissionBroker, PermissionScope

    kernel = RuntimeKernel()
    kernel.permissions.grant("runtime", Permission(PermissionScope.EXECUTE, "*"))
    step = Step(
        step_id="s1",
        action="echo x",
        metadata={"scope": PermissionScope.EXECUTE, "resource": "s1", "command": "echo x"},
    )
    plan = ExecutionPlan(plan_id="p2")
    plan.add_step(step)
    ok, reason = _governance_precheck(kernel, plan)
    assert ok is True
