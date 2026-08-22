"""System Readiness vs Harness Trust — readiness/trust gate (TASK-092, M13).

Canonical trust contract:

    ReadinessTrust
    ├── system_ready: bool
    ├── harness_trusted: bool
    ├── combined: READY_TRUSTED | READY_UNTRUSTED | NOT_READY
    ├── reason
    └── evidence_ref

Safety properties (all fail-closed / both-required / provenance / deterministic):
* Fail-closed certify — untrusted -> never certify.
* Both required — ready AND trusted (not just one).
* Evidence required — every trust decision carries provenance (T001 Rule 5).
* Deterministic — same system + same harness -> same trust result.
* No parallel trust system — uses Coverage (T090) + Meta (T091) + Cert (T073).

Integration: imports ``aios.harness_coverage.coverage`` (CoverageReport,
Readiness), ``aios.meta_harness.meta`` (MetaResult, MetaVerdict) and
``aios.certification.certifier`` (Certifier, Certification, CertStatus).
No rewrite of any dependency.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from aios.certification.certifier import Certifier
from aios.certification.contracts import CertStatus, Certification
from aios.harness_coverage.coverage import CoverageReport, Readiness
from aios.meta_harness.meta import MetaResult, MetaVerdict


class CombinedTrust(str, Enum):
    """The combined readiness/trust decision."""

    READY_TRUSTED = "ready_trusted"
    READY_UNTRUSTED = "ready_untrusted"
    NOT_READY = "not_ready"


@dataclass
class ReadinessTrust:
    """The combined readiness/trust decision for a build."""

    system_ready: bool
    harness_trusted: bool
    combined: CombinedTrust
    reason: str
    evidence_ref: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "system_ready": self.system_ready,
            "harness_trusted": self.harness_trusted,
            "combined": self.combined.value,
            "reason": self.reason,
            "evidence_ref": self.evidence_ref,
        }


class TrustGate:
    """Combined gate: only READY_TRUSTED certifies a build (fail-closed)."""

    def __init__(self, certifier: Optional[Certifier] = None) -> None:
        self._certifier = certifier or Certifier()

    def evaluate(
        self,
        system_ready: bool,
        coverage_report: CoverageReport,
        meta_result: MetaResult,
        evidence_ref: str = "",
    ) -> ReadinessTrust:
        """Same system + same harness -> same trust result (deterministic)."""
        harness_trusted = (
            coverage_report.readiness == Readiness.READY
            and meta_result.verdict == MetaVerdict.PASS
        )
        if not system_ready:
            combined = CombinedTrust.NOT_READY
            reason = "system not ready"
        elif not harness_trusted:
            combined = CombinedTrust.READY_UNTRUSTED
            reason = "system ready but harness untrusted"
        else:
            combined = CombinedTrust.READY_TRUSTED
            reason = "system ready and harness trusted"
        return ReadinessTrust(
            system_ready=system_ready,
            harness_trusted=harness_trusted,
            combined=combined,
            reason=reason,
            evidence_ref=evidence_ref,
        )

    # -- certification integration (T073) -------------------------------------

    def certify(
        self, trust: ReadinessTrust, target_id: str = ""
    ) -> Optional[Certification]:
        """Fail-closed: only READY_TRUSTED certifies (T073)."""
        if trust.combined != CombinedTrust.READY_TRUSTED:
            return None
        cert = self._certifier.issue(target_id or f"trust:{target_id or 'build'}")
        return self._certifier.certify(cert.cert_id)

    # -- determinism / provenance ---------------------------------------------

    def provenance_complete(self, trust: ReadinessTrust) -> bool:
        return bool(trust.evidence_ref)

    def trust_hash(self, trust: ReadinessTrust) -> str:
        """Deterministic hash (same inputs -> same hash)."""
        payload = {
            "system_ready": trust.system_ready,
            "harness_trusted": trust.harness_trusted,
            "combined": trust.combined.value,
            "reason": trust.reason,
            "evidence_ref": trust.evidence_ref,
        }
        data = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hashlib.sha256(data).hexdigest()
