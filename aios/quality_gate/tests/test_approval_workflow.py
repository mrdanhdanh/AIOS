from aios.quality_gate.approval_workflow import (
    ApprovalReport,
    ApprovalRequest,
    ApprovalWorkflow,
)
from aios.quality_gate._common import QualityGateError


def test_approval_construction_immutable():
    r = ApprovalRequest("R1", "CHG", "LOW")
    assert r.request_id == "R1"


def test_approval_low_risk_approved():
    w = ApprovalWorkflow()
    rep = w.submit(ApprovalRequest("R1", "CHG", "LOW", approvers=("u1",)))
    assert isinstance(rep, ApprovalReport)
    assert rep.state == "APPROVED"
    assert rep.rollback == "NO_RECOMMEND"


def test_approval_high_risk_needs_two_approvers():
    w = ApprovalWorkflow()
    rep = w.submit(ApprovalRequest("R1", "CHG", "HIGH", approvers=("u1",)))
    assert rep.state == "REJECTED"
    assert rep.rollback == "BLOCKED"


def test_approval_high_risk_recommend_rollback():
    w = ApprovalWorkflow()
    rep = w.submit(ApprovalRequest("R1", "CHG", "CRITICAL", approvers=("u1", "u2")))
    assert rep.state == "APPROVED"
    assert rep.rollback == "RECOMMEND"


def test_approval_rejects_invalid_risk():
    w = ApprovalWorkflow()
    try:
        w.submit(ApprovalRequest("R1", "CHG", "NOPE"))
        assert False, "expected QualityGateError"
    except QualityGateError:
        pass


def test_approval_rejects_non_request():
    w = ApprovalWorkflow()
    try:
        w.submit("not-a-request")
        assert False, "expected QualityGateError"
    except QualityGateError:
        pass


def test_approval_deterministic_report_id():
    w = ApprovalWorkflow()
    a = w.submit(ApprovalRequest("R1", "CHG", "LOW", approvers=("u1",)))
    b = w.submit(ApprovalRequest("R1", "CHG", "LOW", approvers=("u1",)))
    assert a.report_id == b.report_id
