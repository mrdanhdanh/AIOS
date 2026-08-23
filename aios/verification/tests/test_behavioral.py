from aios.verification.behavioral import (
    BehaviorReport,
    BehaviorSpec,
    BehavioralVerifier,
)
from aios.verification._common import VerificationError


def test_spec_construction():
    s = BehaviorSpec("B1", expected=1, actual=1)
    assert s.spec_id == "B1"


def test_verify_pass_on_match():
    v = BehavioralVerifier()
    rep = v.verify(BehaviorSpec("B1", expected={"a": 1}, actual={"a": 1}))
    assert isinstance(rep, BehaviorReport)
    assert rep.match is True
    assert rep.status == "PASS"


def test_verify_insufficient_on_mismatch():
    v = BehavioralVerifier()
    rep = v.verify(BehaviorSpec("B1", expected=1, actual=2))
    assert rep.match is False
    assert rep.status == "INSUFFICIENT"


def test_verify_rejects_empty_spec_id():
    v = BehavioralVerifier()
    try:
        v.verify(BehaviorSpec("", expected=1, actual=1))
        assert False, "expected VerificationError"
    except VerificationError:
        pass


def test_verify_rejects_non_spec():
    v = BehavioralVerifier()
    try:
        v.verify("not-a-spec")
        assert False, "expected VerificationError"
    except VerificationError:
        pass


def test_verify_handles_none_actual():
    v = BehavioralVerifier()
    rep = v.verify(BehaviorSpec("B1", expected=None, actual=None))
    assert rep.match is True
    assert rep.status == "PASS"


def test_verify_deterministic_report_id():
    v = BehavioralVerifier()
    s = BehaviorSpec("B1", expected=1, actual=1)
    assert v.verify(s).report_id == v.verify(s).report_id
