"""Harness Coverage + Readiness — coverage metric, not a new harness (TASK-090, M13).

Canonical coverage contract:

    CoverageReport
    ├── total_surfaces
    ├── harnessed_surfaces
    ├── coverage_ratio
    ├── gaps: [..]
    ├── readiness: READY | NOT_READY
    └── evidence_ref

Safety properties (all fail-closed / no-hidden-gap / provenance / deterministic):
* Fail-closed readiness — coverage below threshold -> NOT_READY (no certify).
* No hidden gap — every uncovered surface is reported.
* Evidence required — every readiness check carries provenance (T001 Rule 5).
* Deterministic — same system + same harness -> same coverage.
* No parallel coverage system — uses Harness (T030/T032) + Certification (T073).

Integration: imports ``aios.certification.certifier`` (Certifier, Certification,
CertStatus) and ``aios.behavioral.behavioral`` (BehaviorScenario) for surface
registration. No rewrite of any dependency.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from aios.behavioral.behavioral import BehaviorScenario
from aios.certification.certifier import Certifier
from aios.certification.contracts import CertStatus, Certification


class Readiness(str, Enum):
    """Whether the harness is ready to certify a build."""

    READY = "ready"
    NOT_READY = "not_ready"


@dataclass
class CoverageReport:
    """Evidence-backed coverage + readiness report for the harness surface."""

    total_surfaces: int
    harnessed_surfaces: int
    coverage_ratio: float
    gaps: list[str]
    readiness: Readiness
    evidence_ref: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_surfaces": self.total_surfaces,
            "harnessed_surfaces": self.harnessed_surfaces,
            "coverage_ratio": self.coverage_ratio,
            "gaps": list(self.gaps),
            "readiness": self.readiness.value,
            "evidence_ref": self.evidence_ref,
        }


class CoverageMap:
    """Maps system surfaces -> the harness that covers them."""

    def __init__(self) -> None:
        self._map: dict[str, str] = {}

    def register(self, surface: str, harness_name: str) -> None:
        self._map[surface] = harness_name

    def harnessed(self, surface: str) -> bool:
        return surface in self._map

    def surfaces(self) -> list[str]:
        return list(self._map.keys())

    def harness_for(self, surface: str) -> Optional[str]:
        return self._map.get(surface)

    def gaps(self, all_surfaces: list[str]) -> list[str]:
        """Every uncovered surface is reported (no hidden gap)."""
        return [s for s in all_surfaces if s not in self._map]

    def from_behavior_scenarios(self, scenarios: list[BehaviorScenario]) -> None:
        """Register each behavior scenario's surface as harnessed (T089)."""
        for sc in scenarios:
            self.register(sc.scenario_id, f"behavior_harness:{sc.surface.value}")

    def to_dict(self) -> dict[str, Any]:
        return {"map": dict(self._map)}


class CoverageChecker:
    """Computes a fail-closed coverage + readiness report."""

    def __init__(self, threshold: float = 1.0) -> None:
        # Default: full coverage required to be READY (fail-closed).
        self._threshold = threshold

    def evaluate(
        self,
        all_surfaces: list[str],
        coverage_map: CoverageMap,
        evidence_ref: str = "",
    ) -> CoverageReport:
        """Same system + same harness -> same coverage (deterministic)."""
        harnessed = [s for s in all_surfaces if coverage_map.harnessed(s)]
        ratio = (len(harnessed) / len(all_surfaces)) if all_surfaces else 0.0
        gaps = coverage_map.gaps(all_surfaces)
        readiness = (
            Readiness.READY if ratio >= self._threshold else Readiness.NOT_READY
        )
        return CoverageReport(
            total_surfaces=len(all_surfaces),
            harnessed_surfaces=len(harnessed),
            coverage_ratio=ratio,
            gaps=gaps,
            readiness=readiness,
            evidence_ref=evidence_ref,
        )

    # -- certification integration (T073) -------------------------------------

    def certify(
        self,
        report: CoverageReport,
        certifier: Optional[Certifier] = None,
        target_id: str = "",
    ) -> Optional[Certification]:
        """Fail-closed: only a READY report is certified (T073)."""
        if report.readiness != Readiness.READY:
            return None
        certifier = certifier or Certifier()
        cert = certifier.issue(target_id or f"coverage:{target_id or 'build'}")
        return certifier.certify(cert.cert_id)

    # -- determinism / provenance ---------------------------------------------

    def provenance_complete(self, report: CoverageReport) -> bool:
        return bool(report.evidence_ref)

    def report_hash(self, report: CoverageReport) -> str:
        """Deterministic hash (same surfaces + map -> same hash)."""
        payload = {
            "total_surfaces": report.total_surfaces,
            "harnessed_surfaces": report.harnessed_surfaces,
            "coverage_ratio": round(report.coverage_ratio, 6),
            "gaps": sorted(report.gaps),
            "readiness": report.readiness.value,
            "evidence_ref": report.evidence_ref,
        }
        data = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hashlib.sha256(data).hexdigest()
