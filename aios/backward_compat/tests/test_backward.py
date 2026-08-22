"""Tests for TASK-086 — Backward Compatibility (Test Matrix)."""

from __future__ import annotations

import pytest

from aios.backward_compat.backward import (
    BackwardCompatChecker,
    CompatCheck,
    CompatSurface,
    CompatSuiteResult,
)


def test_1_0_consumer_calls_1_x_api_works():
    chk = BackwardCompatChecker()
    res = chk.check(CompatCheck(surface=CompatSurface.API, provider_version="1.1.0"))
    assert res.compatible is True
    assert res.blocked is False


def test_break_1_0_schema_blocked():
    chk = BackwardCompatChecker()
    res = chk.check(CompatCheck(
        surface=CompatSurface.SCHEMA, provider_version="1.1.0", breaking=True,
        evidence_ref="e1",
    ))
    assert res.compatible is False
    assert res.blocked is True
    assert "BLOCKED" in res.reason


def test_compat_suite_pass_allows_done():
    chk = BackwardCompatChecker()
    checks = [
        CompatCheck(surface=CompatSurface.API, provider_version="1.1.0", evidence_ref="a"),
        CompatCheck(surface=CompatSurface.SCHEMA, provider_version="1.1.0", evidence_ref="b"),
        CompatCheck(surface=CompatSurface.EVENT, provider_version="1.0.5", evidence_ref="c"),
    ]
    suite: CompatSuiteResult = chk.run_suite(checks)
    assert suite.passed is True
    assert suite.blocked is False


def test_compat_suite_fail_blocks():
    chk = BackwardCompatChecker()
    checks = [
        CompatCheck(surface=CompatSurface.API, provider_version="1.1.0", evidence_ref="a"),
        CompatCheck(surface=CompatSurface.SCHEMA, provider_version="1.1.0",
                    breaking=True, evidence_ref="b"),
    ]
    suite = chk.run_suite(checks)
    assert suite.passed is False
    assert suite.blocked is True


def test_same_surface_and_version_deterministic():
    chk = BackwardCompatChecker()
    a = chk.check(CompatCheck(surface=CompatSurface.EVENT, provider_version="1.2.0"))
    b = chk.check(CompatCheck(surface=CompatSurface.EVENT, provider_version="1.2.0"))
    assert a.compatible == b.compatible
    assert a.blocked == b.blocked


def test_compat_evidence_provenance():
    chk = BackwardCompatChecker()
    with_ev = CompatCheck(surface=CompatSurface.API, provider_version="1.1.0",
                          evidence_ref="ev-x")
    without = CompatCheck(surface=CompatSurface.API, provider_version="1.1.0")
    assert chk.provenance_complete(with_ev) is True
    assert chk.provenance_complete(without) is False


def test_suite_hash_deterministic():
    chk = BackwardCompatChecker()
    checks = [
        CompatCheck(surface=CompatSurface.API, provider_version="1.1.0", evidence_ref="a"),
        CompatCheck(surface=CompatSurface.SCHEMA, provider_version="1.0.5", evidence_ref="b"),
    ]
    h1 = chk.suite_hash(checks)
    h2 = chk.suite_hash(checks)
    assert h1 == h2
    assert len(h1) == 64
