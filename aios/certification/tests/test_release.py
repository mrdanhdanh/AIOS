"""Tests for the AIOS 1.0 Certification Suite release certifier (TASK-073)."""

from __future__ import annotations

import pytest

from aios.certification.release import (
    GateResult,
    ReleaseCertifier,
    ReleaseGateFailed,
    architecture_gate,
    contract_conformance_gate,
    governance_gates,
    harness_gate,
)


def _passing_gates():
    return [
        GateResult("registry", True),
        GateResult("dependency", True),
        GateResult("architecture", True),
        GateResult("deterministic", True),
        GateResult("evidence", True),
        GateResult("lifecycle", True),
        GateResult("regression", True),
        GateResult("contract", True),
        GateResult("harness", True),
    ]


def test_all_gates_pass_issues_certificate():
    cert = ReleaseCertifier(version="1.0.3").certify(
        _passing_gates(), contracts_conformed=["api", "schema"], evidence_ref="ev-1"
    )
    assert cert.version == "1.0.3"
    assert set(cert.gates_passed) == {
        "registry",
        "dependency",
        "architecture",
        "deterministic",
        "evidence",
        "lifecycle",
        "regression",
        "contract",
        "harness",
    }
    assert cert.contracts_conformed == ["api", "schema"]
    assert cert.evidence_ref == "ev-1"


def test_one_gate_fails_blocks_certificate_fail_closed():
    gates = _passing_gates()
    gates[2] = GateResult("architecture", False, "ARCH-001 violation")
    with pytest.raises(ReleaseGateFailed):
        ReleaseCertifier().certify(gates)


def test_architecture_violation_blocks_cert():
    # Build a fixture with an agent-layer module importing subprocess (ARCH-001).
    import os
    import tempfile
    from pathlib import Path

    tmp = Path(tempfile.mkdtemp())
    agent_dir = tmp / "agent"
    agent_dir.mkdir()
    (agent_dir / "__init__.py").write_text("")
    (agent_dir / "bad.py").write_text("import subprocess\n")
    try:
        res = architecture_gate(str(tmp))
        assert res.passed is False
        with pytest.raises(ReleaseGateFailed):
            ReleaseCertifier().certify([res])
    finally:
        import shutil

        shutil.rmtree(tmp, ignore_errors=True)


def test_contract_conformance_gate_runs():
    # Default registry (T064) is conforming -> PASS; if contracts absent -> FAIL.
    res = contract_conformance_gate()
    assert isinstance(res, GateResult)
    if res.passed:
        cert = ReleaseCertifier().certify([res])
        assert "contract" in cert.gates_passed


def test_certificate_has_provenance():
    cert = ReleaseCertifier().certify(_passing_gates(), evidence_ref="prov-xyz")
    assert cert.evidence_ref == "prov-xyz"


def test_deterministic_same_gates_same_result():
    a = ReleaseCertifier().certify(_passing_gates())
    b = ReleaseCertifier().certify(_passing_gates())
    assert a.gates_passed == b.gates_passed
    assert a.version == b.version


def test_governance_gates_named():
    names = {g.name for g in governance_gates()}
    assert {"registry", "dependency", "architecture", "deterministic", "evidence", "lifecycle", "regression"} <= names


def test_harness_gate_is_best_effort():
    assert isinstance(harness_gate(), GateResult)
