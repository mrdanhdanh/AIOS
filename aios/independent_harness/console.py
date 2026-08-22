"""Management Console / Independent Harness Integration (TASK-108, M16).

Integrates independent harness status into the management console so an operator
can view / manage independent verification **without** replacing Core. The
console only *displays*; operator actions go through the API/runtime and are
policy-gated. AIOS retains authority (``aios_authority_flag`` is always ``aios``).

Reuses:
* Oracle (T105) + Foundation (T104) + Bridges (T106/T107)
* ``aios.dashboard.views`` (view models) — T042/T072/T018
* ``aios.api`` (routers) — T017
* ``aios.verification_integrity`` (VerdictClass) — T078
* ``aios.governance.evidence.store`` (EvidenceStore) — T001 Rule 5
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from .behavioral_bridge import BehavioralConformanceReport
from .foundation import PolicyAuthority
from .oracle import OracleResult
from .permission_sandbox_bridge import PermissionSandboxReport


@dataclass
class ConsoleHarnessView:
    """Aggregated independent-harness status view for an operator."""

    console_id: str
    harness_status: str
    independent_results_summary: dict[str, Any]
    aios_authority_flag: str = "aios"
    operator_action: str = "view-only"
    evidence_ref: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "console_id": self.console_id,
            "harness_status": self.harness_status,
            "independent_results_summary": dict(self.independent_results_summary),
            "aios_authority_flag": self.aios_authority_flag,
            "operator_action": self.operator_action,
            "evidence_ref": self.evidence_ref,
        }


class ManagementConsoleIntegration:
    """Aggregates independent harness verdicts into a console view.

    The console never decides policy; operator actions are routed through the
    API/runtime and must pass a policy gate.
    """

    def __init__(self) -> None:
        self._last_view: Optional[ConsoleHarnessView] = None

    def aggregate(
        self,
        console_id: str,
        harness_id: str,
        oracle: Optional[OracleResult] = None,
        behavioral: Optional[BehavioralConformanceReport] = None,
        permission: Optional[PermissionSandboxReport] = None,
    ) -> ConsoleHarnessView:
        summary: dict[str, Any] = {
            "oracle": oracle.to_dict() if oracle else None,
            "behavioral": behavioral.to_dict() if behavioral else None,
            "permission": permission.to_dict() if permission else None,
        }
        # Overall harness status is fail-closed: any non-pass -> "degraded".
        statuses = []
        if oracle is not None:
            statuses.append(oracle.aios_policy_verdict)
        if behavioral is not None:
            statuses.append("pass" if behavioral.conformance else "fail")
        if permission is not None:
            statuses.append("pass" if permission.aios_policy_result == "allow" else "fail")
        if not statuses:
            harness_status = "no-data"
        elif all(s == "pass" for s in statuses):
            harness_status = "healthy"
        else:
            harness_status = "degraded"

        evidence_ref = ""
        for rep in (oracle, behavioral, permission):
            if rep is not None and getattr(rep, "evidence_ref", ""):
                evidence_ref = rep.evidence_ref
                break

        view = ConsoleHarnessView(
            console_id=console_id,
            harness_status=harness_status,
            independent_results_summary=summary,
            aios_authority_flag="aios",
            operator_action="view-only",
            evidence_ref=evidence_ref,
        )
        self._last_view = view
        return view

    def request_operator_action(
        self, action: str, policy_gate_allowed: bool
    ) -> dict[str, Any]:
        """Operator action must be policy-gated (never bypasses AIOS policy).

        Returns a descriptor; the actual mutation is performed by the API/runtime
        after this gate passes. Console itself holds no authority.
        """
        if not PolicyAuthority.is_aios_authoritative():
            return {"action": action, "dispatched": False, "reason": "authority not aios"}
        if not policy_gate_allowed:
            return {
                "action": action,
                "dispatched": False,
                "reason": "policy gate denied (fail-closed)",
            }
        # Console only dispatches; AIOS runtime executes the action.
        return {
            "action": action,
            "dispatched": True,
            "via": "api/runtime",
            "authority": "aios",
        }
