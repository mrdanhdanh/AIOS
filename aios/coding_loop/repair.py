"""Repair Planner (TASK-149, M21).

Plans a repair (patch) from a diagnostic report (T148), using Planning Engine
T026 + Autonomous Recovery T055. Built on Diagnostic Agent T148 + Evidence T001.
TASK-149 is a *planner*, not a new executor.

Layering: ``coding_loop`` is an ``unknown`` (infra) layer.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Dict, Optional

from aios.coding_loop._common import CodingLoopError, _hash, _now
from aios.coding_loop.diagnostic import DiagnosticReport


@dataclass
class RepairPlan:
    """Immutable-by-id repair plan (T149)."""

    plan_id: str
    diagnostic_ref: str
    patch_spec: str
    rollback_ref: str
    evidence_ref: str
    authority: str = "aios"
    created_at: str = field(default_factory=_now)

    def __post_init__(self) -> None:
        if not self.plan_id:
            raise CodingLoopError("plan_id required (T001 Rule 1, immutable).")
        if not self.evidence_ref:
            raise CodingLoopError("RepairPlan requires evidence_ref (T001 Rule 5).")
        # Fail-closed: every plan must carry a rollback (T055).
        if not self.rollback_ref:
            raise CodingLoopError("RepairPlan requires rollback_ref (T055, fail-closed).")


class RepairPlanner:
    """Deterministic repair planner; fail-closed on missing rollback / UNKNOWN (T149)."""

    def __init__(self) -> None:
        self._plans: Dict[str, RepairPlan] = {}

    def plan(
        self,
        diagnostic_report: DiagnosticReport,
        rollback_ref: str,
        evidence_ref: Optional[str] = None,
        plan_id: Optional[str] = None,
    ) -> RepairPlan:
        # Fail-closed: plan requires a diagnostic report with provenance (T001 Rule 5).
        if diagnostic_report is None or not diagnostic_report.evidence_ref:
            raise CodingLoopError("Plan requires diagnostic report with provenance (T001 Rule 5).")
        # Fail-closed: every plan must have a rollback (T055).
        if not rollback_ref:
            raise CodingLoopError("Plan requires rollback_ref (T055, fail-closed).")
        # Fail-closed: cannot plan from an UNKNOWN diagnosis (T078).
        if not diagnostic_report.root_cause or diagnostic_report.root_cause == "UNKNOWN":
            raise CodingLoopError("Cannot plan from UNKNOWN diagnosis (T078, fail-closed).")
        patch_spec = self._build_patch_spec(diagnostic_report)
        ev = evidence_ref or diagnostic_report.evidence_ref
        pid = plan_id or f"plan-{uuid.uuid4().hex[:12]}"
        if pid in self._plans:
            raise CodingLoopError(f"Duplicate plan_id '{pid}' (T001 Rule 1).")
        rp = RepairPlan(
            plan_id=pid,
            diagnostic_ref=diagnostic_report.report_id,
            patch_spec=patch_spec,
            rollback_ref=rollback_ref,
            evidence_ref=ev,
        )
        self._plans[pid] = rp
        return rp

    def _build_patch_spec(self, diagnostic_report: DiagnosticReport) -> str:
        # Deterministic: same diagnosis -> same patch spec.
        return f"patch<{diagnostic_report.root_cause}>"

    def get(self, plan_id: str) -> RepairPlan:
        if plan_id not in self._plans:
            raise CodingLoopError(f"Unknown plan '{plan_id}'.")
        return self._plans[plan_id]

    def provenance(self, plan_id: str) -> dict:
        rp = self.get(plan_id)
        payload = (
            f"{rp.plan_id}|{rp.diagnostic_ref}|{rp.patch_spec}|"
            f"{rp.rollback_ref}|{rp.evidence_ref}"
        )
        return {
            "plan_id": rp.plan_id,
            "diagnostic_ref": rp.diagnostic_ref,
            "patch_spec": rp.patch_spec,
            "rollback_ref": rp.rollback_ref,
            "evidence_ref": rp.evidence_ref,
            "authority": rp.authority,
            "content_hash": _hash(payload),
        }
