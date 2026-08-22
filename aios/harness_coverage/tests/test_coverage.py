"""Tests for TASK-090 — Harness Coverage + Readiness (Test Matrix)."""

from __future__ import annotations

from aios.certification.certifier import Certifier
from aios.harness_coverage.coverage import (
    CoverageChecker,
    CoverageMap,
    Readiness,
)
from aios.harness_coverage.coverage import CoverageReport


def _full_map() -> CoverageMap:
    m = CoverageMap()
    for s in ["api", "schema", "event", "capability", "tool"]:
        m.register(s, f"harness:{s}")
    return m


def _partial_map() -> CoverageMap:
    m = CoverageMap()
    m.register("api", "harness:api")
    m.register("schema", "harness:schema")
    return m


def test_coverage_full_threshold_ready():
    checker = CoverageChecker(threshold=1.0)
    report = checker.evaluate(
        ["api", "schema", "event", "capability", "tool"], _full_map(), evidence_ref="ev-1"
    )
    assert report.readiness is Readiness.READY
    assert report.coverage_ratio == 1.0
    assert report.gaps == []


def test_coverage_low_not_ready_fail_closed():
    checker = CoverageChecker(threshold=1.0)
    report = checker.evaluate(
        ["api", "schema", "event", "capability", "tool"], _partial_map(), evidence_ref="ev-2"
    )
    assert report.readiness is Readiness.NOT_READY
    assert report.coverage_ratio < 1.0


def test_gap_reported_not_hidden():
    checker = CoverageChecker(threshold=1.0)
    report = checker.evaluate(
        ["api", "schema", "event", "capability", "tool"], _partial_map(), evidence_ref="ev-3"
    )
    assert set(report.gaps) == {"event", "capability", "tool"}


def test_same_system_same_coverage_deterministic():
    checker = CoverageChecker(threshold=1.0)
    r1 = checker.evaluate(["api", "schema"], _partial_map(), evidence_ref="ev-4")
    r2 = checker.evaluate(["api", "schema"], _partial_map(), evidence_ref="ev-4")
    assert checker.report_hash(r1) == checker.report_hash(r2)
    assert r1.coverage_ratio == r2.coverage_ratio


def test_readiness_evidence_provenance():
    checker = CoverageChecker(threshold=1.0)
    report = checker.evaluate(["api"], _full_map(), evidence_ref="ev-5")
    assert checker.provenance_complete(report) is True


def test_harness_certify_ready_only():
    checker = CoverageChecker(threshold=1.0)
    certifier = Certifier()
    ready = checker.evaluate(["api", "schema", "event", "capability", "tool"], _full_map())

    cert_ready = checker.certify(ready, certifier=certifier, target_id="build-1")
    assert cert_ready is not None
    assert cert_ready.status is __import__(
        "aios.certification.contracts", fromlist=["CertStatus"]
    ).CertStatus.CERTIFIED

    blocked = checker.evaluate(
        ["api", "schema", "event", "capability", "tool"], _partial_map()
    )
    cert_blocked = checker.certify(blocked, certifier=certifier, target_id="build-2")
    assert cert_blocked is None


def test_from_behavior_scenarios_registers_surfaces():
    from aios.behavioral.behavioral import BehaviorScenario, BehaviorSurface

    m = CoverageMap()
    m.from_behavior_scenarios(
        [BehaviorScenario(scenario_id="s1", given="g", when="w", then="t", surface=BehaviorSurface.API)]
    )
    assert m.harnessed("s1")
