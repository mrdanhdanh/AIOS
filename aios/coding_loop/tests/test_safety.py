"""Tests for the autonomous safety controller (T153)."""

import pytest

from aios.coding_loop import (
    AutonomousSafetyController,
    ContextRefreshPatchChain,
    ProgressRegressionDetector,
    VerifyStatus,
    VerificationGate,
)
from aios.coding_loop._common import CodingLoopError


def _chain():
    d = ProgressRegressionDetector(baseline=0.5)
    prog = d.detect("loop1", "plan1", 0.8, evidence_ref="ev1")
    vr = VerificationGate().verify(prog, "abc", evidence_ref="ev1")
    return ContextRefreshPatchChain().refresh_and_chain(vr, "ctx-0", "snap-0", "snap-0")


def test_within_boundary_continue():
    s = AutonomousSafetyController()
    dec = s.evaluate(_chain(), boundary_status="within")
    assert dec.kill_switch is False
    assert dec.boundary_status == "within"


def test_boundary_violation_kill_switch():
    s = AutonomousSafetyController()
    dec = s.evaluate(_chain(), boundary_status="escaped")  # fail-closed (T068)
    assert dec.kill_switch is True


def test_deterministic_same_state_same_decision():
    s1 = AutonomousSafetyController()
    s2 = AutonomousSafetyController()
    a = s1.evaluate(_chain(), boundary_status="within")
    b = s2.evaluate(_chain(), boundary_status="within")
    assert a.kill_switch == b.kill_switch


def test_evaluate_requires_provenance():
    s = AutonomousSafetyController()
    from aios.coding_loop.patch_chain import PatchChain

    bad = PatchChain("c1", "v1", "ctx-0", ("p1",), "snap-0", evidence_ref="ev-tmp")
    object.__setattr__(bad, "evidence_ref", "")
    with pytest.raises(CodingLoopError):
        s.evaluate(bad)


def test_duplicate_decision_id_rejected():
    s = AutonomousSafetyController()
    s.evaluate(_chain(), boundary_status="within", decision_id="safe1")
    with pytest.raises(CodingLoopError):
        s.evaluate(_chain(), boundary_status="within", decision_id="safe1")


def test_guardrail_applied():
    s = AutonomousSafetyController(guardrail_ref="gr-custom")
    dec = s.evaluate(_chain(), boundary_status="within")
    assert dec.guardrail_ref == "gr-custom"


def test_provenance_hash():
    s = AutonomousSafetyController()
    dec = s.evaluate(_chain(), boundary_status="within")
    prov = s.provenance(dec.decision_id)
    assert prov["content_hash"]
    assert prov["kill_switch"] is False
