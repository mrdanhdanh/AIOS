"""Tests for Continuous Certification (TASK-101)."""

from aios.continuous_certification.cert import CertGate, ContinuousCertEngine


def test_change_triggers_cert():
    eng = ContinuousCertEngine()
    assert eng.trigger_on_change("change-1") is True
    assert eng.trigger_on_change("") is False


def test_all_gates_pass_deploy_allowed():
    eng = ContinuousCertEngine()
    run = eng.run_suite("change-pass")
    assert run.all_passed is True
    assert run.deploy_allowed is True


def test_one_gate_fail_blocks_deploy():
    eng = ContinuousCertEngine()
    run = eng.run_suite("change-fail", gate_overrides={CertGate.HARNESS.value: False})
    assert run.all_passed is False
    assert run.deploy_allowed is False  # fail-closed


def test_cert_reruns_on_each_change():
    eng = ContinuousCertEngine()
    r1 = eng.run_suite("change-a")
    r2 = eng.run_suite("change-b")
    # Both changes are certified (never skipped).
    assert r1.change_id == "change-a"
    assert r2.change_id == "change-b"
    assert r1.evidence_ref != r2.evidence_ref


def test_deterministic_cert_result():
    eng = ContinuousCertEngine()
    r1 = eng.run_suite("change-det")
    r2 = eng.run_suite("change-det")
    assert eng.result_hash(r1) == eng.result_hash(r2)


def test_cert_evidence_provenance():
    eng = ContinuousCertEngine()
    run = eng.run_suite("change-ev")
    assert eng.provenance_complete(run) is True
    assert run.evidence_ref
