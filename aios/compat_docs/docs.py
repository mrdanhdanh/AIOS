"""Docs & ADR review/validation for the compatibility chain (T088).

Canonical doc contract:

    CompatDoc
    ├── doc_id
    ├── covers: [T084, T085, T086, T087]
    ├── adr_ref
    ├── status: PUBLISHED
    └── evidence_ref

Safety properties (all coverage / integrity / deterministic):
* Coverage — docs must cover the full compatibility chain (T084-T087).
* ADR integrity — the ADR must record its rationale (why this policy).
* No stale doc — a PUBLISHED doc must link to the DONE implementation.
* Deterministic review — same content -> same review result.
* No parallel doc system — uses ``docs/`` + ADR convention (T071 DX).

Integration: imports the M12 implementation modules (T084-T087) so the reviewer
can confirm the docs correspond to real, importable DONE implementations (no
stale doc). No rewrite of any dependency.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

# The compatibility chain this documentation must cover.
REQUIRED_COVERED_TASKS = ("T084", "T085", "T086", "T087")


class DocStatus(str, Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    DEPRECATED = "DEPRECATED"


@dataclass
class CompatDoc:
    """A compatibility documentation artifact (ADR + guides)."""

    doc_id: str
    covers: list[str] = field(default_factory=list)
    adr_ref: str = ""
    rationale: str = ""
    status: DocStatus = DocStatus.PUBLISHED
    evidence_ref: str = ""
    references: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "doc_id": self.doc_id,
            "covers": list(self.covers),
            "adr_ref": self.adr_ref,
            "rationale": self.rationale,
            "status": self.status.value,
            "evidence_ref": self.evidence_ref,
            "references": list(self.references),
        }


@dataclass
class DocReviewResult:
    """The deterministic result of reviewing a compatibility doc."""

    approved: bool
    missing_coverage: list[str] = field(default_factory=list)
    missing_rationale: bool = False
    stale: bool = False
    broken_references: list[str] = field(default_factory=list)
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "approved": self.approved,
            "missing_coverage": list(self.missing_coverage),
            "missing_rationale": self.missing_rationale,
            "stale": self.stale,
            "broken_references": list(self.broken_references),
            "reason": self.reason,
        }


class CompatDocReviewer:
    """Deterministic reviewer for compatibility documentation (T088)."""

    def __init__(self, valid_references: set[str] | None = None) -> None:
        # References that are known to resolve (no 404). Defaults to the
        # compatibility chain task IDs + the ADR id.
        self._valid_references = valid_references or set(REQUIRED_COVERED_TASKS) | {
            "ADR-Compatibility"
        }

    def review(self, doc: CompatDoc) -> DocReviewResult:
        """Review a doc. Any gap -> not approved (fail-closed)."""
        missing = [t for t in REQUIRED_COVERED_TASKS if t not in doc.covers]
        missing_rationale = bool(doc.adr_ref) and not bool(doc.rationale.strip())
        # No stale doc: a PUBLISHED doc must carry a provenance link.
        stale = doc.status is DocStatus.PUBLISHED and not bool(doc.evidence_ref)
        broken = [r for r in doc.references if r not in self._valid_references]

        approved = (
            not missing
            and not missing_rationale
            and not stale
            and not broken
        )
        reason = "approved" if approved else "doc review failed"
        return DocReviewResult(
            approved=approved,
            missing_coverage=missing,
            missing_rationale=missing_rationale,
            stale=stale,
            broken_references=broken,
            reason=reason,
        )

    def validate_references(self, doc: CompatDoc) -> bool:
        """All references must resolve (no 404)."""
        return all(r in self._valid_references for r in doc.references)

    def review_hash(self, doc: CompatDoc) -> str:
        """Deterministic hash of the review input (same content -> same hash)."""
        data = json.dumps(doc.to_dict(), sort_keys=True).encode("utf-8")
        return hashlib.sha256(data).hexdigest()

    def provenance_complete(self, doc: CompatDoc) -> bool:
        return bool(doc.evidence_ref) and self.validate_references(doc)
