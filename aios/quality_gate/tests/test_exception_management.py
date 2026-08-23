from aios.quality_gate.exception_management import (
    ExceptionManager,
    ExceptionReport,
    ExceptionRequest,
)
from aios.quality_gate._common import QualityGateError


def test_exception_construction_immutable():
    r = ExceptionRequest("E1", "POL", "justified")
    assert r.exception_id == "E1"


def test_exception_approved_when_justified():
    m = ExceptionManager()
    rep = m.request(ExceptionRequest("E1", "POL", "needs waiver"))
    assert isinstance(rep, ExceptionReport)
    assert rep.state == "APPROVED"


def test_exception_rejected_without_justification():
    m = ExceptionManager()
    rep = m.request(ExceptionRequest("E1", "POL", ""))
    assert rep.state == "REJECTED"
    assert rep.reason == "missing justification"


def test_exception_rejected_with_whitespace_justification():
    m = ExceptionManager()
    rep = m.request(ExceptionRequest("E1", "POL", "   "))
    assert rep.state == "REJECTED"


def test_exception_keeps_provided_state_when_not_pending():
    m = ExceptionManager()
    rep = m.request(ExceptionRequest("E1", "POL", "j", state="REJECTED"))
    assert rep.state == "REJECTED"


def test_exception_rejects_non_request():
    m = ExceptionManager()
    try:
        m.request("not-a-request")
        assert False, "expected QualityGateError"
    except QualityGateError:
        pass


def test_exception_deterministic_report_id():
    m = ExceptionManager()
    a = m.request(ExceptionRequest("E1", "POL", "j"))
    b = m.request(ExceptionRequest("E1", "POL", "j"))
    assert a.report_id == b.report_id
