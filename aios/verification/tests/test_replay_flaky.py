from aios.verification.replay_flaky import (
    FlakyReport,
    ReplayFlakyDetector,
    ReplayRun,
)
from aios.verification._common import VerificationError


def test_run_construction():
    r = ReplayRun("R1", outcomes=("pass", "pass"))
    assert r.run_id == "R1"


def test_detect_pass_when_stable():
    d = ReplayFlakyDetector()
    r = ReplayRun("R1", outcomes=("pass", "pass", "pass"))
    rep = d.detect(r)
    assert isinstance(rep, FlakyReport)
    assert rep.flaky is False
    assert rep.status == "PASS"


def test_detect_insufficient_when_flaky():
    d = ReplayFlakyDetector()
    r = ReplayRun("R1", outcomes=("pass", "fail", "pass"))
    rep = d.detect(r)
    assert rep.flaky is True
    assert rep.status == "INSUFFICIENT"


def test_detect_rejects_empty_run_id():
    d = ReplayFlakyDetector()
    try:
        d.detect(ReplayRun("", outcomes=("pass",)))
        assert False, "expected VerificationError"
    except VerificationError:
        pass


def test_detect_rejects_empty_outcomes():
    d = ReplayFlakyDetector()
    try:
        d.detect(ReplayRun("R1", outcomes=()))
        assert False, "expected VerificationError"
    except VerificationError:
        pass


def test_detect_rejects_non_run():
    d = ReplayFlakyDetector()
    try:
        d.detect("not-a-run")
        assert False, "expected VerificationError"
    except VerificationError:
        pass


def test_detect_deterministic_report_id():
    d = ReplayFlakyDetector()
    r = ReplayRun("R1", outcomes=("pass", "pass"))
    assert d.detect(r).report_id == d.detect(r).report_id
