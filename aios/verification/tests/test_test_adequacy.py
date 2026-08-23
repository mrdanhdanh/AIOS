from aios.verification.test_adequacy import (
    AdequacyReport,
    MutationSuite,
    TestAdequacyAnalyzer,
)
from aios.verification._common import VerificationError


def test_suite_construction_valid():
    s = MutationSuite("S1", mutants=10, killed=10)
    assert s.mutants == 10
    assert s.killed == 10


def test_analyze_pass_high_mutation_score():
    a = TestAdequacyAnalyzer()
    s = MutationSuite("S1", mutants=10, killed=9)
    rep = a.analyze(s)
    assert isinstance(rep, AdequacyReport)
    assert rep.mutation_score == 0.9
    assert rep.status == "PASS"


def test_analyze_insufficient_low_score():
    a = TestAdequacyAnalyzer()
    s = MutationSuite("S1", mutants=10, killed=2)
    rep = a.analyze(s)
    assert rep.mutation_score == 0.2
    assert rep.status == "INSUFFICIENT"


def test_analyze_unknown_when_no_mutants():
    a = TestAdequacyAnalyzer()
    s = MutationSuite("S1", mutants=0, killed=0)
    rep = a.analyze(s)
    assert rep.status == "UNKNOWN"


def test_analyze_rejects_empty_suite_id():
    a = TestAdequacyAnalyzer()
    try:
        a.analyze(MutationSuite("", mutants=1, killed=1))
        assert False, "expected VerificationError"
    except VerificationError:
        pass


def test_analyze_rejects_killed_gt_mutants():
    a = TestAdequacyAnalyzer()
    try:
        a.analyze(MutationSuite("S1", mutants=1, killed=2))
        assert False, "expected VerificationError"
    except VerificationError:
        pass


def test_analyze_deterministic_report_id():
    a = TestAdequacyAnalyzer()
    s = MutationSuite("S1", mutants=10, killed=5)
    assert a.analyze(s).report_id == a.analyze(s).report_id
