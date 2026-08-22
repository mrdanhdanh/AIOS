"""Tests for TASK-095 — Remediation Candidate Generation + Risk Scoring (M14)."""

from __future__ import annotations

from aios.autonomy_governor.contracts import (
    AutonomyAction,
    AutonomyDecision,
    AutonomyMode,
    AutonomyPolicy,
)
from aios.autonomy_governor.governor import AutonomyGovernor
from aios.remediation_candidate.candidate import (
    Candidate,
    CandidateEngine,
    CandidateGenerator,
    CandidatePlan,
    RiskScorer,
)
from aios.remediation_detect.detect import Diagnosis, Incident, Symptom


def _diagnosis() -> Diagnosis:
    inc = Incident("inc-1", "anomaly", "major", {}, evidence_ref="ev-inc")
    syms = [Symptom("s1", "sym1", "ev-1")]
    return Diagnosis(
        "inc-1", syms, "root cause", 0.7, ["cause a", "cause b"], evidence_ref="ev-d"
    )


def _denying_governor() -> AutonomyGovernor:
    # Policy that denies destructive actions (fail-closed removal).
    policy = AutonomyPolicy(mode=AutonomyMode.SUPERVISED, actions={"destructive": "deny"})
    return AutonomyGovernor(policy=policy)


def _delete_candidate_id() -> str:
    gen = CandidateGenerator()
    return [c.candidate_id for c in gen.generate(_diagnosis()) if c.action == "delete_data"][0]


def test_generate_from_diagnosis():
    gen = CandidateGenerator()
    cands = gen.generate(_diagnosis())
    assert len(cands) >= 5
    assert all(c.source_diagnosis_id == "inc-1" for c in cands)
    assert any(c.action == "delete_data" for c in cands)


def test_risk_score_evidence_based():
    scorer = RiskScorer()
    c = Candidate("c1", "inc-1", "restart_service", 0.0, True, 0.1, blast_radius="local", impact=0.2)
    scored = scorer.score(c)
    # local radius (0.1) + impact 0.2*0.5 + rollback 0.1*0.3 = 0.1+0.1+0.03 = 0.23
    assert scored.risk_score == 0.23
    # global radius is riskier than local for same impact/rollback
    cg = Candidate("c2", "inc-1", "isolate_node", 0.0, True, 0.5, blast_radius="global", impact=0.6)
    assert scorer.score(cg).risk_score > scored.risk_score


def test_policy_violation_removed():
    eng = CandidateEngine(governor=_denying_governor())
    plan = eng.run(_diagnosis())
    # Destructive candidate must be rejected (fail-closed).
    assert "delete_data" not in [c.action for c in plan.candidates]
    assert plan.rejected
    assert _delete_candidate_id() in plan.rejected


def test_deterministic_ranking():
    eng = CandidateEngine()
    p1 = eng.run(_diagnosis())
    p2 = eng.run(_diagnosis())
    assert eng.result_hash(p1) == eng.result_hash(p2)
    assert [c.candidate_id for c in p1.candidates] == [c.candidate_id for c in p2.candidates]


def test_candidate_provenance():
    eng = CandidateEngine()
    plan = eng.run(_diagnosis())
    assert eng.provenance_complete(plan) is True
    assert plan.evidence_ref


def test_ranked_low_risk_first():
    eng = CandidateEngine()
    plan = eng.run(_diagnosis())
    scores = [c.risk_score for c in plan.candidates]
    assert scores == sorted(scores)
    # lowest-risk candidate should be a local/low-impact action
    assert plan.candidates[0].risk_score <= plan.candidates[-1].risk_score


def test_engine_full_flow_plan():
    eng = CandidateEngine()
    plan = eng.run(_diagnosis())
    assert isinstance(plan, CandidatePlan)
    assert plan.source_diagnosis_id == "inc-1"
    assert len(plan.candidates) > 0
    # every surviving candidate is policy compliant
    assert all(c.policy_compliant for c in plan.candidates)
