"""Behavioral Spec + ADR-0008 review/validation (TASK-093, M13).

Canonical spec/ADR contract:

    BehavioralDoc
    ├── doc_id
    ├── covers: [T089, T090, T091, T092, T093]
    ├── adr_ref: ADR-0008
    ├── status: PUBLISHED
    └── evidence_ref

Safety properties (all coverage / integrity / deterministic / no-stale):
* Coverage — the doc must cover the full M13 chain (T089-T093).
* ADR integrity — ADR-0008 must record its rationale (why this policy).
* No stale doc — referenced modules/docs must exist (no 404, no drift).
* Deterministic review — same content -> same review result.
* No parallel doc system — uses ``docs/`` + ADR convention (T071 DX).

Integration: imports nothing from runtime; validates references against the
repository tree (``aios/...`` modules + ``docs/...`` files). No rewrite of any
dependency.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

# The full M13 chain that a behavioral spec doc must cover.
M13_TASKS = {"TASK-089", "TASK-090", "TASK-091", "TASK-092", "TASK-093"}


class DocStatus(str, Enum):
    PUBLISHED = "published"
    DRAFT = "draft"


@dataclass
class BehavioralDoc:
    """A published behavioral spec / ADR document."""

    doc_id: str
    covers: list[str]
    adr_ref: str
    status: DocStatus
    references: list[str]  # repo-relative paths (aios/... or docs/...)
    rationale: str = ""
    evidence_ref: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "doc_id": self.doc_id,
            "covers": list(self.covers),
            "adr_ref": self.adr_ref,
            "status": self.status.value,
            "references": list(self.references),
            "rationale": self.rationale,
            "evidence_ref": self.evidence_ref,
        }


@dataclass
class DocReviewResult:
    """Fail-closed review result for a behavioral spec doc."""

    doc_id: str
    covers_m13: bool
    adr_has_rationale: bool
    no_stale: bool
    links_valid: bool
    deterministic: bool
    passed: bool
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "doc_id": self.doc_id,
            "covers_m13": self.covers_m13,
            "adr_has_rationale": self.adr_has_rationale,
            "no_stale": self.no_stale,
            "links_valid": self.links_valid,
            "deterministic": self.deterministic,
            "passed": self.passed,
            "notes": list(self.notes),
        }


class BehavioralDocReviewer:
    """Reviews a behavioral spec doc for coverage, ADR integrity and staleness."""

    def __init__(self, repo_root: Path | None = None) -> None:
        # aios/behavioral_docs/docs.py -> parents[2] == repo root.
        self._root = repo_root or Path(__file__).resolve().parents[2]

    # -- reference resolution ------------------------------------------------

    def _resolve(self, ref: str) -> Path:
        return (self._root / ref).resolve()

    def _exists(self, ref: str) -> bool:
        try:
            return self._resolve(ref).exists()
        except (OSError, ValueError):
            return False

    # -- review ---------------------------------------------------------------

    def review(self, doc: BehavioralDoc) -> DocReviewResult:
        """Same content -> same result (deterministic, pure)."""
        notes: list[str] = []

        covers_m13 = M13_TASKS.issubset(set(doc.covers))
        if not covers_m13:
            missing = M13_TASKS - set(doc.covers)
            notes.append(f"doc does not cover M13 tasks: {sorted(missing)}")

        adr_has_rationale = bool(doc.rationale) and "ADR-0008" in doc.adr_ref
        if not adr_has_rationale:
            notes.append("ADR-0008 rationale missing or adr_ref not set")

        # No stale: referenced implementation modules / docs must exist.
        no_stale = all(self._exists(ref) for ref in doc.references)
        if not no_stale:
            missing_refs = [r for r in doc.references if not self._exists(r)]
            notes.append(f"stale/404 references: {missing_refs}")

        # Links valid: every reference resolves to an existing path.
        links_valid = no_stale

        passed = covers_m13 and adr_has_rationale and no_stale and links_valid
        return DocReviewResult(
            doc_id=doc.doc_id,
            covers_m13=covers_m13,
            adr_has_rationale=adr_has_rationale,
            no_stale=no_stale,
            links_valid=links_valid,
            deterministic=True,
            passed=passed,
            notes=notes,
        )

    # -- determinism / provenance --------------------------------------------

    def provenance_complete(self, doc: BehavioralDoc) -> bool:
        return bool(doc.evidence_ref)

    def review_hash(self, result: DocReviewResult) -> str:
        """Deterministic hash (same result -> same hash)."""
        payload = {
            "doc_id": result.doc_id,
            "covers_m13": result.covers_m13,
            "adr_has_rationale": result.adr_has_rationale,
            "no_stale": result.no_stale,
            "links_valid": result.links_valid,
            "passed": result.passed,
            "notes": sorted(result.notes),
        }
        data = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hashlib.sha256(data).hexdigest()
