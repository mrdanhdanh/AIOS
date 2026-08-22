"""Permission + Sandbox Bridge (TASK-107, M16).

Bridges permission / sandbox checks from an independent harness into AIOS
verification **without** replacing Core. The independent result is only *input*;
``aios_policy_result`` is decided by AIOS. An undefined result is INCONCLUSIVE
and never promoted to PASS (fail-closed, T078).

Reuses:
* Oracle (T105) / Foundation (T104) — evidence bridge + authority boundary
* ``aios.identity.contracts`` (Permission, Principal) — T035/T113
* ``aios.security.contracts`` (SandboxConfig, NetworkPolicy) — T040
* ``aios.security.isolation`` (IsolationManager) — T040
* ``aios.verification_integrity`` (VerdictClass) — T078
* ``aios.governance.evidence.store`` (EvidenceStore) — T001 Rule 5
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from aios.identity.contracts import Permission
from aios.security.contracts import NetworkPolicy, SandboxConfig
from aios.security.isolation import IsolationManager
from aios.verification_integrity.integrity import VerdictClass

from .foundation import (
    EvidenceIngestBoundary,
    EvidencePayload,
    FoundationError,
    HarnessRegistry,
    PolicyAuthority,
)


@dataclass
class PermissionSandboxReport:
    """Bridged permission + sandbox report.

    ``independent_result`` is the harness input; ``aios_policy_result`` is the
    authoritative AIOS decision. ``authority`` is always ``aios``.
    """

    check_id: str
    permission_ref: str
    sandbox_ref: str
    independent_result: str
    aios_policy_result: str
    evidence_ref: str
    authority: str = "aios"

    def to_dict(self) -> dict[str, Any]:
        return {
            "check_id": self.check_id,
            "permission_ref": self.permission_ref,
            "sandbox_ref": self.sandbox_ref,
            "independent_result": self.independent_result,
            "aios_policy_result": self.aios_policy_result,
            "evidence_ref": self.evidence_ref,
            "authority": self.authority,
        }


class PermissionSandboxBridge:
    """Bridges independent permission/sandbox checks into AIOS policy results."""

    def __init__(
        self,
        registry: Optional[HarnessRegistry] = None,
        ingest: Optional[EvidenceIngestBoundary] = None,
        isolation: Optional[IsolationManager] = None,
    ) -> None:
        self._registry = registry or HarnessRegistry()
        self._ingest = ingest or EvidenceIngestBoundary(self._registry)
        self._isolation = isolation or IsolationManager()

    def bridge(
        self,
        harness_id: str,
        check_id: str,
        permission_ref: str,
        sandbox_ref: str,
        independent_result: str,
        task_id: str = "TASK-107",
        run_id: str = "",
    ) -> PermissionSandboxReport:
        # Fail-closed: an undefined result is INCONCLUSIVE -> not promoted.
        if not independent_result:
            return PermissionSandboxReport(
                check_id=check_id,
                permission_ref=permission_ref,
                sandbox_ref=sandbox_ref,
                independent_result=independent_result,
                aios_policy_result="deny",
                evidence_ref="",
                authority="aios",
            )
        # Bridge the independent result evidence into AIOS via foundation boundary.
        evidence_id = f"perm-ev-{check_id}"
        from aios.verification_integrity.integrity import sha256

        payload = EvidencePayload(
            evidence_id=evidence_id,
            task_id=task_id,
            run_id=run_id or evidence_id,
            producer=f"independent-permission:{harness_id}",
            type="permission_sandbox_check",
            source=f"{permission_ref}|{sandbox_ref}",
            content=independent_result,
            content_hash=sha256(independent_result),
        )
        ingest_result = self._ingest.ingest(harness_id, payload)

        # AIOS decides the policy result; independent result cannot override.
        # AIOS authoritative result: pass only if independent=pass AND provenance
        # admitted AND the referenced sandbox/permission exist in AIOS isolation.
        aios_pass = (
            VerdictClass.from_any(independent_result) is VerdictClass.PASS
            and ingest_result.accepted
            and self._isolation.get_sandbox(sandbox_ref) is not None
        )
        aios_result = "allow" if aios_pass else "deny"
        aios_policy_result = str(
            PolicyAuthority.reject_override(independent_result, aios_result)
        )
        return PermissionSandboxReport(
            check_id=check_id,
            permission_ref=permission_ref,
            sandbox_ref=sandbox_ref,
            independent_result=independent_result,
            aios_policy_result=aios_policy_result,
            evidence_ref=evidence_id if ingest_result.accepted else "",
            authority="aios",
        )
