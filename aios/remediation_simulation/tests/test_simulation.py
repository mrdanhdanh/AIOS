"""Tests for TASK-096 — Remediation Simulation + Meta-Verification Gate (M14)."""

from __future__ import annotations

from aios.remediation_candidate.candidate import Candidate
from aios.remediation_simulation.simulation import (
    Sandbox,
    SimulationEngine,
    SimulationGate,
    SimulationGateEngine,
    SimulationResult,
)


def _candidate(risk: float = 0.2, action: str = "restart_service") -> Candidate:
    return Candidate(
        candidate_id="cand-1",
        source_diagnosis_id="inc-1",
        action=action,
        risk_score=risk,
        policy_compliant=True,
        rollback_cost=0.1,
        blast_radius="local",
        impact=0.2,
        autonomy_action="execute",
    )


def _sandbox() -> Sandbox:
    return Sandbox("sbx-1")


def test_simulate_pass_meta_pass_gate_pass():
    eng = SimulationGateEngine()
    res = eng.run(_candidate(risk=0.2), _sandbox(), simulate_fn=lambda c: "pass")
    assert isinstance(res, SimulationResult)
    assert res.observed_outcome == "pass"
    assert res.meta_verified is True
    assert res.gate is SimulationGate.PASS


def test_simulate_fail_rejects():
    eng = SimulationGateEngine()
    res = eng.run(_candidate(risk=0.2), _sandbox(), simulate_fn=lambda c: "fail")
    assert res.observed_outcome == "fail"
    assert res.gate is SimulationGate.REJECT  # fail-closed


def test_meta_verify_fail_rejects():
    eng = SimulationGateEngine()
    # Simulation says pass, but the meta-verifier disagrees -> meta FAIL.
    res = eng.run(
        _candidate(risk=0.2),
        _sandbox(),
        simulate_fn=lambda c: "pass",
        meta_fn=lambda subject: "fail",
    )
    assert res.meta_verified is False
    assert res.gate is SimulationGate.REJECT  # fail-closed


def test_sandbox_isolation_blocks_non_isolated():
    eng = SimulationGateEngine()
    # A non-isolated sandbox must never run (fail-closed isolation).
    res = eng.run(_candidate(risk=0.2), Sandbox("sbx-x", isolation=False))
    assert res.observed_outcome == "inconclusive"
    assert res.gate is SimulationGate.REJECT


def test_deterministic_outcome():
    eng = SimulationGateEngine()
    r1 = eng.run(_candidate(risk=0.2), _sandbox(), simulate_fn=lambda c: "pass")
    r2 = eng.run(_candidate(risk=0.2), _sandbox(), simulate_fn=lambda c: "pass")
    assert eng.result_hash(r1) == eng.result_hash(r2)
    assert r1.observed_outcome == r2.observed_outcome
    assert r1.gate == r2.gate


def test_provenance_complete():
    eng = SimulationGateEngine()
    res = eng.run(_candidate(risk=0.2), _sandbox(), simulate_fn=lambda c: "pass")
    assert eng.provenance_complete(res) is True
    assert res.evidence_ref


def test_simulation_result_fields():
    eng = SimulationGateEngine()
    res = eng.run(_candidate(risk=0.2), _sandbox(), simulate_fn=lambda c: "pass")
    d = res.to_dict()
    assert d["candidate_id"] == "cand-1"
    assert d["sandbox_id"] == "sbx-1"
    assert d["observed_outcome"] == "pass"
    assert d["meta_verified"] is True
    assert d["gate"] == "pass"
    assert d["evidence_ref"]
