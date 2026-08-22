"""Tests for TASK-087 — Compatibility Conformance (Test Matrix)."""

from __future__ import annotations

import pytest

from aios.certification.certifier import Certifier
from aios.conformance.conformance import (
    ConformanceCheck,
    ConformanceReport,
    ConformanceRunner,
)
from aios.contracts.contract import Contract, ContractStatus, ContractSurface


def _frozen_contracts() -> list[Contract]:
    return [
        Contract(name="api", surface=ContractSurface.API, status=ContractStatus.FROZEN),
        Contract(name="schema", surface=ContractSurface.SCHEMA, status=ContractStatus.FROZEN),
        Contract(name="event", surface=ContractSurface.EVENT, status=ContractStatus.FROZEN),
    ]


def test_all_checks_pass_issues_conformance():
    runner = ConformanceRunner()
    report = runner.run("1.1.0", contracts=_frozen_contracts(), evidence_ref="ev-1")
    assert report.conformant is True
    assert set(report.checks_passed) == {c.value for c in ConformanceCheck.all()}
    assert runner.issue(report) is True


def test_one_check_fails_not_conformant():
    runner = ConformanceRunner()
    # Missing contracts -> contract check fails -> not conformant.
    report = runner.run("1.1.0", contracts=None, evidence_ref="ev-2")
    assert report.conformant is False
    assert runner.issue(report) is False


def test_version_policy_violation_conform_fails():
    runner = ConformanceRunner()
    # 2.0.0 crosses a major boundary -> version check fails.
    report = runner.run("2.0.0", contracts=_frozen_contracts(), evidence_ref="ev-3")
    assert report.conformant is False
    assert ConformanceCheck.VERSION.value not in report.checks_passed


def test_contract_not_frozen_conform_fails():
    runner = ConformanceRunner()
    contracts = _frozen_contracts()
    contracts[0].status = ContractStatus.DRAFT  # api not frozen
    report = runner.run("1.1.0", contracts=contracts, evidence_ref="ev-4")
    assert report.conformant is False
    assert ConformanceCheck.CONTRACT.value not in report.checks_passed


def test_report_has_evidence_provenance():
    runner = ConformanceRunner()
    report = runner.run("1.1.0", contracts=_frozen_contracts(), evidence_ref="ev-5")
    assert runner.provenance_complete(report) is True
    assert len(report.evidence_ref) > 0


def test_same_build_and_suite_deterministic():
    runner = ConformanceRunner()
    r1 = runner.run("1.1.0", contracts=_frozen_contracts(), evidence_ref="ev-6")
    r2 = runner.run("1.1.0", contracts=_frozen_contracts(), evidence_ref="ev-6")
    assert runner.report_hash(r1) == runner.report_hash(r2)
    assert r1.conformant == r2.conformant


def test_certification_only_when_conformant():
    runner = ConformanceRunner()
    certifier = Certifier()
    good = runner.run("1.1.0", contracts=_frozen_contracts(), evidence_ref="ev-7")
    cert = runner.certify(good, certifier=certifier, target_id="build-1.1.0")
    assert cert is not None
    assert certifier.is_certified("build-1.1.0") is True

    bad = runner.run("2.0.0", contracts=_frozen_contracts(), evidence_ref="ev-8")
    assert runner.certify(bad, certifier=certifier, target_id="build-2.0.0") is None
