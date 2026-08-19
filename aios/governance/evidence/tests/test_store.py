import sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from aios.governance.evidence import Evidence, EvidenceStore


def _ev():
    return Evidence(
        evidence_id="EVD-000421", task_id="TASK-125", run_id="RUN-0092",
        producer="coder-harness", type="test-result", source="pytest",
        content_hash="sha256:abc123", status="PASS",
        parent_artifact="art-1", environment="win",
    )


def test_provenance_chain():
    store = EvidenceStore()
    store.add(_ev())
    chain = store.provenance_chain("EVD-000421")
    assert chain["evidence"] == "EVD-000421"
    assert chain["run"] == "RUN-0092"
    assert chain["artifact"] == "art-1"
    assert chain["task"] == "TASK-125"
    assert chain["requirement"] == "pytest"
    assert chain["status"] == "PASS"


def test_verify_full_chain():
    store = EvidenceStore()
    store.add(_ev())
    assert store.verify("EVD-000421") is True


def test_unknown_evidence_fails():
    store = EvidenceStore()
    assert store.verify("MISSING") is False
