"""Compatibility Conformance — runner, report, fail-closed gate (T087).

Canonical conformance contract:

    ConformanceReport
    ├── target_version: 1.x
    ├── baseline: 1.0 (T084)
    ├── checks_passed: [api, schema, event, version, contract]
    ├── issued_at
    └── evidence_ref

Safety properties (all fail-closed / evidence / deterministic):
* Fail-closed conform — one check FAIL -> not conformant.
* Evidence required — the report carries full provenance.
* Deterministic — same build + same suite -> same result.
* No parallel conformer — uses Certification (T073) + Contract (T064).

Integration: imports ``aios.versioning.versioning`` (T084) for the compatibility
matrix, ``aios.backward_compat.backward`` (T086) for the compat checks,
``aios.contracts.contract`` (T064) for the freeze status, and
``aios.certification.certifier`` (T073) for issuing a conformance certificate.
No rewrite of any dependency.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from aios.backward_compat.backward import (
    BackwardCompatChecker,
    CompatCheck,
    CompatSurface,
)
from aios.certification.certifier import Certifier
from aios.contracts.contract import Contract, ContractStatus
from aios.versioning.versioning import CompatibilityMatrix, VersionBaseline

BASELINE_VERSION = "1.0.0"


class ConformanceCheck(str, Enum):
    """The five checks a build must pass to be conformant."""

    API = "api"
    SCHEMA = "schema"
    EVENT = "event"
    VERSION = "version"
    CONTRACT = "contract"

    @classmethod
    def all(cls) -> list["ConformanceCheck"]:
        return [cls.API, cls.SCHEMA, cls.EVENT, cls.VERSION, cls.CONTRACT]


@dataclass
class ConformanceReport:
    """Evidence-backed conformance report for a target build."""

    target_version: str
    baseline: str = BASELINE_VERSION
    checks_passed: list[str] = field(default_factory=list)
    issued_at: float = field(default_factory=time.time)
    evidence_ref: str = ""
    conformant: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "target_version": self.target_version,
            "baseline": self.baseline,
            "checks_passed": list(self.checks_passed),
            "issued_at": self.issued_at,
            "evidence_ref": self.evidence_ref,
            "conformant": self.conformant,
        }


class ConformanceRunner:
    """Runs the full conformance suite and emits a fail-closed report."""

    def __init__(self, baseline: VersionBaseline | None = None) -> None:
        self._baseline = baseline or VersionBaseline()
        self._checker = BackwardCompatChecker()

    # -- individual checks ----------------------------------------------------

    def _check_surface(self, surface: CompatSurface, target_version: str,
                       evidence_ref: str) -> tuple[bool, str]:
        res = self._checker.check(
            CompatCheck(surface=surface, provider_version=target_version,
                        evidence_ref=evidence_ref)
        )
        return res.compatible and not res.blocked, res.reason

    def _check_version(self, target_version: str) -> tuple[bool, str]:
        ok = CompatibilityMatrix.is_compatible(self._baseline.baseline_version,
                                               target_version)
        return ok, ("version compatible" if ok
                    else "target version not backward-compatible with baseline")

    def _check_contract(self, contracts: list[Contract] | None) -> tuple[bool, str]:
        if not contracts:
            return False, "no contracts provided; cannot prove freeze"
        unfrozen = [c.name for c in contracts if c.status is not ContractStatus.FROZEN]
        if unfrozen:
            return False, f"contracts not frozen: {unfrozen}"
        return True, "all contracts frozen"

    # -- full run -------------------------------------------------------------

    def run(self, target_version: str,
            contracts: list[Contract] | None = None,
            evidence_ref: str = "") -> ConformanceReport:
        """Run all five checks. Any FAIL -> not conformant (fail-closed)."""
        checks: dict[ConformanceCheck, tuple[bool, str]] = {}

        api_ok, api_reason = self._check_surface(
            CompatSurface.API, target_version, f"{evidence_ref}:api")
        sch_ok, sch_reason = self._check_surface(
            CompatSurface.SCHEMA, target_version, f"{evidence_ref}:schema")
        evt_ok, evt_reason = self._check_surface(
            CompatSurface.EVENT, target_version, f"{evidence_ref}:event")
        ver_ok, ver_reason = self._check_version(target_version)
        con_ok, con_reason = self._check_contract(contracts)

        checks[ConformanceCheck.API] = (api_ok, api_reason)
        checks[ConformanceCheck.SCHEMA] = (sch_ok, sch_reason)
        checks[ConformanceCheck.EVENT] = (evt_ok, evt_reason)
        checks[ConformanceCheck.VERSION] = (ver_ok, ver_reason)
        checks[ConformanceCheck.CONTRACT] = (con_ok, con_reason)

        passed = [c.value for c, (ok, _) in checks.items() if ok]
        conformant = len(passed) == len(ConformanceCheck.all())
        return ConformanceReport(
            target_version=target_version,
            baseline=self._baseline.baseline_version,
            checks_passed=passed,
            evidence_ref=evidence_ref,
            conformant=conformant,
        )

    # -- gate -----------------------------------------------------------------

    def issue(self, report: ConformanceReport) -> bool:
        """Fail-closed gate: only a fully conformant report is issued."""
        return report.conformant

    # -- certification integration (T073) ------------------------------------

    def certify(self, report: ConformanceReport,
                certifier: Certifier | None = None,
                target_id: str = "") -> Optional[Any]:
        """Issue a conformance certificate only when conformant (T073)."""
        if not report.conformant:
            return None
        certifier = certifier or Certifier()
        cert = certifier.issue(target_id or f"conformance:{report.target_version}")
        # ``issue`` only creates the record; ``certify`` marks it CERTIFIED
        # (fail-closed: only a conformant build reaches CERTIFIED status).
        return certifier.certify(cert.cert_id)

    # -- determinism / provenance --------------------------------------------

    def report_hash(self, report: ConformanceReport) -> str:
        """Deterministic hash of the report (same build + suite -> same hash).

        ``issued_at`` is a wall-clock timestamp and is excluded so the hash is
        stable for the same build + suite.
        """
        payload = {
            "target_version": report.target_version,
            "baseline": report.baseline,
            "checks_passed": sorted(report.checks_passed),
            "evidence_ref": report.evidence_ref,
            "conformant": report.conformant,
        }
        data = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hashlib.sha256(data).hexdigest()

    def provenance_complete(self, report: ConformanceReport) -> bool:
        return bool(report.evidence_ref) and report.conformant
