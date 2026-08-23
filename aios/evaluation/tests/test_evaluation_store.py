from aios.evaluation.evaluation_store import (
    EvaluationStore,
    StoredEvaluation,
    StoreReport,
)
from aios.evaluation._common import EvaluationError, _hash, redact_secret


def test_store_construction():
    s = EvaluationStore()
    assert isinstance(s, EvaluationStore)


def test_store_store_and_verify_clean():
    s = EvaluationStore()
    content = "result: pass"
    rec = StoredEvaluation("R1", "subj", content, _hash(redact_secret(content)))
    rep = s.store(rec)
    assert isinstance(rep, StoreReport)
    assert rep.stored == 1
    assert rep.tampered == ()


def test_store_rejects_tampered_content():
    s = EvaluationStore()
    rec = StoredEvaluation("R1", "subj", "result: pass", _hash("different"))
    try:
        s.store(rec)
        assert False, "expected EvaluationError"
    except EvaluationError:
        pass


def test_store_verify_detects_tamper():
    s = EvaluationStore()
    content = "result: pass"
    rec = StoredEvaluation("R1", "subj", content, _hash(redact_secret(content)))
    s.store(rec)
    # Simulate tamper by mutating content via new record with bad hash.
    bad = StoredEvaluation("R1", "subj", "result: FAIL", _hash(redact_secret(content)))
    s._records.append(bad)
    rep = s.verify_integrity()
    assert "R1" in rep.tampered


def test_store_rejects_empty_record_id():
    s = EvaluationStore()
    try:
        s.store(StoredEvaluation("", "subj", "x", _hash("x")))
        assert False, "expected EvaluationError"
    except EvaluationError:
        pass


def test_store_rejects_empty_content_hash():
    s = EvaluationStore()
    try:
        s.store(StoredEvaluation("R1", "subj", "x", ""))
        assert False, "expected EvaluationError"
    except EvaluationError:
        pass


def test_store_deterministic_report_id():
    s = EvaluationStore()
    content = "result: pass"
    a = s.store(StoredEvaluation("R1", "subj", content, _hash(redact_secret(content))))
    b = EvaluationStore().store(StoredEvaluation("R1", "subj", content, _hash(redact_secret(content))))
    assert a.report_id == b.report_id
