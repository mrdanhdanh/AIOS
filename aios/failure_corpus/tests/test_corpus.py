"""Tests for the Failure-Corpus Improvement Engine (TASK-100)."""

from aios.autonomous_harness_loop.loop import HarnessLoopRun
from aios.failure_corpus.corpus import FailureCorpusEngine, FailureSource
from aios.harness_coverage.coverage import CoverageMap
from aios.remediation_detect.detect import Diagnosis, Incident, Symptom, SymptomSeverity


def _diagnosis(incident_id="inc-1", symptom="timeout", root_cause="slow-db"):
    incident = Incident(incident_id=incident_id, kind="failure", severity="high", evidence_ref="ev-1")
    sym = Symptom("s1", symptom, evidence_ref="ev-1", severity=SymptomSeverity.HIGH)
    return Diagnosis(
        incident_id=incident_id,
        symptoms=[sym],
        root_cause=root_cause,
        confidence=0.9,
        causal_trace=["trace:1"],
        evidence_ref="ev-1",
    )


def test_failure_collected_from_t094():
    eng = FailureCorpusEngine()
    entry = eng.collect_from_diagnosis(_diagnosis())
    assert entry.source == FailureSource.T094.value
    assert entry in eng._corpus.entries()


def test_corpus_dedupe_no_duplicate():
    eng = FailureCorpusEngine()
    e1 = eng.collect_from_diagnosis(_diagnosis())
    e2 = eng.collect_from_diagnosis(_diagnosis())  # identical -> dedupe
    assert e1.failure_id == e2.failure_id
    assert len(eng._corpus.entries()) == 1


def test_gap_uncovered_reported():
    # Coverage map harnesses nothing -> failure is a gap (T090).
    eng = FailureCorpusEngine(coverage_map=CoverageMap())
    eng.collect_from_diagnosis(_diagnosis(incident_id="inc-gap"))
    gaps = eng.gaps()
    assert len(gaps) == 1
    assert gaps[0].covered_by_harness is False


def test_improvement_proposed():
    eng = FailureCorpusEngine(coverage_map=CoverageMap())
    eng.collect_from_diagnosis(_diagnosis(incident_id="inc-imp"))
    improvements = eng.propose_improvements()
    assert any("harness" in i for i in improvements)
    assert any("detection" in i for i in improvements)
    assert any("remediation" in i for i in improvements)


def test_deterministic_analysis():
    eng = FailureCorpusEngine(coverage_map=CoverageMap())
    eng.collect_from_diagnosis(_diagnosis(incident_id="inc-det"))
    h1 = eng.analysis_hash()
    # Rebuild an identical corpus and compare.
    eng2 = FailureCorpusEngine(coverage_map=CoverageMap())
    eng2.collect_from_diagnosis(_diagnosis(incident_id="inc-det"))
    assert h1 == eng2.analysis_hash()


def test_corpus_entry_evidence_provenance():
    eng = FailureCorpusEngine()
    entry = eng.collect_from_diagnosis(_diagnosis())
    assert eng.provenance_complete(entry) is True
    assert entry.evidence_ref
