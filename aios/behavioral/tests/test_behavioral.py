"""Tests for TASK-089 — Behavioral Conformance (Test Matrix)."""

from __future__ import annotations

import pytest

from aios.behavioral.behavioral import (
    BehaviorConformanceChecker,
    BehaviorHarness,
    BehaviorScenario,
    BehaviorSurface,
)
from aios.harness.verification import Verdict


def _echo_driver(scenario: BehaviorScenario) -> str:
    """A deterministic system driver that returns the scenario's `then`."""
    return scenario.then


def _wrong_driver(scenario: BehaviorScenario) -> str:
    """A driver that always returns a value different from expected."""
    return "UNEXPECTED_OUTPUT"


def _test_scenario() -> BehaviorScenario:
    return BehaviorScenario(
        scenario_id="sc-1",
        given="system online",
        when="call /health",
        then="ok",
        surface=BehaviorSurface.API,
    )


def test_scenario_conform_pass():
    h = BehaviorHarness()
    sc = _test_scenario()
    h.observe(sc, _echo_driver)
    assert sc.conforms is True
    assert sc.actual_observable == "ok"


def test_behavior_deviation_not_conform_fail_closed():
    h = BehaviorHarness()
    sc = _test_scenario()
    h.observe(sc, _wrong_driver)
    assert sc.conforms is False
    assert sc.actual_observable == "UNEXPECTED_OUTPUT"


def test_non_observable_spec_blocked():
    h = BehaviorHarness()
    sc = BehaviorScenario(
        scenario_id="sc-bad",
        given="",
        when="",
        then="",
        observable=False,  # internal/non-observable spec
    )
    h.observe(sc, _echo_driver)
    assert sc.conforms is False
    assert sc.is_observable() is False


def test_same_scenario_deterministic():
    h = BehaviorHarness()
    sc = _test_scenario()
    assert h.is_deterministic(sc, _echo_driver, repeats=3) is True
    assert h.is_deterministic(sc, _wrong_driver, repeats=3) is True


def test_behavior_evidence_provenance():
    store = __import__("aios.governance.evidence.store", fromlist=["EvidenceStore"]).EvidenceStore()
    h = BehaviorHarness(evidence_store=store)
    sc = _test_scenario()
    h.observe(sc, _echo_driver, run_id="run-1")
    assert sc.evidence_ref
    assert store.get(sc.evidence_ref).content_hash


def test_harness_verify_returns_verdict():
    h = BehaviorHarness()
    sc = _test_scenario()
    verdict = h.verify(sc, _echo_driver, run_id="run-2")
    assert verdict is Verdict.PASS

    sc2 = _test_scenario()
    verdict2 = h.verify(sc2, _wrong_driver, run_id="run-3")
    assert verdict2 is Verdict.FAIL


def test_replay_check_reproduces():
    h = BehaviorHarness()
    sc = _test_scenario()
    assert h.replay_check(sc, _echo_driver, run_id="run-4") is True


def test_conformance_suite_fail_closed():
    checker = BehaviorConformanceChecker()
    scenarios = [
        _test_scenario(),
        BehaviorScenario(scenario_id="sc-2", given="g", when="w", then="x"),
    ]
    result = checker.check(scenarios, _wrong_driver)
    assert result.conformant is False
    assert "sc-1" in result.non_conforming
    assert checker.provenance_complete(result) is True


def test_conformance_suite_pass_and_report():
    checker = BehaviorConformanceChecker()
    scenarios = [_test_scenario()]
    result = checker.check(scenarios, _echo_driver, run_id="suite-1")
    assert result.conformant is True
    report = checker.to_conformance_report(result)
    assert report.conformant is True
    assert checker.result_hash(result)
