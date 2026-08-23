from aios.quality_gate.ledger import (
    GovernanceLedger,
    LedgerEntry,
    ProvenanceEdge,
    ProvenanceGraph,
)
from aios.quality_gate._common import QualityGateError


def test_ledger_record_immutable():
    l = GovernanceLedger()
    e = l.record("subj", "action")
    assert isinstance(e, LedgerEntry)
    assert e.entry_id
    assert e.entry_hash


def test_ledger_verify_clean():
    l = GovernanceLedger()
    e = l.record("subj", "action")
    rep = l.verify([e])
    assert rep.tampered == ()


def test_ledger_detects_tamper():
    l = GovernanceLedger()
    e = l.record("subj", "action")
    bad = LedgerEntry(e.entry_id, e.subject, e.action, e.prev_hash, "tampered-hash")
    rep = l.verify([bad])
    assert e.entry_id in rep.tampered


def test_provenance_graph_builds_edges():
    l = GovernanceLedger()
    e = l.record("subj", "action")
    g = ProvenanceGraph()
    edges = g.build([e])
    assert isinstance(edges[0], ProvenanceEdge)
    assert edges[0].source == "subj"
    assert edges[0].target == "action"


def test_ledger_rejects_empty_subject():
    l = GovernanceLedger()
    try:
        l.record("", "action")
        assert False, "expected QualityGateError"
    except QualityGateError:
        pass


def test_ledger_verify_rejects_non_entry():
    l = GovernanceLedger()
    try:
        l.verify(["not-an-entry"])
        assert False, "expected QualityGateError"
    except QualityGateError:
        pass


def test_ledger_deterministic_entry_id():
    l = GovernanceLedger()
    a = l.record("subj", "action")
    b = l.record("subj", "action")
    assert a.entry_id == b.entry_id
