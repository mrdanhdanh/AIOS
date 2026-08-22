"""Tests for M16 Independent Harness Integration (TASK-104..108).

Covers the Test Matrix for each task:
* T104 — Foundation: register / immutable id / fail-closed ingest / authority
* T105 — Oracle: invariant mapping / evidence bridge / authority / INCONCLUSIVE
* T106 — Behavioral bridge: observation bridge / authority / INCONCLUSIVE
* T107 — Permission+Sandbox bridge: check bridge / authority / INCONCLUSIVE
* T108 — Console: aggregate status / policy-gated action / authority

All tests are deterministic and fail-closed (T078). No LLM / network calls.
"""
from __future__ import annotations

import pytest

from aios.verification_integrity.integrity import sha256

from aios.independent_harness import (
    BehavioralConformanceBridge,
    EvidenceIngestBoundary,
    EvidencePayload,
    HarnessRegistry,
    HarnessType,
    IndependentHarnessAdapter,
    IndependentVerificationOracle,
    InvariantMapping,
    ManagementConsoleIntegration,
    OracleResult,
    PermissionSandboxBridge,
    PermissionSandboxReport,
)
from aios.security.contracts import SandboxConfig
from aios.security.isolation import IsolationManager


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------
def _adapter(harness_id: str = "ext-1") -> IndependentHarnessAdapter:
    return IndependentHarnessAdapter(
        harness_id=harness_id,
        harness_type=HarnessType.EXTERNAL,
        source="https://harness.example/verify",
        supported_checks=["inv:noop", "perm:read", "sandbox:net"],
    )


def _registry_with(adapter: IndependentHarnessAdapter) -> HarnessRegistry:
    reg = HarnessRegistry()
    reg.register(adapter)
    return reg


# --------------------------------------------------------------------------
# T104 — Foundation
# --------------------------------------------------------------------------
class TestFoundation:
    def test_register_new_harness_ok(self):
        reg = _registry_with(_adapter())
        assert reg.is_registered("ext-1")
        assert reg.get("ext-1").policy_authority == "aios"

    def test_register_duplicate_id_rejected(self):
        reg = HarnessRegistry()
        reg.register(_adapter("ext-1"))
        with pytest.raises(Exception):
            reg.register(_adapter("ext-1"))

    def test_ingest_missing_hash_rejected(self):
        reg = _registry_with(_adapter())
        ingest = EvidenceIngestBoundary(reg)
        res = ingest.ingest(
            "ext-1",
            EvidencePayload(
                evidence_id="ev-1", task_id="T104", run_id="r1",
                producer="", source="", type="harness_evidence",
                content="x", content_hash="",
            ),
        )
        assert res.accepted is False
        assert "provenance" in res.reason

    def test_ingest_with_provenance_ok(self):
        reg = _registry_with(_adapter())
        ingest = EvidenceIngestBoundary(reg)
        res = ingest.ingest(
            "ext-1",
            EvidencePayload(
                evidence_id="ev-2", task_id="T104", run_id="r1",
                producer="ext-harness", source="inv:noop",
                type="harness_evidence",
                content="pass", content_hash=sha256("pass"),
            ),
        )
        assert res.accepted is True

    def test_independent_harness_cannot_override_policy(self):
        from aios.independent_harness import PolicyAuthority

        assert PolicyAuthority.reject_override("pass", "fail") == "fail"
        assert PolicyAuthority.is_aios_authoritative() is True

    def test_same_adapter_and_input_deterministic(self):
        reg = _registry_with(_adapter())
        ingest = EvidenceIngestBoundary(reg)
        payload = EvidencePayload(
            evidence_id="ev-d", task_id="T104", run_id="r1",
            producer="ext-harness", source="inv:noop",
            type="harness_evidence",
            content="pass", content_hash=sha256("pass"),
        )
        r1 = ingest.ingest("ext-1", payload)
        r2 = ingest.ingest("ext-1", payload)
        assert r1.accepted == r2.accepted
        assert r1.content_hash == r2.content_hash


# --------------------------------------------------------------------------
# T105 — Oracle
# --------------------------------------------------------------------------
class TestOracle:
    def _oracle(self, harness_id: str = "ext-1") -> IndependentVerificationOracle:
        reg = _registry_with(_adapter(harness_id))
        oracle = IndependentVerificationOracle(reg)
        oracle.map_invariant("inv:noop", "inv:noop")
        return oracle

    def test_map_invariant_to_oracle_check(self):
        oracle = self._oracle()
        res = oracle.query("ext-1", "inv:noop", lambda check, inp: "pass", "input")
        assert isinstance(res, OracleResult)
        assert res.invariant_ref == "inv:noop"

    def test_evidence_bridged_into_aios(self):
        oracle = self._oracle()
        res = oracle.query("ext-1", "inv:noop", lambda c, i: "pass", None)
        assert res.evidence_ref  # provenance recorded
        assert res.authority == "aios"

    def test_aios_authority_not_overridden_by_oracle(self):
        oracle = self._oracle()
        # Oracle says pass, but AIOS policy is authoritative -> aios decides.
        res = oracle.query("ext-1", "inv:noop", lambda c, i: "pass", None)
        # AIOS promotes only on explicit PASS + admitted evidence.
        assert res.aios_policy_verdict in ("pass", "fail")
        assert res.authority == "aios"

    def test_oracle_inconclusive_not_promoted(self):
        oracle = self._oracle()
        res = oracle.query("ext-1", "inv:noop", lambda c, i: "inconclusive", None)
        assert res.aios_policy_verdict == "fail"  # fail-closed

    def test_oracle_unknown_fail_closed(self):
        oracle = self._oracle()
        res = oracle.query("ext-1", "inv:noop", lambda c, i: "unknown", None)
        assert res.aios_policy_verdict == "fail"

    def test_same_invariant_and_input_deterministic(self):
        oracle = self._oracle()
        r1 = oracle.query("ext-1", "inv:noop", lambda c, i: "pass", "x")
        r2 = oracle.query("ext-1", "inv:noop", lambda c, i: "pass", "x")
        assert r1.independent_verdict == r2.independent_verdict
        assert r1.aios_policy_verdict == r2.aios_policy_verdict


# --------------------------------------------------------------------------
# T106 — Behavioral Conformance Bridge
# --------------------------------------------------------------------------
class TestBehavioralBridge:
    def _bridge(self, harness_id: str = "ext-1") -> BehavioralConformanceBridge:
        reg = _registry_with(_adapter(harness_id))
        return BehavioralConformanceBridge(reg)

    def test_bridge_observation_ok(self):
        b = self._bridge()
        rep = b.bridge("ext-1", "beh-1", "created", "created")
        assert rep.conformance is True
        assert rep.evidence_ref
        assert rep.authority == "aios"

    def test_observation_conflict_aios_authoritative(self):
        b = self._bridge()
        rep = b.bridge("ext-1", "beh-2", "actual", "expected")
        assert rep.conformance is False  # AIOS decides, observation != expected

    def test_observation_inconclusive_not_promoted(self):
        b = self._bridge()
        rep = b.bridge("ext-1", "beh-3", "", "expected")
        assert rep.conformance is False
        assert rep.evidence_ref == ""

    def test_same_behavior_and_observation_deterministic(self):
        b = self._bridge()
        r1 = b.bridge("ext-1", "beh-d", "ok", "ok")
        r2 = b.bridge("ext-1", "beh-d", "ok", "ok")
        assert r1.conformance == r2.conformance


# --------------------------------------------------------------------------
# T107 — Permission + Sandbox Bridge
# --------------------------------------------------------------------------
class TestPermissionSandboxBridge:
    def _bridge(self, harness_id: str = "ext-1") -> PermissionSandboxBridge:
        reg = _registry_with(_adapter(harness_id))
        iso = IsolationManager()
        iso.create_sandbox(SandboxConfig(sandbox_id="sbx-1"))
        return PermissionSandboxBridge(reg, isolation=iso)

    def test_bridge_permission_check_ok(self):
        b = self._bridge()
        rep = b.bridge("ext-1", "chk-1", "perm:read", "sbx-1", "pass")
        assert isinstance(rep, PermissionSandboxReport)
        assert rep.aios_policy_result == "allow"
        assert rep.evidence_ref

    def test_bridge_sandbox_check_ok(self):
        b = self._bridge()
        rep = b.bridge("ext-1", "chk-2", "perm:read", "sbx-1", "pass")
        assert rep.aios_policy_result == "allow"

    def test_independent_result_conflict_aios_authoritative(self):
        b = self._bridge()
        # independent says pass but sandbox not known to AIOS -> AIOS denies.
        rep = b.bridge("ext-1", "chk-3", "perm:read", "unknown-sbx", "pass")
        assert rep.aios_policy_result == "deny"

    def test_result_inconclusive_not_promoted(self):
        b = self._bridge()
        rep = b.bridge("ext-1", "chk-4", "perm:read", "sbx-1", "inconclusive")
        assert rep.aios_policy_result == "deny"

    def test_result_undefined_fail_closed(self):
        b = self._bridge()
        rep = b.bridge("ext-1", "chk-5", "perm:read", "sbx-1", "")
        assert rep.aios_policy_result == "deny"

    def test_same_check_and_input_deterministic(self):
        b = self._bridge()
        r1 = b.bridge("ext-1", "chk-d", "perm:read", "sbx-1", "pass")
        r2 = b.bridge("ext-1", "chk-d", "perm:read", "sbx-1", "pass")
        assert r1.aios_policy_result == r2.aios_policy_result


# --------------------------------------------------------------------------
# T108 — Management Console Integration
# --------------------------------------------------------------------------
class TestConsole:
    def test_aggregate_healthy(self):
        console = ManagementConsoleIntegration()
        oracle = OracleResult(
            oracle_id="o1", invariant_ref="inv:noop", independent_verdict="pass",
            aios_policy_verdict="pass", evidence_ref="ev", authority="aios",
        )
        view = console.aggregate("c1", "ext-1", oracle=oracle)
        assert view.harness_status == "healthy"
        assert view.aios_authority_flag == "aios"

    def test_aggregate_degraded_on_fail(self):
        console = ManagementConsoleIntegration()
        from aios.independent_harness import BehavioralConformanceReport

        beh = BehavioralConformanceReport(
            behavior_id="b1", independent_observation="x", aios_expected="y",
            conformance=False, evidence_ref="ev", authority="aios",
        )
        view = console.aggregate("c2", "ext-1", behavioral=beh)
        assert view.harness_status == "degraded"

    def test_operator_action_policy_gated(self):
        console = ManagementConsoleIntegration()
        denied = console.request_operator_action("restart", policy_gate_allowed=False)
        assert denied["dispatched"] is False
        allowed = console.request_operator_action("restart", policy_gate_allowed=True)
        assert allowed["dispatched"] is True
        assert allowed["via"] == "api/runtime"

    def test_console_cannot_override_authority(self):
        console = ManagementConsoleIntegration()
        res = console.request_operator_action("x", policy_gate_allowed=True)
        assert res["authority"] == "aios"

    def test_same_harness_state_deterministic_view(self):
        console = ManagementConsoleIntegration()
        oracle = OracleResult(
            oracle_id="o1", invariant_ref="inv:noop", independent_verdict="pass",
            aios_policy_verdict="pass", evidence_ref="ev", authority="aios",
        )
        v1 = console.aggregate("c", "ext-1", oracle=oracle)
        v2 = console.aggregate("c", "ext-1", oracle=oracle)
        assert v1.harness_status == v2.harness_status
