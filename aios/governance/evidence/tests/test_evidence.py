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
