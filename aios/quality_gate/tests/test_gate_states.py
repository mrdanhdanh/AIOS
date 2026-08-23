from aios.quality_gate.gate_states import GateCheck, GateReport, QualityGate
from aios.quality_gate._common import QualityGateError


def test_gate_construction_immutable():
    g = QualityGate("G1")
    assert g.gate_id == "G1"


def test_gate_pass_with_all_pass_checks():
    g = QualityGate("G1")
    rep = g.evaluate([GateCheck("C1", "unit", "PASS"), GateCheck("C2", "lint", "PASS")])
    assert isinstance(rep, GateReport)
    assert rep.state == "PASS"
    assert rep.blocking == ()


def test_gate_fail_on_failing_check():
    g = QualityGate("G1")
    rep = g.evaluate([GateCheck("C1", "unit", "PASS"), GateCheck("C2", "lint", "FAIL")])
    assert rep.state == "FAIL"
    assert "C2" in rep.blocking


def test_gate_unknown_blocks_promotion():
    g = QualityGate("G1")
    rep = g.evaluate([GateCheck("C1", "unit", "PASS"), GateCheck("C2", "lint", "UNKNOWN")])
    assert rep.state == "UNKNOWN"
    assert "C2" in rep.blocking


def test_gate_unknown_never_promoted_to_pass():
    g = QualityGate("G1")
    rep = g.evaluate([GateCheck("C1", "unit", "UNKNOWN")])
    assert rep.state != "PASS"


def test_gate_rejects_empty_checks_list_as_unknown():
    g = QualityGate("G1")
    rep = g.evaluate([])
    assert rep.state == "UNKNOWN"


def test_gate_rejects_non_check_and_deterministic_id():
    g = QualityGate("G1")
    try:
        g.evaluate(["not-a-check"])
        assert False, "expected QualityGateError"
    except QualityGateError:
        pass
    a = g.evaluate([GateCheck("C1", "unit", "PASS")])
    b = g.evaluate([GateCheck("C1", "unit", "PASS")])
    assert a.report_id == b.report_id
