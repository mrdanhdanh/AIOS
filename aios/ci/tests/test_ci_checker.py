"""Tests for the local CI/CD checker (offline; uses a fake runner)."""
from __future__ import annotations

import pytest

from aios.ci.checker import (
    CIChecker,
    CIReport,
    CIStatus,
    CheckResult,
    run_ci_check,
)


# -- fixtures / helpers ---------------------------------------------------

def _fake_runner(passed: int, failed: int, exit_code: int = 0):
    """Return a runner that fakes a pytest summary for any command."""

    def _run(cmd, timeout):
        summary = f"{passed} passed"
        if failed:
            summary = f"{failed} failed, {passed} passed"
        if exit_code != 0:
            summary += ", 1 warning"
        return exit_code, summary + " in 1.23s\n", ""

    return _run


def _missing_spec(monkeypatch, missing):
    """Patch importlib.util.find_spec so the given modules appear missing."""

    real = __import__("importlib.util", fromlist=["find_spec"]).find_spec

    def _fake(name, *a, **k):
        if name in missing:
            return None
        return real(name, *a, **k)

    monkeypatch.setattr("aios.ci.checker.importlib.util.find_spec", _fake)


# -- CIStatus --------------------------------------------------------------

def test_ci_status_ok():
    assert CIStatus.PASS.ok
    assert CIStatus.WARNING.ok
    assert not CIStatus.FAIL.ok
    assert not CIStatus.UNKNOWN.ok


# -- CheckResult / CIReport ------------------------------------------------

def test_check_result_to_dict():
    r = CheckResult("deps", CIStatus.PASS, "ok", duration_s=0.5, passed=10, total=10)
    d = r.to_dict()
    assert d["name"] == "deps"
    assert d["status"] == "pass"
    assert d["passed"] == 10
    assert d["total"] == 10


def test_report_overall_pass():
    rep = CIReport(
        scope="core",
        results=[CheckResult("deps", CIStatus.PASS), CheckResult("core", CIStatus.PASS)],
    )
    assert rep.overall is CIStatus.PASS


def test_report_overall_fail_short_circuits():
    rep = CIReport(
        scope="full",
        results=[CheckResult("deps", CIStatus.FAIL)],
    )
    assert rep.overall is CIStatus.FAIL


def test_report_overall_unknown():
    rep = CIReport(scope="core", results=[CheckResult("deps", CIStatus.UNKNOWN)])
    assert rep.overall is CIStatus.UNKNOWN


def test_report_to_markdown_and_dict():
    rep = CIReport(scope="core", results=[CheckResult("deps", CIStatus.PASS, "ok")])
    md = rep.to_markdown()
    assert "core" in md and "PASS" in md
    assert rep.to_dict()["overall"] == "pass"


# -- CIChecker -------------------------------------------------------------

def test_parse_summary_counts():
    text = "2 failed, 58 passed, 1 warning in 4.10s\n"
    passed, total = CIChecker._parse_summary(text)
    assert passed == 58
    assert total == 60


def test_parse_summary_collection_error():
    text = "ERROR collecting aios/api/tests/test_api.py\n1 error in 1.47s\n"
    passed, total = CIChecker._parse_summary(text)
    assert passed == 0
    assert total == 1


def test_check_dependencies_missing(monkeypatch):
    _missing_spec(monkeypatch, missing=["fastapi"])
    res = CIChecker().check_dependencies()
    assert res.status is CIStatus.FAIL
    assert "fastapi" in res.detail


def test_check_dependencies_present(monkeypatch):
    _missing_spec(monkeypatch, missing=[])
    res = CIChecker().check_dependencies()
    assert res.status is CIStatus.PASS


def test_run_core_scope_passes_with_fake_runner():
    checker = CIChecker(runner=_fake_runner(passed=10, failed=0, exit_code=0))
    rep = checker.run(scope="core")
    assert rep.overall is CIStatus.PASS
    names = {r.name for r in rep.results}
    assert names == {"dependencies", "core-tests"}


def test_run_full_scope_includes_full_suite():
    checker = CIChecker(runner=_fake_runner(passed=100, failed=0, exit_code=0))
    rep = checker.run(scope="full")
    assert rep.overall is CIStatus.PASS
    names = {r.name for r in rep.results}
    assert names == {"dependencies", "core-tests", "full-suite"}


def test_run_fails_when_tests_fail():
    checker = CIChecker(runner=_fake_runner(passed=5, failed=3, exit_code=1))
    rep = checker.run(scope="core")
    assert rep.overall is CIStatus.FAIL
    core = next(r for r in rep.results if r.name == "core-tests")
    assert core.status is CIStatus.FAIL
    assert core.exit_code == 1


def test_run_short_circuits_without_deps(monkeypatch):
    _missing_spec(monkeypatch, missing=["pytest"])
    # Even with a "passing" runner, missing deps must skip the suites.
    checker = CIChecker(runner=_fake_runner(passed=10, failed=0))
    rep = checker.run(scope="full")
    assert rep.overall is CIStatus.FAIL
    names = {r.name for r in rep.results}
    assert names == {"dependencies"}  # suites not run


def test_run_ci_check_programmatic():
    rep = run_ci_check(scope="core")  # uses real runner in this env
    assert isinstance(rep, CIReport)
    assert rep.scope == "core"


def test_unknown_scope_raises():
    with pytest.raises(ValueError):
        CIChecker().run(scope="bogus")
