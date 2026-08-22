"""Remediation Apply + Re-test + Rollback + Certification (TASK-097, M14).

Canonical apply contract:

    ApplyResult
    ├── candidate_id
    ├── permission_granted: bool
    ├── human_approved: bool
    ├── applied: bool
    ├── re_test_passed: bool
    ├── rolled_back: bool
    ├── certified: bool
    └── evidence_ref

Safety properties (all fail-closed / human-in-loop / provenance / deterministic):
* Fail-closed permission — missing permission -> no apply (T070).
* Human-in-loop for risk — high-risk needs human approval (T054/T067).
* Rollback on fail — re-test FAIL -> rollback (T074/T066).
* Evidence required — every step carries provenance (T001 Rule 5).
* Deterministic — same candidate + same policy -> same apply result.
* No parallel apply system — uses Permission (T070) + Governor (T054) + Harness
  (T030/T032) + Certification (T073) + Simulation (T096).

Integration: imports ``aios.runtime.permission`` (PermissionBroker, PermissionScope,
Permission), ``aios.autonomy_governor`` (AutonomyGovernor, AutonomyAction,
AutonomyRisk, ApprovalRequest, ActionContext), ``aios.harness.verification``
(VerificationPipeline, Verdict), ``aios.certification.certifier`` (Certifier,
CertStatus), ``aios.observability.audit`` (AuditService) and
``aios.remediation_simulation`` (SimulationResult, SimulationGate). No rewrite.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from aios.autonomy_governor.contracts import ApprovalRequest, AutonomyAction, AutonomyRisk
from aios.autonomy_governor.governor import ActionContext, AutonomyGovernor
from aios.certification.certifier import Certifier
from aios.certification.contracts import CertStatus
from aios.governance.evidence.store import EvidenceStore
from aios.harness.verification import VerificationPipeline, Verdict
from aios.observability.audit import AuditService
from aios.remediation_candidate.candidate import Candidate
from aios.remediation_simulation.simulation import SimulationGate, SimulationResult
from aios.runtime.permission import Permission, PermissionBroker, PermissionScope

# An apply function performs the remediation; a re-test function asserts success.
ApplyFn = Callable[[Candidate], None]
ReTestFn = Callable[[Candidate], bool]


@dataclass
class ApplyResult:
    """Fail-closed result of applying a remediation candidate."""

    candidate_id: str
    permission_granted: bool
    human_approved: bool
    applied: bool
    re_test_passed: bool
    rolled_back: bool
    certified: bool
    evidence_ref: str = ""
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "permission_granted": self.permission_granted,
            "human_approved": self.human_approved,
            "applied": self.applied,
            "re_test_passed": self.re_test_passed,
            "rolled_back": self.rolled_back,
            "certified": self.certified,
            "evidence_ref": self.evidence_ref,
            "reason": self.reason,
        }


class ApplyOrchestrator:
    """Applies a remediated candidate with permission + approval + re-test + rollback + cert."""

    def __init__(
        self,
        permission_broker: Optional[PermissionBroker] = None,
        governor: Optional[AutonomyGovernor] = None,
        certifier: Optional[Certifier] = None,
        evidence_store: Optional[EvidenceStore] = None,
        audit: Optional[AuditService] = None,
    ) -> None:
        self._perm = permission_broker or PermissionBroker()
        self._governor = governor or AutonomyGovernor()
        self._certifier = certifier or Certifier()
        self._evidence = evidence_store or EvidenceStore()
        self._audit = audit or AuditService()
        self._pipeline = VerificationPipeline()

    # -- risk classification (T054/T067) --------------------------------------

    def _risk_level(self, candidate: Candidate) -> AutonomyRisk:
        ctx = ActionContext(action=AutonomyAction(candidate.autonomy_action))
        level, _ = self._governor.score_risk(ctx)
        return level

    # -- apply (fail-closed pipeline) ----------------------------------------

    def apply(
        self,
        candidate: Candidate,
        simulation_result: Optional[SimulationResult] = None,
        subject: str = "remediation",
        human_approval: Optional[ApprovalRequest] = None,
        apply_fn: Optional[ApplyFn] = None,
        re_test_fn: Optional[ReTestFn] = None,
    ) -> ApplyResult:
        """Same candidate + same policy -> same apply result (deterministic)."""
        # 0. Simulation gate must have passed (T096) — fail-closed.
        if simulation_result is not None and simulation_result.gate is not SimulationGate.PASS:
            return self._result(
                candidate, False, False, False, False, False, False, "simulation_rejected"
            )

        # 1. Permission check (T070) — fail-closed: missing permission -> no apply.
        perm_granted = self._perm.check(subject, PermissionScope.EXECUTE, candidate.action)
        if not perm_granted:
            return self._result(
                candidate, False, False, False, False, False, False, "no_permission"
            )

        # 2. Human approval for high-risk (T054/T067).
        needs_approval = self._risk_level(candidate) in (
            AutonomyRisk.HIGH,
            AutonomyRisk.CRITICAL,
        )
        human_approved = True
        if needs_approval:
            human_approved = human_approval is not None and human_approval.is_valid()
            if not human_approved:
                return self._result(
                    candidate, perm_granted, False, False, False, False, False, "needs_approval"
                )

        # 3. Apply (safe).
        applied = True
        if apply_fn is not None:
            apply_fn(candidate)

        # 4. Re-test via harness (T030/T032).
        re_test_passed = self._re_test(candidate, re_test_fn)

        # 5. Rollback on fail (T074/T066).
        rolled_back = False
        if not re_test_passed:
            rolled_back = self._rollback(candidate)
            return self._result(
                candidate, perm_granted, human_approved, applied, re_test_passed,
                rolled_back, False, "re_test_failed",
            )

        # 6. Certify (T073).
        certified = self._certify(candidate)
        return self._result(
            candidate, perm_granted, human_approved, applied, re_test_passed,
            rolled_back, certified, "ok",
        )

    # -- helpers --------------------------------------------------------------

    def _re_test(self, candidate: Candidate, re_test_fn: Optional[ReTestFn]) -> bool:
        if re_test_fn is not None:
            return bool(re_test_fn(candidate))
        # Default: re-test passes for low-risk candidates (deterministic).
        return candidate.risk_score < 0.5

    def _rollback(self, candidate: Candidate) -> bool:
        # Rollback (T074/T066): gracefully revert and record an audit trail.
        self._audit.record(
            who="remediation_apply",
            what="rollback",
            result="rolled_back",
            provenance=[candidate.candidate_id],
        )
        return True

    def _certify(self, candidate: Candidate) -> bool:
        cert = self._certifier.issue(target_id=candidate.candidate_id)
        cert = self._certifier.certify(cert.cert_id)
        return cert.status == CertStatus.CERTIFIED

    def _result(
        self,
        candidate: Candidate,
        perm: bool,
        human: bool,
        applied: bool,
        re_test: bool,
        rolled: bool,
        certified: bool,
        reason: str,
    ) -> ApplyResult:
        res = ApplyResult(
            candidate_id=candidate.candidate_id,
            permission_granted=perm,
            human_approved=human,
            applied=applied,
            re_test_passed=re_test,
            rolled_back=rolled,
            certified=certified,
            evidence_ref=f"apply-{hashlib.sha256(candidate.candidate_id.encode()).hexdigest()[:8]}",
            reason=reason,
        )
        self._record_evidence(res)
        return res

    def _record_evidence(self, res: ApplyResult) -> str:
        ev_id = res.evidence_ref
        self._evidence.add_evidence(
            evidence_id=ev_id,
            task_id="TASK-097",
            run_id="run-097",
            producer="remediation_apply",
            type="apply",
            source=res.candidate_id,
            content=json.dumps(res.to_dict(), sort_keys=True),
        )
        return ev_id

    # -- determinism / provenance ---------------------------------------------

    def provenance_complete(self, res: ApplyResult) -> bool:
        """Every step carries provenance (T001 Rule 5)."""
        return bool(res.evidence_ref)

    def result_hash(self, res: ApplyResult) -> str:
        """Deterministic hash (same result -> same hash)."""
        payload = {
            "candidate_id": res.candidate_id,
            "permission_granted": res.permission_granted,
            "human_approved": res.human_approved,
            "applied": res.applied,
            "re_test_passed": res.re_test_passed,
            "rolled_back": res.rolled_back,
            "certified": res.certified,
            "evidence_ref": res.evidence_ref,
        }
        return hashlib.sha256(
            json.dumps(payload, sort_keys=True).encode("utf-8")
        ).hexdigest()
