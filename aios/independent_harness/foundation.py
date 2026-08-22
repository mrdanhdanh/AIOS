"""Independent Harness Integration Foundation (TASK-104, M16).

Defines the adapter contract, registration (immutable ``harness_id``, T001
Rule 1), the evidence ingest boundary (fail-closed, provenance via T078/T001),
and the policy authority boundary (AIOS always authoritative).

This is the **foundation** of M16 — it is *not* a new harness. It reuses:
* ``aios.harness.contracts`` (HarnessSpec, RunResult, Assertion) — T030/T032
* ``aios.verification_integrity`` (IntegrityChecker, sha256, VerdictClass) — T078
* ``aios.governance.evidence.store`` (EvidenceStore, Evidence) — T001 Rule 5

Safety properties (all fail-closed / provenance / deterministic / authority):
* Fail-closed ingest — evidence missing provenance/hash -> reject (T078).
* Authority stays in AIOS — independent harness cannot override policy verdict.
* Evidence required — every ingest carries provenance (T001 Rule 5).
* Deterministic — same adapter + same input -> same ingest result.
* No parallel authority system — reuses Harness + Integrity + Evidence.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from aios.governance.evidence.store import Evidence, EvidenceStore
from aios.verification_integrity import IntegrityChecker
from aios.verification_integrity.integrity import VerdictClass, sha256


class FoundationError(Exception):
    """Raised on foundation contract or lifecycle errors (fail-closed)."""


class HarnessType(str, Enum):
    """Where the independent harness lives relative to AIOS."""

    EXTERNAL = "external"
    THIRD_PARTY = "third-party"
    SEPARATE = "separate"


@dataclass(frozen=True)
class IndependentHarnessAdapter:
    """Contract every independent harness must implement to connect to AIOS.

    ``harness_id`` is immutable (T001 Rule 1). ``policy_authority`` is always
    ``aios`` — the independent harness only supplies input, never policy.
    """

    harness_id: str
    harness_type: HarnessType
    source: str
    supported_checks: list[str] = field(default_factory=list)
    evidence_format: str = "aios-evidence-v1"
    policy_authority: str = "aios"

    def to_dict(self) -> dict[str, Any]:
        return {
            "harness_id": self.harness_id,
            "harness_type": self.harness_type.value,
            "source": self.source,
            "supported_checks": list(self.supported_checks),
            "evidence_format": self.evidence_format,
            "policy_authority": self.policy_authority,
        }

    def supports(self, check: str) -> bool:
        return check in self.supported_checks


class HarnessRegistry:
    """Registers independent harness adapters with immutable ``harness_id``.

    Rejects duplicate / reused ids (T001 Rule 1). Registration is required
    before any evidence may be ingested from a harness.
    """

    def __init__(self) -> None:
        self._adapters: dict[str, IndependentHarnessAdapter] = {}

    def register(self, adapter: IndependentHarnessAdapter) -> IndependentHarnessAdapter:
        if not adapter.harness_id:
            raise FoundationError("harness_id is required (immutable, T001 Rule 1).")
        if adapter.harness_id in self._adapters:
            raise FoundationError(
                f"harness_id '{adapter.harness_id}' already registered (T001 Rule 1)."
            )
        self._adapters[adapter.harness_id] = adapter
        return adapter

    def get(self, harness_id: str) -> IndependentHarnessAdapter:
        if harness_id not in self._adapters:
            raise FoundationError(f"harness '{harness_id}' not registered.")
        return self._adapters[harness_id]

    def is_registered(self, harness_id: str) -> bool:
        return harness_id in self._adapters

    def list(self) -> list[IndependentHarnessAdapter]:
        return list(self._adapters.values())


@dataclass
class IngestResult:
    """Outcome of an evidence ingest attempt (fail-closed)."""

    accepted: bool
    evidence_id: str
    content_hash: str
    reason: str = ""
    harness_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "accepted": self.accepted,
            "evidence_id": self.evidence_id,
            "content_hash": self.content_hash,
            "reason": self.reason,
            "harness_id": self.harness_id,
        }


@dataclass
class EvidencePayload:
    """Raw evidence submitted by an independent harness for ingest."""

    evidence_id: str
    task_id: str
    run_id: str
    producer: str
    type: str
    source: str
    content: str = ""
    content_hash: str = ""

    def resolved_hash(self) -> str:
        return self.content_hash or sha256(self.content or self.evidence_id)


class EvidenceIngestBoundary:
    """Fail-closed boundary that admits evidence from independent harnesses.

    Every admitted evidence must carry provenance (producer + source +
    content_hash) per T001 Rule 5, and is recorded into the AIOS
    ``EvidenceStore``. The same adapter + same payload always yields the same
    result (deterministic / idempotent).
    """

    def __init__(
        self,
        registry: Optional[HarnessRegistry] = None,
        evidence_store: Optional[EvidenceStore] = None,
        integrity: Optional[IntegrityChecker] = None,
    ) -> None:
        self._registry = registry or HarnessRegistry()
        self._evidence = evidence_store or EvidenceStore()
        self._integrity = integrity or IntegrityChecker()

    def ingest(self, harness_id: str, payload: EvidencePayload) -> IngestResult:
        # 1) harness must be registered first.
        if not self._registry.is_registered(harness_id):
            return IngestResult(
                accepted=False,
                evidence_id=payload.evidence_id,
                content_hash=payload.resolved_hash(),
                reason="harness not registered",
                harness_id=harness_id,
            )
        # 2) fail-closed provenance check (T001 Rule 5 / T078).
        if not payload.producer or not payload.source or not payload.content_hash:
            return IngestResult(
                accepted=False,
                evidence_id=payload.evidence_id,
                content_hash=payload.resolved_hash(),
                reason="missing provenance (producer/source/hash)",
                harness_id=harness_id,
            )
        # 3) tamper check — supplied hash must match content (T078).
        if self._integrity.is_tampered(payload.content or "", payload.content_hash):
            return IngestResult(
                accepted=False,
                evidence_id=payload.evidence_id,
                content_hash=payload.content_hash,
                reason="content hash mismatch (tamper)",
                harness_id=harness_id,
            )
        # 4) idempotent / deterministic: same evidence_id -> same accepted result.
        if self._evidence_is_present(payload.evidence_id):
            return IngestResult(
                accepted=True,
                evidence_id=payload.evidence_id,
                content_hash=payload.content_hash,
                reason="already ingested (idempotent)",
                harness_id=harness_id,
            )
        # 5) admit + record provenance.
        self._evidence.add_evidence(
            evidence_id=payload.evidence_id,
            task_id=payload.task_id,
            run_id=payload.run_id,
            producer=payload.producer,
            type=payload.type,
            source=payload.source,
            content=payload.content,
            content_hash=payload.content_hash,
        )
        return IngestResult(
            accepted=True,
            evidence_id=payload.evidence_id,
            content_hash=payload.content_hash,
            reason="admitted",
            harness_id=harness_id,
        )

    def _evidence_is_present(self, evidence_id: str) -> bool:
        try:
            self._evidence.get(evidence_id)
            return True
        except Exception:
            return False


class PolicyAuthority:
    """Enforces that AIOS retains policy authority over independent harnesses.

    An independent harness may *propose* a verdict, but it can never override
    the authoritative AIOS policy verdict.
    """

    AUTHORITY = "aios"

    @staticmethod
    def is_aios_authoritative() -> bool:
        return True

    @staticmethod
    def reject_override(independent_verdict: Any, aios_verdict: Any) -> Any:
        """Independent harness cannot override the AIOS verdict.

        Returns the authoritative AIOS verdict regardless of the independent one.
        """
        return aios_verdict

    @staticmethod
    def authoritative_verdict(base_verdict: Any) -> str:
        """Normalize an AIOS-decided verdict; never promotes on UNKNOWN/INCONCLUSIVE."""
        return (
            "pass"
            if IntegrityChecker.promotes_to_pass(base_verdict)
            else "fail"
        )


def _hash_dict(d: dict[str, Any]) -> str:
    return hashlib.sha256(
        repr(sorted(d.items())).encode("utf-8")
    ).hexdigest()[:16]
