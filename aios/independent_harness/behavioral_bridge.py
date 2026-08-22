"""Behavioral Conformance Bridge (TASK-106, M16).

Bridges behavioral conformance observations from an independent harness into
AIOS verification **without** replacing Core. The independent observation is
only *input*; ``conformance`` is decided by AIOS. An undefined observation is
INCONCLUSIVE and is never promoted to PASS (fail-closed, T078).

Reuses:
* Oracle (T105) — evidence bridge + authority boundary
* Foundation (T104) — registration + ingest boundary
* ``aios.behavioral.behavioral`` (BehaviorScenario, BehaviorSurface) — T089/T090
* ``aios.verification_integrity`` (VerdictClass) — T078
* ``aios.governance.evidence.store`` (EvidenceStore) — T001 Rule 5
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from aios.verification_integrity.integrity import VerdictClass

from .foundation import (
    EvidenceIngestBoundary,
    EvidencePayload,
    FoundationError,
    HarnessRegistry,
    PolicyAuthority,
)


@dataclass
class BehavioralConformanceReport:
    """Bridged behavioral conformance report.

    ``independent_observation`` is the harness input; ``conformance`` is decided
    by AIOS. ``authority`` is always ``aios``.
    """

    behavior_id: str
    independent_observation: str
    aios_expected: str
    conformance: bool
    evidence_ref: str
    authority: str = "aios"

    def to_dict(self) -> dict[str, Any]:
        return {
            "behavior_id": self.behavior_id,
            "independent_observation": self.independent_observation,
            "aios_expected": self.aios_expected,
            "conformance": self.conformance,
            "evidence_ref": self.evidence_ref,
            "authority": self.authority,
        }


class BehavioralConformanceBridge:
    """Bridges independent behavioral observations into AIOS conformance."""

    def __init__(
        self,
        registry: Optional[HarnessRegistry] = None,
        ingest: Optional[EvidenceIngestBoundary] = None,
    ) -> None:
        self._registry = registry or HarnessRegistry()
        self._ingest = ingest or EvidenceIngestBoundary(self._registry)

    def bridge(
        self,
        harness_id: str,
        behavior_id: str,
        independent_observation: str,
        aios_expected: str,
        task_id: str = "TASK-106",
        run_id: str = "",
    ) -> BehavioralConformanceReport:
        # Fail-closed: an undefined / empty observation is INCONCLUSIVE.
        if not independent_observation:
            return BehavioralConformanceReport(
                behavior_id=behavior_id,
                independent_observation=independent_observation,
                aios_expected=aios_expected,
                conformance=False,
                evidence_ref="",
                authority="aios",
            )
        # Bridge the observation evidence into AIOS via the foundation boundary.
        evidence_id = f"beh-ev-{behavior_id}"
        from aios.verification_integrity.integrity import sha256

        payload = EvidencePayload(
            evidence_id=evidence_id,
            task_id=task_id,
            run_id=run_id or evidence_id,
            producer=f"independent-behavioral:{harness_id}",
            type="behavior_observation",
            source=behavior_id,
            content=independent_observation,
            content_hash=sha256(independent_observation),
        )
        ingest_result = self._ingest.ingest(harness_id, payload)

        # AIOS decides conformance; observation cannot override (authority AIOS).
        conforms = (
            independent_observation == aios_expected and ingest_result.accepted
        )
        conformance = bool(
            PolicyAuthority.reject_override(independent_observation, conforms)
        )
        return BehavioralConformanceReport(
            behavior_id=behavior_id,
            independent_observation=independent_observation,
            aios_expected=aios_expected,
            conformance=conformance,
            evidence_ref=evidence_id if ingest_result.accepted else "",
            authority="aios",
        )
