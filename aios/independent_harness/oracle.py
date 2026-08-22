"""Independent Verification Oracle (TASK-105, M16).

Maps checkable AIOS invariants onto independent harness oracle checks and
**bridges** the oracle's evidence into AIOS verification. The oracle only
supplies an ``independent_verdict`` (input); **AIOS policy verdict is the
authoritative one** and an oracle conflict never overrides it.

This is the **oracle bridge**, not a new verification engine. It reuses:
* Foundation (T104) — registration + evidence ingest boundary
* ``aios.harness.contracts`` (HarnessSpec, RunResult) — T030/T032
* ``aios.verification_integrity`` (IntegrityChecker, VerdictClass) — T078
* ``aios.governance.evidence.store`` (EvidenceStore) — T001 Rule 5

Safety properties (fail-closed / provenance / deterministic / authority):
* AIOS authority — oracle has no policy power; AIOS verdict is authoritative.
* Fail-closed — oracle INCONCLUSIVE/UNKNOWN -> not promoted to PASS (T078).
* Evidence required — every bridge carries provenance (T001 Rule 5).
* Deterministic — same invariant + same oracle input -> same independent_verdict.
* No transfer of authority — reuses Foundation + Harness + Integrity.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from aios.verification_integrity.integrity import VerdictClass, sha256

from .foundation import (
    EvidenceIngestBoundary,
    EvidencePayload,
    FoundationError,
    HarnessRegistry,
    PolicyAuthority,
)


@dataclass
class OracleResult:
    """Result of an oracle query bridged into AIOS verification.

    ``independent_verdict`` is the oracle's input; ``aios_policy_verdict`` is the
    authoritative decision computed by AIOS. ``authority`` is always ``aios``.
    """

    oracle_id: str
    invariant_ref: str
    independent_verdict: str
    aios_policy_verdict: str
    evidence_ref: str
    authority: str = "aios"

    def to_dict(self) -> dict[str, Any]:
        return {
            "oracle_id": self.oracle_id,
            "invariant_ref": self.invariant_ref,
            "independent_verdict": self.independent_verdict,
            "aios_policy_verdict": self.aios_policy_verdict,
            "evidence_ref": self.evidence_ref,
            "authority": self.authority,
        }


class InvariantMapping:
    """Maps AIOS invariant references onto independent harness oracle checks."""

    def __init__(self) -> None:
        self._map: dict[str, str] = {}

    def register(self, invariant_ref: str, oracle_check: str) -> None:
        self._map[invariant_ref] = oracle_check

    def resolve(self, invariant_ref: str) -> Optional[str]:
        return self._map.get(invariant_ref)

    def is_mapped(self, invariant_ref: str) -> bool:
        return invariant_ref in self._map


# An oracle callable takes the oracle check name + raw input and returns a
# verdict string understood by VerdictClass (pass/fail/unknown/inconclusive).
OracleCallable = Callable[[str, Any], str]


class IndependentVerificationOracle:
    """Bridges independent harness oracle verdicts into AIOS verification."""

    def __init__(
        self,
        registry: Optional[HarnessRegistry] = None,
        ingest: Optional[EvidenceIngestBoundary] = None,
        mapping: Optional[InvariantMapping] = None,
    ) -> None:
        self._registry = registry or HarnessRegistry()
        self._ingest = ingest or EvidenceIngestBoundary(self._registry)
        self._mapping = mapping or InvariantMapping()

    def map_invariant(self, invariant_ref: str, oracle_check: str) -> None:
        self._mapping.register(invariant_ref, oracle_check)

    def query(
        self,
        harness_id: str,
        invariant_ref: str,
        oracle: OracleCallable,
        oracle_input: Any = None,
        task_id: str = "TASK-105",
        run_id: str = "",
    ) -> OracleResult:
        if not self._mapping.is_mapped(invariant_ref):
            raise FoundationError(f"invariant '{invariant_ref}' not mapped to an oracle check.")
        check = self._mapping.resolve(invariant_ref)
        # Independent verdict is the oracle's *input* only.
        independent_verdict = str(oracle(check, oracle_input))
        vclass = VerdictClass.from_any(independent_verdict)

        # Bridge the oracle evidence into AIOS via the foundation ingest boundary.
        evidence_id = f"oracle-ev-{invariant_ref}-{vclass.value}"
        payload = EvidencePayload(
            evidence_id=evidence_id,
            task_id=task_id,
            run_id=run_id or evidence_id,
            producer=f"independent-oracle:{harness_id}",
            type="oracle_verdict",
            source=invariant_ref,
            content=independent_verdict,
            content_hash=sha256(independent_verdict),
        )
        ingest_result = self._ingest.ingest(harness_id, payload)

        # AIOS authority: the policy verdict is computed by AIOS, fail-closed.
        # An oracle conflict (independent=pass, AIOS=fail) does NOT override AIOS.
        aios_verdict = (
            "pass" if vclass is VerdictClass.PASS and ingest_result.accepted else "fail"
        )
        aios_policy_verdict = PolicyAuthority.reject_override(
            independent_verdict, aios_verdict
        )
        return OracleResult(
            oracle_id=f"oracle-{invariant_ref}",
            invariant_ref=invariant_ref,
            independent_verdict=independent_verdict,
            aios_policy_verdict=aios_policy_verdict,
            evidence_ref=evidence_id if ingest_result.accepted else "",
            authority="aios",
        )
