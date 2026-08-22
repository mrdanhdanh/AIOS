"""Tests for TASK-094 — Remediation Detect + Diagnose (M14)."""

from __future__ import annotations

from aios.remediation_detect.detect import (
    DetectDiagnoseEngine,
    Diagnosis,
    Incident,
    Symptom,
    SymptomSeverity,
)


def _engine() -> DetectDiagnoseEngine:
    return DetectDiagnoseEngine()


def test_detect_anomaly_oscillation():
    eng = _engine()
    # Repeated state hash within the window -> oscillation detected.
    eng.observe(1, 0.5, 1.0, "h1", evidence_ref="ev-1")
    eng.observe(2, 0.5, 1.0, "h1", evidence_ref="ev-2")
    inc = eng.detect()
    assert inc is not None
    assert inc.kind == "oscillation"
    assert inc.evidence_ref


def test_detect_no_anomaly():
    eng = _engine()
    # Monotonic progress, distinct hashes -> no stuck signal.
    eng.observe(1, 0.1, 1.0, "a", evidence_ref="ev-1")
    eng.observe(2, 0.5, 1.0, "b", evidence_ref="ev-2")
    eng.observe(3, 0.9, 1.0, "c", evidence_ref="ev-3")
    assert eng.detect() is None


def test_capture_symptom_with_evidence():
    eng = _engine()
    sym = eng.capture_symptom("s1", "latency spike", "ev-lat", SymptomSeverity.HIGH)
    assert isinstance(sym, Symptom)
    assert sym.evidence_ref == "ev-lat"
    assert sym.severity is SymptomSeverity.HIGH


def test_root_cause_traceable():
    eng = _engine()
    inc = Incident("inc-1", "anomaly", "major", {"k": "v"}, evidence_ref="ev-inc")
    syms = [eng.capture_symptom("s1", "sym1", "ev-1")]
    trace = ["probe timeout", "downstream dependency down"]
    diag = eng.diagnose(inc, syms, trace)
    assert diag.escalated is False
    assert diag.is_traceable()
    assert diag.root_cause == "downstream dependency down"
    assert diag.causal_trace == trace
    assert 0.0 < diag.confidence <= 1.0


def test_missing_evidence_escalates():
    eng = _engine()
    inc = Incident("inc-1", "anomaly", "major", {}, evidence_ref="ev-inc")
    # Symptom without evidence -> fail-closed escalate, never conclude.
    syms = [Symptom("s1", "sym without evidence")]
    diag = eng.diagnose(inc, syms, ["cause a", "cause b"])
    assert diag.escalated is True
    assert diag.root_cause == ""
    assert diag.confidence == 0.0


def test_missing_causal_trace_escalates():
    eng = _engine()
    inc = Incident("inc-1", "anomaly", "major", {}, evidence_ref="ev-inc")
    syms = [eng.capture_symptom("s1", "sym1", "ev-1")]
    # No causal trace -> cannot conclude root cause -> escalate.
    diag = eng.diagnose(inc, syms, [])
    assert diag.escalated is True
    assert diag.is_traceable() is False


def test_deterministic_diagnosis():
    eng = _engine()
    inc = Incident("inc-1", "anomaly", "major", {"k": "v"}, evidence_ref="ev-inc")
    syms = [eng.capture_symptom("s1", "sym1", "ev-1")]
    trace = ["cause a", "cause b"]
    d1 = eng.diagnose(inc, syms, trace)
    d2 = eng.diagnose(inc, syms, trace)
    assert eng.result_hash(d1) == eng.result_hash(d2)
    assert d1.root_cause == d2.root_cause
    assert d1.confidence == d2.confidence


def test_provenance_complete():
    eng = _engine()
    inc = Incident("inc-1", "anomaly", "major", {}, evidence_ref="ev-inc")
    syms = [eng.capture_symptom("s1", "sym1", "ev-1")]
    diag = eng.diagnose(inc, syms, ["cause a"])
    assert eng.provenance_complete(diag) is True
    assert diag.evidence_ref


def test_diagnosis_report_provenance():
    eng = _engine()
    inc = eng.detect() or Incident("inc-1", "anomaly", "major", {}, evidence_ref="ev-inc")
    syms = [eng.capture_symptom("s1", "sym1", "ev-1")]
    diag = eng.diagnose(inc, syms, ["cause a", "cause b"])
    report = diag.to_dict()
    assert report["traceable"] is True
    assert report["evidence_ref"]
    assert eng.provenance_complete(diag) is True
