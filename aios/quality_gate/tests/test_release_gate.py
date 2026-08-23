from aios.quality_gate.release_gate import (
    ReleaseCriterion,
    ReleaseGate,
    ReleaseReport,
)
from aios.quality_gate._common import QualityGateError


def test_release_construction_immutable():
    c = ReleaseCriterion("C1", "tests", True)
    assert c.criterion_id == "C1"


def test_release_when_all_blocking_met():
    g = ReleaseGate()
    rep = g.evaluate([ReleaseCriterion("C1", "tests", True), ReleaseCriterion("C2", "coverage", True)])
    assert isinstance(rep, ReleaseReport)
    assert rep.decision == "RELEASE"
    assert "all blocking criteria met" in rep.explanation


def test_release_no_release_when_blocking_unmet():
    g = ReleaseGate()
    rep = g.evaluate([ReleaseCriterion("C1", "tests", True), ReleaseCriterion("C2", "coverage", False)])
    assert rep.decision == "NO_RELEASE"
    assert "coverage" in rep.explanation
    assert "C2" in rep.unmet[0].criterion_id


def test_release_non_blocking_unmet_still_releases():
    g = ReleaseGate()
    rep = g.evaluate([ReleaseCriterion("C1", "tests", True), ReleaseCriterion("C2", "docs", False, blocking=False)])
    assert rep.decision == "RELEASE"


def test_release_blocked_with_no_criteria():
    g = ReleaseGate()
    rep = g.evaluate([])
    assert rep.decision == "BLOCKED"


def test_release_rejects_non_criterion():
    g = ReleaseGate()
    try:
        g.evaluate(["not-a-criterion"])
        assert False, "expected QualityGateError"
    except QualityGateError:
        pass


def test_release_deterministic_report_id():
    g = ReleaseGate()
    a = g.evaluate([ReleaseCriterion("C1", "tests", True)])
    b = g.evaluate([ReleaseCriterion("C1", "tests", True)])
    assert a.report_id == b.report_id
