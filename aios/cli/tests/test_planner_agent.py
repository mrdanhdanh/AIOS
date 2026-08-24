"""Tests for the AIOS Planner agent/skill outputs (TASK-223).

These verify that a plan produced by the planner (sample files standing in for
the agent's output) is valid for `aiagent execute` (TASK-222) and that the
agent/skill markdown files have the required frontmatter.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from aios.runtime.workflow import WorkflowDefinition, WorkflowError
from aios.cli.workflow_cli import _cmd_execute

TESTS_DIR = Path(__file__).resolve().parent


def _args(file: str, simulate: bool = False, timeout: float = 30.0):
    return type("A", (), {"file": file, "simulate": simulate, "timeout": timeout})()


def test_sample_plan_validates():
    wf = WorkflowDefinition.from_file(str(TESTS_DIR / "plan_sample.yaml"))
    wf.validate()
    assert wf.name == "sample-plan"
    assert any(n.command for n in wf.nodes)


def test_markdown_plan_validates():
    text = (TESTS_DIR / "plan_sample.md").read_text(encoding="utf-8")
    wf = WorkflowDefinition.from_markdown(text)
    assert len(wf.nodes) == 2
    assert wf.nodes[0].command == "echo \"hello from markdown plan\""


def test_sample_plan_executes(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("AIOS_REAL_EXECUTION_ENABLED", "1")
    # Copy sample into tmp to avoid touching repo root.
    plan = tmp_path / "plan.yaml"
    plan.write_text(
        (TESTS_DIR / "plan_sample.yaml").read_text(encoding="utf-8"), encoding="utf-8"
    )
    rc = _cmd_execute(_args(str(plan), simulate=False))
    assert rc == 0
    out = capsys.readouterr().out
    assert "hello from AIOS plan" in out
    assert "[PASS]" in out


def test_agent_md_has_frontmatter():
    md = (Path(__file__).resolve().parents[3] / ".github" / "agents" / "aios-planner.agent.md")
    content = md.read_text(encoding="utf-8")
    assert content.startswith("---")
    assert "name:" in content
    assert "description:" in content
    assert "tools:" in content


def test_skill_md_has_frontmatter():
    md = (Path(__file__).resolve().parents[3] / ".github" / "skills" / "aios-plan" / "SKILL.md")
    content = md.read_text(encoding="utf-8")
    assert content.startswith("---")
    assert "name: aios-plan" in content
    assert "description:" in content
