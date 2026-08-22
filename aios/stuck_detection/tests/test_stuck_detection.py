"""Tests for TASK-061 Advanced Stuck Detection."""
from __future__ import annotations

from aios.stuck_detection.contracts import StuckKind, StuckSeverity
from aios.stuck_detection.detector import IterationSample, StuckDetector, StuckGate


def _sample(it, progress, cost=0.0, state=None, ev="ev:1"):
    if state is None:
        state = f"state-{it}"
    return IterationSample(iteration=it, progress=progress, cost=cost,
                           state_hash=hashlib_state(state), evidence_ref=ev)


def hashlib_state(s):
    import hashlib
    return hashlib.sha256(s.encode()).hexdigest()[:12]


def test_every_iteration_monitored():
    d = StuckDetector()
    d.observe(_sample(1, 0.0))
    d.observe(_sample(2, 0.0))
    assert len(d.history) == 2


def test_oscillation_detected_from_trajectory_hash():
    d = StuckDetector(oscillation_window=3)
    d.observe(_sample(1, 0.5, state="A"))
    d.observe(_sample(2, 0.5, state="B"))
    d.observe(_sample(3, 0.5, state="A"))  # repeats A -> oscillation
    sig = d.detect()
    assert sig is not None
    assert sig.kind == StuckKind.OSCILLATION


def test_plateau_detected():
    d = StuckDetector(plateau_threshold=0.01, plateau_window=3)
    for i in range(1, 5):
        d.observe(_sample(i, 0.4 + i * 0.001))  # tiny deltas
    sig = d.detect()
    assert sig is not None
    assert sig.kind == StuckKind.PLATEAU


def test_resource_burn_detected():
    d = StuckDetector(resource_burn_window=3, plateau_threshold=0.01)
    d.observe(_sample(1, 0.5, cost=0.1))
    d.observe(_sample(2, 0.5, cost=0.3))
    d.observe(_sample(3, 0.5, cost=0.6))  # cost up, progress flat
    sig = d.detect()
    assert sig is not None
    assert sig.kind == StuckKind.RESOURCE_BURN


def test_low_confidence_escalates_fail_closed():
    from aios.stuck_detection.contracts import StuckSignal, StuckPolicy
    pol = StuckPolicy()
    sig = StuckSignal(kind=StuckKind.PLATEAU, confidence=0.2, evidence_ref="ev:1")
    assert pol.resolve(sig) == "escalate"


def test_missing_evidence_escalates():
    from aios.stuck_detection.contracts import StuckSignal, StuckPolicy
    pol = StuckPolicy()
    sig = StuckSignal(kind=StuckKind.OSCILLATION, confidence=0.9, evidence_ref="")
    assert pol.resolve(sig) == "escalate"


def test_high_confidence_oscillation_safe_stop():
    from aios.stuck_detection.contracts import StuckSignal, StuckPolicy
    pol = StuckPolicy()
    sig = StuckSignal(kind=StuckKind.OSCILLATION, confidence=0.9, evidence_ref="ev:1")
    assert pol.resolve(sig) == "safe_stop"


def test_stuck_gate_blocks_on_budget():
    g = StuckGate()
    final, reason = g.gate("safe_stop", {"budget_exceeded": True})
    assert final == "BLOCK"


def test_stuck_gate_governor_allow():
    def gov(action, ctx):
        return "ALLOW"
    g = StuckGate(governor_decision=gov)
    final, reason = g.gate("recover", {})
    assert final == "recover"
    assert reason == "allowed"


def test_detect_returns_none_when_progressing():
    d = StuckDetector()
    d.observe(_sample(1, 0.1))
    d.observe(_sample(2, 0.5))
    d.observe(_sample(3, 0.9))
    assert d.detect() is None


def test_deterministic_same_trajectory_same_verdict():
    def build():
        det = StuckDetector(oscillation_window=3)
        det.observe(_sample(1, 0.5, state="A"))
        det.observe(_sample(2, 0.5, state="B"))
        det.observe(_sample(3, 0.5, state="A"))
        return det.detect()
    r1 = build()
    r2 = build()
    assert r1.kind == r2.kind == StuckKind.OSCILLATION
