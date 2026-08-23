"""Unit + Contract + Integration + Architecture + Regression tests (TASK-126)."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from aios.coder.planner import (
    CodingPlanner,
    PlanStatus,
    PlanVerifyError,
    PlanVerifier,
)


# --------------------------------------------------------------------------- #
# Deterministic-first
# --------------------------------------------------------------------------- #
def test_plan_by_rule_llm_call_zero():
    p = CodingPlanner()
    plan = p.plan("please add function to module")
    assert plan.planner_deterministic is True
    assert plan.llm_call_count == 0
    assert len(plan.steps) > 0


def test_rule_insufficient_llm_fallback_called():
    p = CodingPlanner()
    calls = {"n": 0}

    def fallback(req):
        calls["n"] += 1
        return [("create", "x.py"), ("test", "t.py")]

    plan = p.plan("do something totally unknown", llm_fallback=fallback)
    assert calls["n"] == 1
    assert plan.llm_call_count == 1
    assert plan.planner_deterministic is False


def test_deterministic_same_request_same_plan():
    p = CodingPlanner()
    a = p.plan("fix bug in parser")
    b = p.plan("fix bug in parser")
    assert a.content_hash == b.content_hash
    assert [s.action for s in a.steps] == [s.action for s in b.steps]


# --------------------------------------------------------------------------- #
# PlanVerifier — fail-closed
# --------------------------------------------------------------------------- #
def test_verifier_accepts_valid_plan():
    p = CodingPlanner()
    plan = p.plan("add function")
    verified = PlanVerifier().verify(plan)
    assert verified.verified is True
    assert verified.status is PlanStatus.VERIFIED


def test_verifier_rejects_empty_plan():
    p = CodingPlanner()
    plan = p.plan("unknown intent with no rule match", llm_fallback=lambda r: [])
    with pytest.raises(PlanVerifyError):
        PlanVerifier().verify(plan)


def test_verifier_rejects_policy():
    p = CodingPlanner()
    plan = p.plan("add function")
    with pytest.raises(PlanVerifyError):
        PlanVerifier().verify(plan, policy_ok=False)


def test_verifier_rejects_bad_target():
    from aios.coder.planner import CodingPlan, CodingStep

    plan = CodingPlan(
        plan_id="x",
        agent_ref="coder-1",
        steps=[CodingStep(action="create", target="bad; rm -rf /")],
        planner_deterministic=True,
        verified=False,
        llm_call_count=0,
        evidence_id="ev-x",
        content_hash="0" * 64,
    )
    with pytest.raises(PlanVerifyError):
        PlanVerifier().verify(plan)


# --------------------------------------------------------------------------- #
# Provenance
# --------------------------------------------------------------------------- #
def test_plan_has_provenance():
    p = CodingPlanner()
    plan = p.plan("refactor module")
    assert plan.evidence_id.startswith("ev-")
    assert len(plan.content_hash) == 64


# --------------------------------------------------------------------------- #
# Architecture — no forbidden imports
# --------------------------------------------------------------------------- #
def test_module_has_no_forbidden_imports():
    src = Path(__file__).resolve().parents[1] / "planner.py"
    tree = ast.parse(src.read_text(encoding="utf-8"))
    forbidden = {"subprocess", "os", "aios.runtime.providers", "aios.runtime.filesystem"}
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                imported.add(n.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            imported.add(node.module or "")
    assert not (imported & forbidden), f"forbidden imports: {imported & forbidden}"
