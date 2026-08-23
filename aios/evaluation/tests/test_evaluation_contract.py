from aios.evaluation.evaluation_contract import (
    ContractValidationReport,
    EvaluationContract,
    EvaluationContractValidator,
)
from aios.evaluation._common import EvaluationError


def test_contract_construction_immutable():
    c = EvaluationContract("C1", "coding", ("correctness",), (0.8,))
    assert c.contract_id == "C1"


def test_contract_validate_pass():
    v = EvaluationContractValidator()
    c = EvaluationContract("C1", "coding", ("correctness", "robustness"), (0.8, 0.7))
    rep = v.validate(c)
    assert isinstance(rep, ContractValidationReport)
    assert rep.status == "PASS"
    assert rep.dimension_count == 2


def test_contract_validate_unknown_when_no_dimensions():
    v = EvaluationContractValidator()
    c = EvaluationContract("C1", "coding", (), ())
    rep = v.validate(c)
    assert rep.status == "UNKNOWN"


def test_contract_rejects_threshold_out_of_range():
    v = EvaluationContractValidator()
    try:
        v.validate(EvaluationContract("C1", "coding", ("correctness",), (1.5,)))
        assert False, "expected EvaluationError"
    except EvaluationError:
        pass


def test_contract_rejects_length_mismatch():
    v = EvaluationContractValidator()
    try:
        v.validate(EvaluationContract("C1", "coding", ("a", "b"), (0.8,)))
        assert False, "expected EvaluationError"
    except EvaluationError:
        pass


def test_contract_rejects_non_contract():
    v = EvaluationContractValidator()
    try:
        v.validate("not-a-contract")
        assert False, "expected EvaluationError"
    except EvaluationError:
        pass


def test_contract_deterministic_report_id():
    v = EvaluationContractValidator()
    a = v.validate(EvaluationContract("C1", "coding", ("correctness",), (0.8,)))
    b = v.validate(EvaluationContract("C1", "coding", ("correctness",), (0.8,)))
    assert a.report_id == b.report_id
