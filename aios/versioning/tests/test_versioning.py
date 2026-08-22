"""Tests for TASK-084 — Version + Compatibility Baseline (Test Matrix)."""

from __future__ import annotations

import pytest

from aios.versioning.versioning import (
    ChangeType,
    CompatibilityMatrix,
    VersionBaseline,
    VersionBump,
    VersionChange,
    VersionPolicy,
    VersionPolicyEngine,
)


def test_breaking_change_requires_major_plus_adr_and_deprecation():
    eng = VersionPolicyEngine()
    change = VersionChange(
        change_type=ChangeType.BREAKING,
        description="remove legacy endpoint",
        has_adr=True,
        has_deprecation_notice=True,
        evidence_ref="evt-1",
    )
    decision = eng.decide(change)
    assert decision.bump is VersionBump.MAJOR
    assert decision.allowed is True
    assert "MAJOR" in decision.reason


def test_compatible_change_minor():
    eng = VersionPolicyEngine()
    change = VersionChange(change_type=ChangeType.COMPATIBLE, evidence_ref="evt-2")
    decision = eng.decide(change)
    assert decision.bump is VersionBump.MINOR
    assert decision.allowed is True


def test_fix_patch():
    eng = VersionPolicyEngine()
    change = VersionChange(change_type=ChangeType.FIX, evidence_ref="evt-3")
    decision = eng.decide(change)
    assert decision.bump is VersionBump.PATCH
    assert decision.allowed is True


def test_deprecated_without_notice_blocked():
    eng = VersionPolicyEngine()
    # Breaking change but missing ADR and/or deprecation notice -> blocked.
    change = VersionChange(change_type=ChangeType.BREAKING, has_adr=True)
    decision = eng.decide(change)
    assert decision.allowed is False
    assert "BLOCKED" in decision.reason

    change2 = VersionChange(change_type=ChangeType.BREAKING, has_deprecation_notice=True)
    decision2 = eng.decide(change2)
    assert decision2.allowed is False


def test_same_change_type_same_bump_deterministic():
    eng = VersionPolicyEngine()
    a = eng.decide(VersionChange(change_type=ChangeType.BREAKING, has_adr=True,
                                 has_deprecation_notice=True))
    b = eng.decide(VersionChange(change_type=ChangeType.BREAKING, has_adr=True,
                                 has_deprecation_notice=True))
    assert a.bump is b.bump is VersionBump.MAJOR
    assert a.allowed == b.allowed


def test_version_policy_evidence_provenance():
    eng = VersionPolicyEngine()
    with_ev = VersionChange(change_type=ChangeType.FIX, evidence_ref="evt-x")
    without_ev = VersionChange(change_type=ChangeType.FIX)
    assert eng.provenance_complete(with_ev) is True
    assert eng.provenance_complete(without_ev) is False


def test_compatibility_matrix_1_0_vs_1_x():
    # 1.0 is compatible with 1.x (same major, target >= base).
    assert CompatibilityMatrix.is_compatible("1.0.0", "1.1.0") is True
    assert CompatibilityMatrix.is_compatible("1.0.0", "1.0.1") is True
    # Different major -> breaking, not compatible.
    assert CompatibilityMatrix.is_compatible("1.0.0", "2.0.0") is False
    assert CompatibilityMatrix.is_breaking("1.0.0", "2.0.0") is True
    assert CompatibilityMatrix.is_breaking("1.0.0", "1.1.0") is False


def test_bump_version_computes_next():
    eng = VersionPolicyEngine()
    assert eng.bump_version("1.0.0", VersionBump.MAJOR) == "2.0.0"
    assert eng.bump_version("1.0.0", VersionBump.MINOR) == "1.1.0"
    assert eng.bump_version("1.0.3", VersionBump.PATCH) == "1.0.4"


def test_baseline_hash_deterministic():
    eng = VersionPolicyEngine()
    h1 = eng.baseline_hash(VersionBaseline())
    h2 = eng.baseline_hash(VersionBaseline())
    assert h1 == h2
    assert len(h1) == 64
