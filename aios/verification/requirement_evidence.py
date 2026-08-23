"""TASK-155 — Requirement -> Evidence Mapping (M22).

Deterministic mapping of requirements to collected evidence with coverage
measurement. Fail-closed: a requirement with no provenance cannot be mapped;
UNKNOWN coverage is never promoted to PASS.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from aios.verification._common import VerificationError, _hash, _now


@dataclass(frozen=True)
class Requirement:
    requirement_id: str
    text: str
    source: str = "spec"

    def __post_init__(self) -> None:
        if not self.requirement_id:
            raise VerificationError("requirement_id must be non-empty")
        if not self.text:
            raise VerificationError("requirement text must be non-empty")


@dataclass(frozen=True)
class EvidenceLink:
    link_id: str
    requirement_ref: str
    evidence_ref: str
    coverage: float = 1.0

    def __post_init__(self) -> None:
        if not self.link_id:
            raise VerificationError("link_id must be non-empty")
        if not self.requirement_ref:
            raise VerificationError("requirement_ref must be non-empty")
        if not self.evidence_ref:
            raise VerificationError("evidence_ref must be non-empty")


@dataclass(frozen=True)
class MappingReport:
    report_id: str
    requirement_ref: str
    evidence_refs: tuple
    coverage_ratio: float
    status: str  # PASS | INSUFFICIENT | UNKNOWN


COVERAGE_THRESHOLD = 0.5


class RequirementEvidenceMapper:
    """Map a requirement to evidence and compute deterministic coverage."""

    def map_requirement(
        self,
        requirement: Requirement,
        evidence_refs: List[str],
        *,
        links: Optional[List[EvidenceLink]] = None,
    ) -> MappingReport:
        if not isinstance(requirement, Requirement):
            raise VerificationError("requirement must be a Requirement")
        if evidence_refs is None:
            raise VerificationError("evidence_refs must be provided")
        for ref in evidence_refs:
            if not ref:
                raise VerificationError("evidence_ref must be non-empty (provenance)")

        total = len(evidence_refs)
        # Coverage = fraction of provided evidence that is linked to this requirement.
        linked = 0
        if links:
            for lnk in links:
                if lnk.requirement_ref == requirement.requirement_id and lnk.evidence_ref in evidence_refs:
                    linked += 1
        coverage_ratio = (linked / total) if total else 0.0

        if total == 0:
            status = "UNKNOWN"
        elif coverage_ratio >= COVERAGE_THRESHOLD:
            status = "PASS"
        else:
            status = "INSUFFICIENT"

        report_id = _hash(f"{requirement.requirement_id}|{','.join(sorted(evidence_refs))}|{coverage_ratio:.4f}")
        return MappingReport(
            report_id=report_id,
            requirement_ref=requirement.requirement_id,
            evidence_refs=tuple(evidence_refs),
            coverage_ratio=coverage_ratio,
            status=status,
        )
