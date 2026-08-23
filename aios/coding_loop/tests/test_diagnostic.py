"""Tests for the diagnostic agent (T148)."""

import pytest

from aios.coding_loop import DiagnosticAgent, ExecutionObservation, FailureClassifier
from aios.coding_loop._common import CodingLoopError


def _class(trace):
    o = ExecutionObservation()
    obs = o.capture("exec1", "loop1", trace, evidence_ref="ev1")
    return FailureClassifier().classify(obs)


def test_diagnose_clear_input():
    d = DiagnosticAgent()
    fc = _class(("SyntaxError: bad token",))
    rep = d.diagnose(fc)
    assert rep.root_cause != "UNKNOWN"
    assert d.is_promotable(rep) is True


def test_diagnose_unknown_not_promoted():
    d = DiagnosticAgent()
    fc = _class(("nothing relevant",))
    rep = d.diagnose(fc)
    assert rep.root_cause == "UNKNOWN"
    assert d.is_promotable(rep) is False  # not promoted (T078)


def test_deterministic_same_input_same_root_cause():
    d1 = DiagnosticAgent()
    d2 = DiagnosticAgent()
    fc1 = _class(("Timeout exceeded",))
    fc2 = _class(("Timeout exceeded",))
    assert d1.diagnose(fc1).root_cause == d2.diagnose(fc2).root_cause


def test_diagnose_requires_provenance():
    d = DiagnosticAgent()
    fc = _class(("err",))
    # strip evidence by constructing a class without evidence_ref
    from aios.coding_loop.classification import FailureClass

    bad = FailureClass("fc1", "obs1", "RUNTIME", 0.7, evidence_ref="ev-tmp")
    object.__setattr__(bad, "evidence_ref", "")
    with pytest.raises(CodingLoopError):
        d.diagnose(bad)


def test_duplicate_report_id_rejected():
    d = DiagnosticAgent()
    fc = _class(("RuntimeError",))
    d.diagnose(fc, report_id="diag1")
    with pytest.raises(CodingLoopError):
        d.diagnose(fc, report_id="diag1")


def test_root_cause_mapping():
    d = DiagnosticAgent()
    fc = _class(("Network unreachable",))
    rep = d.diagnose(fc)
    assert "unreachable" in rep.root_cause.lower()


def test_provenance_hash():
    d = DiagnosticAgent()
    fc = _class(("AssertionError: expected",))
    rep = d.diagnose(fc)
    prov = d.provenance(rep.report_id)
    assert prov["content_hash"]
    assert prov["authority"] == "aios"
