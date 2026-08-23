"""Tests for failure classification (T147)."""

import pytest

from aios.coding_loop import ExecutionObservation, FailureClassifier, FailureTaxonomy
from aios.coding_loop._common import CodingLoopError


def _obs(trace):
    o = ExecutionObservation()
    return o.capture("exec1", "loop1", trace, evidence_ref="ev1")


def test_classify_clear_trace():
    c = FailureClassifier()
    fc = c.classify(_obs(("SyntaxError: bad token",)))
    assert fc.taxonomy_label == FailureTaxonomy.SYNTAX.value
    assert fc.confidence >= 0.5
    assert c.is_promotable(fc) is True


def test_classify_ambiguous_trace_unknown():
    c = FailureClassifier()
    fc = c.classify(_obs(("nothing relevant here",)))
    assert fc.taxonomy_label == FailureTaxonomy.UNKNOWN.value
    assert c.is_promotable(fc) is False  # not promoted (T078)


def test_deterministic_same_observation_same_class():
    c1 = FailureClassifier()
    c2 = FailureClassifier()
    a = c1.classify(_obs(("Timeout exceeded",)))
    b = c2.classify(_obs(("Timeout exceeded",)))
    assert a.taxonomy_label == b.taxonomy_label
    assert a.confidence == b.confidence


def test_classify_requires_provenance():
    c = FailureClassifier()
    # observation without provenance must be rejected by classify (T001 Rule 5)
    from aios.coding_loop.observation import Observation

    bad = Observation("o1", "loop1", "exec1", ("err",), evidence_ref="ev-tmp")
    object.__setattr__(bad, "evidence_ref", "")
    with pytest.raises(CodingLoopError):
        c.classify(bad)


def test_closed_taxonomy():
    c = FailureClassifier()
    fc = c.classify(_obs(("connection refused",)))
    assert fc.taxonomy_label in {t.value for t in FailureTaxonomy}


def test_duplicate_class_id_rejected():
    c = FailureClassifier()
    c.classify(_obs(("SyntaxError",)), class_id="fc1")
    with pytest.raises(CodingLoopError):
        c.classify(_obs(("RuntimeError",)), class_id="fc1")


def test_provenance_hash():
    c = FailureClassifier()
    fc = c.classify(_obs(("MemoryError",)))
    prov = c.provenance(fc.class_id)
    assert prov["content_hash"]
    assert prov["evidence_ref"]
