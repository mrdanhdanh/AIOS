"""Tests for the repair planner (T149)."""

import pytest

from aios.coding_loop import DiagnosticAgent, ExecutionObservation, FailureClassifier, RepairPlanner
from aios.coding_loop._common import CodingLoopError


def _report(trace):
    o = ExecutionObservation()
    obs = o.capture("exec1", "loop1", trace, evidence_ref="ev1")
    fc = FailureClassifier().classify(obs)
    return DiagnosticAgent().diagnose(fc)


def test_plan_with_rollback():
    p = RepairPlanner()
    rep = _report(("SyntaxError: bad token",))
    plan = p.plan(rep, rollback_ref="rb1")
    assert plan.plan_id
    assert plan.rollback_ref == "rb1"
    assert plan.patch_spec.startswith("patch<")


def test_plan_missing_rollback_rejected():
    p = RepairPlanner()
    rep = _report(("RuntimeError",))
    with pytest.raises(CodingLoopError):
        p.plan(rep, rollback_ref="")  # fail-closed (T055)


def test_plan_from_unknown_rejected():
    p = RepairPlanner()
    rep = _report(("nothing relevant",))  # UNKNOWN diagnosis
    with pytest.raises(CodingLoopError):
        p.plan(rep, rollback_ref="rb1")  # fail-closed (T078)


def test_deterministic_same_diagnosis_same_plan():
    p1 = RepairPlanner()
    p2 = RepairPlanner()
    rep1 = _report(("Timeout exceeded",))
    rep2 = _report(("Timeout exceeded",))
    assert p1.plan(rep1, rollback_ref="rb1").patch_spec == p2.plan(rep2, rollback_ref="rb1").patch_spec


def test_duplicate_plan_id_rejected():
    p = RepairPlanner()
    rep = _report(("MemoryError",))
    p.plan(rep, rollback_ref="rb1", plan_id="plan1")
    with pytest.raises(CodingLoopError):
        p.plan(rep, rollback_ref="rb1", plan_id="plan1")


def test_plan_requires_provenance():
    p = RepairPlanner()
    from aios.coding_loop.diagnostic import DiagnosticReport

    bad = DiagnosticReport("r1", "fc1", "obs1", "undetermined", 0.6, evidence_ref="ev-tmp")
    object.__setattr__(bad, "evidence_ref", "")
    with pytest.raises(CodingLoopError):
        p.plan(bad, rollback_ref="rb1")


def test_provenance_hash():
    p = RepairPlanner()
    rep = _report(("SyntaxError",))
    plan = p.plan(rep, rollback_ref="rb1")
    prov = p.provenance(plan.plan_id)
    assert prov["content_hash"]
    assert prov["rollback_ref"] == "rb1"
