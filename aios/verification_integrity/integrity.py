"""Verification Integrity — fail-closed integrity gate (TASK-078, M11).

Provides:
* ``IntegrityReport`` — structured integrity result for an evidence/verdict.
* ``VerifierLock`` — locks verifier version + config hash per run.
* ``IntegrityChecker`` — verifies evidence hash (tamper detection), verifier
  lock, fail-closed verdict (UNKNOWN/INCONCLUSIVE -> not PASS), and provenance
  completeness.

Fail-closed: any unverifiable / tampered / inconclusive state -> reject (never
promote to PASS). Deterministic: same evidence + same verifier -> same verdict.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional, Sequence


class IntegrityError(Exception):
    """Raised when an integrity invariant is violated (fail-closed)."""


class VerdictClass(str, Enum):
    """Normalized verdict classes understood by the integrity gate."""

    PASS = "pass"
    FAIL = "fail"
    UNKNOWN = "unknown"
    INCONCLUSIVE = "inconclusive"

    @classmethod
    def from_any(cls, verdict: Any) -> "VerdictClass":
        """Normalize a verdict from harness/evaluation into a VerdictClass."""
        if verdict is None:
            return cls.UNKNOWN
        text = str(verdict).strip().lower()
        if text in ("pass", "passed"):
            return cls.PASS
        if text in ("fail", "failed"):
            return cls.FAIL
        if text in ("unknown",):
            return cls.UNKNOWN
        if text in ("inconclusive", "inconclusive", "warn", "warning"):
            return cls.INCONCLUSIVE
        # Anything not explicitly PASS/FAIL is treated as UNKNOWN (fail-closed).
        return cls.UNKNOWN


def sha256(content: str | bytes) -> str:
    """Return hex sha256 of content (utf-8 encoded if str)."""
    if isinstance(content, str):
        content = content.encode("utf-8")
    return hashlib.sha256(content).hexdigest()


@dataclass
class VerifierLock:
    """Locks verifier identity + config for a single evaluation run."""

    verifier_version: str
    verifier_config: str = ""

    def config_hash(self) -> str:
        return sha256(f"{self.verifier_version}|{self.verifier_config}")

    def to_dict(self) -> dict[str, Any]:
        return {
            "verifier_version": self.verifier_version,
            "verifier_config_hash": self.config_hash(),
        }


@dataclass
class IntegrityReport:
    """Result of an integrity evaluation for one evidence/verdict pair."""

    evidence_id: str
    content_hash: str
    verifier_version: str
    verifier_config_hash: str
    tampered: bool
    verdict_class: str
    promoted_to_pass: bool
    provenance_complete: bool
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "content_hash": self.content_hash,
            "verifier_version": self.verifier_version,
            "verifier_config_hash": self.verifier_config_hash,
            "tampered": self.tampered,
            "verdict_class": self.verdict_class,
            "promoted_to_pass": self.promoted_to_pass,
            "provenance_complete": self.provenance_complete,
            "notes": list(self.notes),
        }


class IntegrityChecker:
    """Fail-closed integrity gate over evidence + verdicts."""

    def __init__(self) -> None:
        # Track locked verifiers per run to detect mid-run version drift.
        self._locks: dict[str, VerifierLock] = {}

    # -- evidence integrity / tamper detection --------------------------------

    def verify_evidence_hash(self, evidence_id: str, content: str | bytes,
                             expected_hash: str) -> bool:
        """Return True iff computed hash matches expected (no tamper)."""
        return sha256(content) == expected_hash

    def is_tampered(self, content: str | bytes, expected_hash: str) -> bool:
        """True when content hash differs from expected (tamper detected)."""
        return sha256(content) != expected_hash

    # -- verifier lock -------------------------------------------------------

    def lock_verifier(self, run_id: str, version: str, config: str = "") -> VerifierLock:
        lock = VerifierLock(verifier_version=version, verifier_config=config)
        self._locks[run_id] = lock
        return lock

    def verifier_changed(self, run_id: str, version: str, config: str = "") -> bool:
        """True if the supplied verifier differs from the locked one for run."""
        locked = self._locks.get(run_id)
        if locked is None:
            return False
        return locked.config_hash() != VerifierLock(version, config).config_hash()

    # -- fail-closed verdict --------------------------------------------------

    @staticmethod
    def promotes_to_pass(verdict: Any) -> bool:
        """Fail-closed: only an explicit PASS promotes; everything else -> False."""
        return VerdictClass.from_any(verdict) is VerdictClass.PASS

    # -- provenance -----------------------------------------------------------

    @staticmethod
    def provenance_complete(chain: Optional[Sequence[Any]]) -> bool:
        """Provenance is complete iff every link has a non-empty id."""
        if not chain:
            return False
        for link in chain:
            link_id = getattr(link, "evidence_id", None) or getattr(link, "id", None)
            if not link_id:
                return False
        return True

    # -- combined evaluation --------------------------------------------------

    def evaluate(
        self,
        evidence_id: str,
        content: str | bytes,
        expected_hash: str,
        verifier_version: str,
        verifier_config: str,
        verdict: Any,
        provenance: Optional[Sequence[Any]] = None,
    ) -> IntegrityReport:
        """Produce an :class:`IntegrityReport` (fail-closed)."""
        tampered = self.is_tampered(content, expected_hash)
        vclass = VerdictClass.from_any(verdict)
        # Fail-closed: tampered OR not-explicitly-PASS -> never promote.
        promoted = (not tampered) and (vclass is VerdictClass.PASS)
        prov_ok = self.provenance_complete(provenance)
        notes: list[str] = []
        if tampered:
            notes.append("evidence hash mismatch -> reject (tamper)")
        if vclass in (VerdictClass.UNKNOWN, VerdictClass.INCONCLUSIVE):
            notes.append(f"verdict {vclass.value} -> not promoted (fail-closed)")
        if not prov_ok:
            notes.append("provenance chain incomplete")
        return IntegrityReport(
            evidence_id=evidence_id,
            content_hash=sha256(content),
            verifier_version=verifier_version,
            verifier_config_hash=VerifierLock(verifier_version, verifier_config).config_hash(),
            tampered=tampered,
            verdict_class=vclass.value,
            promoted_to_pass=promoted,
            provenance_complete=prov_ok,
            notes=notes,
        )
