from aios.verification.contract import (
    Contract,
    ContractReport,
    ContractVerifier,
)
from aios.verification._common import VerificationError


def test_contract_construction():
    c = Contract("C1", preconditions=(True,), postconditions=(True,))
    assert c.contract_id == "C1"


def test_verify_pass_when_all_hold():
    v = ContractVerifier()
    c = Contract("C1", preconditions=(True, True), postconditions=(True,))
    rep = v.verify(c)
    assert isinstance(rep, ContractReport)
    assert rep.violations == ()
    assert rep.status == "PASS"


def test_verify_insufficient_on_violation():
    v = ContractVerifier()
    c = Contract("C1", preconditions=(True, False), postconditions=(True,))
    rep = v.verify(c)
    assert len(rep.violations) == 1
    assert rep.status == "INSUFFICIENT"


def test_verify_rejects_empty_contract_id():
    v = ContractVerifier()
    try:
        v.verify(Contract(""))
        assert False, "expected VerificationError"
    except VerificationError:
        pass


def test_verify_rejects_non_contract():
    v = ContractVerifier()
    try:
        v.verify("not-a-contract")
        assert False, "expected VerificationError"
    except VerificationError:
        pass


def test_verify_postcondition_violation_detected():
    v = ContractVerifier()
    c = Contract("C1", preconditions=(True,), postconditions=(False,))
    rep = v.verify(c)
    assert "postcondition[0] violated" in rep.violations


def test_verify_deterministic_report_id():
    v = ContractVerifier()
    c = Contract("C1", preconditions=(True,), postconditions=(True,))
    assert v.verify(c).report_id == v.verify(c).report_id
