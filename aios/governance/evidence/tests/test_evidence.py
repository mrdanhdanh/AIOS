"""Automated tests for the Evidence Store gate (Rule 5)."""

import pytest

from aios.governance.evidence import (
    Artifact,
    EvidenceError,
    EvidenceStore,
    Requirement,
    Run,
    TaskRecord,
)


def _seed(store: EvidenceStore) -> str:
    store.add_requirement(Requirement("REQ-001", "Task governance exists"))
    store.add_task_record(TaskRecord("TASK-001", "REQ-001"))
    store.add_artifact(Artifact("ART-001", "TASK-001", "REQ-001", kind="test"))
    store.add_run(Run("RUN-001", "ART-001", "TASK-001", command="pytest"))
    ev = store.add_evidence(
        evidence_id="EVID-001",
        task_id="TASK-001",
        run_id="RUN-001",
        producer="pytest",
        type="test-pass",
        source="tests/test_registry.py",
        content="PASS",
        parent_artifact="ART-001",
        environment="win/python3.13",
    )
    return ev.evidence_id


def test_evidence_requires_mandatory_fields():
    store = EvidenceStore()
    with pytest.raises(EvidenceError):
        store.add_evidence(
            evidence_id="",
            task_id="TASK-001",
            run_id="RUN-001",
            producer="pytest",
            type="test",
            source="x",
        )


def test_provenance_chain_is_complete_when_seeded():
    """Rule 5: each PASS must be traceable to a full provenance chain."""
    store = EvidenceStore()
    eid = _seed(store)
    chain = store.get_provenance_chain(eid)
    assert chain.complete is True
    assert chain.evidence.evidence_id == "EVID-001"
    assert chain.run.run_id == "RUN-001"
    assert chain.artifact.artifact_id == "ART-001"
    assert chain.task.task_id == "TASK-001"
    assert chain.requirement.requirement_id == "REQ-001"


def test_incomplete_chain_is_not_admissible():
    store = EvidenceStore()
    # Evidence referencing a run that does not exist -> incomplete.
    ev = store.add_evidence(
        evidence_id="EVID-X",
        task_id="TASK-001",
        run_id="RUN-MISSING",
        producer="pytest",
        type="test",
        source="x",
        content="PASS",
    )
    assert store.is_admissible(ev.evidence_id) is False
    chain = store.get_provenance_chain(ev.evidence_id)
    assert chain.complete is False


# --- TASK-234 Automatic Evidence Generation --------------------------------
def test_evidence_freshness_and_stale():
    store = EvidenceStore()
    past = "2020-01-01T00:00:00+00:00"
    future = "2099-01-01T00:00:00+00:00"
    store.add_requirement(Requirement("REQ-F", "freshness req"))
    store.add_task_record(TaskRecord("T-F", "REQ-F"))
    store.add_artifact(Artifact("A-F", "T-F", "REQ-F"))
    store.add_run(Run("R-F", "A-F", "T-F"))
    ev_stale = store.add_evidence(
        evidence_id="E-STALE", task_id="T-F", run_id="R-F", producer="p",
        type="t", source="s", content="x", requirement_id="REQ-F", freshness=past,
    )
    ev_fresh = store.add_evidence(
        evidence_id="E-FRESH", task_id="T-F", run_id="R-F", producer="p",
        type="t", source="s", content="x", requirement_id="REQ-F", freshness=future,
    )
    assert ev_stale.is_stale() is True
    assert ev_fresh.is_stale() is False


def test_coverage_map_tracks_requirement():
    store = EvidenceStore()
    store.add_requirement(Requirement("REQ-C", "coverage req"))
    store.add_task_record(TaskRecord("T-C", "REQ-C"))
    store.add_artifact(Artifact("A-C", "T-C", "REQ-C"))
    store.add_run(Run("R-C", "A-C", "T-C"))
    store.add_evidence(
        evidence_id="E-C", task_id="T-C", run_id="R-C", producer="p",
        type="t", source="s", content="x", requirement_id="REQ-C",
        freshness="2099-01-01T00:00:00+00:00",
    )
    assert "REQ-C" in store.coverage_map
    assert store.is_requirement_covered("REQ-C") is True
    assert store.is_requirement_covered("REQ-UNKNOWN") is False


# --- TASK-235 Evidence Quality & Integrity ----------------------------------
def _seed_two_runs(store, req, run_a, run_b):
    store.add_requirement(Requirement(req, "q"))
    store.add_task_record(TaskRecord("T", req))
    store.add_artifact(Artifact("A", "T", req))
    store.add_run(Run(run_a, "A", "T"))
    store.add_run(Run(run_b, "A", "T"))


def test_detect_conflicts_finds_disagreement():
    store = EvidenceStore()
    _seed_two_runs(store, "REQ-Q", "RA", "RB")
    store.add_evidence("EA", "T", "RA", "p", "t", "s", "x", requirement_id="REQ-Q", status="PASS")
    store.add_evidence("EB", "T", "RB", "p", "t", "s", "x", requirement_id="REQ-Q", status="FAIL")
    conflicts = store.detect_conflicts()
    assert ("EA", "EB") in conflicts or ("EB", "EA") in conflicts


def test_replay_reconstructs_from_run():
    store = EvidenceStore()
    _seed_two_runs(store, "REQ-R", "RR", "RB2")
    store.add_evidence("ER1", "T", "RR", "p", "t", "s", "x", requirement_id="REQ-R")
    store.add_evidence("ER2", "T", "RR", "p", "t", "s", "x", requirement_id="REQ-R")
    replayed = store.replay("RR")
    assert {e.evidence_id for e in replayed} == {"ER1", "ER2"}


def test_quality_score_and_validity():
    store = EvidenceStore()
    _seed_two_runs(store, "REQ-S", "RS", "RB3")
    store.add_evidence("ES", "T", "RS", "p", "t", "s", "x", requirement_id="REQ-S",
                       status="PASS", freshness="2099-01-01T00:00:00+00:00")
    score = store.quality_score("ES", {"p": 1.0})
    assert score == 1.0
    assert store.is_valid_for_evaluation("ES") is True
    # STALE evidence is invalid for evaluation.
    store.add_evidence("ES2", "T", "RB3", "p", "t", "s", "x", requirement_id="REQ-S",
                       status="PASS", freshness="2020-01-01T00:00:00+00:00")
    assert store.is_valid_for_evaluation("ES2") is False
