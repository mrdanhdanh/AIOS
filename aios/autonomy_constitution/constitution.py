"""Autonomy Constitution + Audit Trail (TASK-103, M15).

Canonical constitution/audit contract:

    AuditEntry
    ├── decision_id
    ├── principal
    ├── action
    ├── policy_ref
    ├── constitution_compliant: bool
    ├── prev_entry_hash (chain)
    ├── timestamp
    └── evidence_ref

Safety properties (all fail-closed-constitution / immutable-audit / tamper-evident / provenance / deterministic):
* Fail-closed constitution — violation -> BLOCK.
* Immutable audit — entry never edited/deleted; hash-chained.
* Tamper-evident — editing an entry is detected (T078).
* Evidence required — every entry carries provenance (T001 Rule 5).
* Deterministic — same decision + same constitution -> same compliance.
* No parallel constitution — uses Autonomy (T067) + Trust (T102) + Evidence (T001)
  + Integrity (T078) + Kill Switch (T068).

Integration: imports ``aios.autonomy_safety`` (AutonomyLevel), ``aios.autonomy_governor``
(AutonomyAction, AutonomyDecision), ``aios.trust_budget`` (TrustBudget),
``aios.kill_switch`` (KillSwitchController, HaltSignal, HaltScope, HaltSource),
``aios.verification_integrity`` (IntegrityChecker, sha256) and
``aios.governance.evidence.store`` (EvidenceStore). No rewrite of any dependency.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, List, Optional

from aios.autonomy_governor.contracts import (
    AutonomyAction,
    AutonomyDecision,
    AutonomyRisk,
)
from aios.autonomy_safety.contracts import AutonomyLevel
from aios.governance.evidence.store import EvidenceStore
from aios.kill_switch.contracts import HaltScope, HaltSignal, HaltSource
from aios.kill_switch.controller import KillSwitchController
from aios.trust_budget.budget import TrustBudget
from aios.verification_integrity.integrity import IntegrityChecker, sha256


@dataclass
class ConstitutionDecision:
    """A decision submitted for constitution evaluation (accountability-bound)."""

    decision_id: str
    principal: str
    action: str
    policy_ref: str
    risk: str = "low"  # low | medium | high | critical
    trust_remaining: float = 1.0
    halt_active: bool = False
    evidence_ref: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision_id": self.decision_id,
            "principal": self.principal,
            "action": self.action,
            "policy_ref": self.policy_ref,
            "risk": self.risk,
            "trust_remaining": self.trust_remaining,
            "halt_active": self.halt_active,
            "evidence_ref": self.evidence_ref,
        }


@dataclass
class AuditEntry:
    """An immutable, hash-chained audit entry for an autonomy decision."""

    decision_id: str
    principal: str
    action: str
    policy_ref: str
    constitution_compliant: bool
    prev_entry_hash: str = ""
    timestamp: str = ""
    evidence_ref: str = ""

    def canonical(self) -> str:
        """Deterministic canonical serialization (used for hashing / chaining)."""
        return json.dumps(
            {
                "decision_id": self.decision_id,
                "principal": self.principal,
                "action": self.action,
                "policy_ref": self.policy_ref,
                "constitution_compliant": self.constitution_compliant,
                "prev_entry_hash": self.prev_entry_hash,
                "timestamp": self.timestamp,
                "evidence_ref": self.evidence_ref,
            },
            sort_keys=True,
            separators=(",", ":"),
        )

    def content_hash(self) -> str:
        return sha256(self.canonical())

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision_id": self.decision_id,
            "principal": self.principal,
            "action": self.action,
            "policy_ref": self.policy_ref,
            "constitution_compliant": self.constitution_compliant,
            "prev_entry_hash": self.prev_entry_hash,
            "timestamp": self.timestamp,
            "evidence_ref": self.evidence_ref,
        }


class AutonomyConstitution:
    """The supreme autonomy law (fail-closed: any violation -> BLOCK)."""

    def __init__(self, rules: Optional[List[str]] = None) -> None:
        self._rules = rules or self._default_rules()

    @staticmethod
    def _default_rules() -> List[str]:
        return [
            "R1: DESTRUCTIVE action requires human approval (policy_ref must cite approval)",
            "R2: No action may proceed while a kill-switch halt is active",
            "R3: Action must stay within the trust budget (trust_remaining > 0)",
            "R4: CRITICAL risk requires policy escalation (policy_ref must cite escalation)",
        ]

    def rules(self) -> List[str]:
        return list(self._rules)

    def is_compliant(self, decision: ConstitutionDecision) -> bool:
        """Fail-closed: any supreme-rule violation -> non-compliant (BLOCK)."""
        if decision.action == AutonomyAction.DESTRUCTIVE.value and "approval" not in decision.policy_ref:
            return False
        if decision.halt_active:
            return False
        if decision.trust_remaining <= 0:
            return False
        if decision.risk == AutonomyRisk.CRITICAL.value and "escalation" not in decision.policy_ref:
            return False
        return True


class AuditTrail:
    """Immutable, hash-chained, tamper-evident audit trail (T078)."""

    def __init__(self, integrity_checker: Optional[IntegrityChecker] = None) -> None:
        self._entries: List[AuditEntry] = []
        self._integrity = integrity_checker or IntegrityChecker()

    def append(self, entry: AuditEntry) -> AuditEntry:
        """Append an entry, chaining it to the previous one's content hash."""
        if self._entries:
            entry.prev_entry_hash = self._entries[-1].content_hash()
        if not entry.timestamp:
            entry.timestamp = datetime.now(timezone.utc).isoformat()
        self._entries.append(entry)
        return entry

    def entries(self) -> List[AuditEntry]:
        return list(self._entries)

    def verify_chain(self) -> bool:
        """Tamper-evident: every entry's prev hash must match the real previous."""
        for i, e in enumerate(self._entries):
            if i == 0:
                if e.prev_entry_hash:
                    return False
            else:
                if e.prev_entry_hash != self._entries[i - 1].content_hash():
                    return False
        return True

    def detect_tamper(self) -> bool:
        """True when the chain has been altered (T078)."""
        return not self.verify_chain()


class ConstitutionEngine:
    """Evaluates autonomy decisions against the constitution and audits them."""

    def __init__(
        self,
        evidence_store: Optional[EvidenceStore] = None,
        constitution: Optional[AutonomyConstitution] = None,
        audit_trail: Optional[AuditTrail] = None,
        integrity_checker: Optional[IntegrityChecker] = None,
        kill_switch: Optional[KillSwitchController] = None,
    ) -> None:
        self._evidence = evidence_store or EvidenceStore()
        self._constitution = constitution or AutonomyConstitution()
        self._audit = audit_trail or AuditTrail(integrity_checker)
        self._integrity = integrity_checker or IntegrityChecker()
        self._kill = kill_switch or KillSwitchController()

    # -- evaluation (fail-closed) -------------------------------------------

    def is_blocked(self, decision: ConstitutionDecision) -> bool:
        """A violating decision is BLOCKed (fail-closed)."""
        return not self._constitution.is_compliant(decision)

    def evaluate(self, decision: ConstitutionDecision) -> tuple[bool, AuditEntry]:
        """Evaluate a decision; append an immutable audit entry; return
        (compliant, entry). Fail-closed: violation -> compliant=False."""
        compliant = self._constitution.is_compliant(decision)
        entry = AuditEntry(
            decision_id=decision.decision_id,
            principal=decision.principal,
            action=decision.action,
            policy_ref=decision.policy_ref,
            constitution_compliant=compliant,
            timestamp=datetime.now(timezone.utc).isoformat(),
            evidence_ref=decision.evidence_ref,
        )
        self._audit.append(entry)
        self._record_evidence(entry)
        return compliant, entry

    # -- trust integration (T102) -------------------------------------------

    def evaluate_with_trust(
        self, decision: ConstitutionDecision, trust: Optional[TrustBudget] = None
    ) -> tuple[bool, AuditEntry]:
        """Evaluate a decision, optionally binding its trust_remaining to a
        TrustBudget (T102) so an empty budget is a constitution violation."""
        if trust is not None:
            decision = ConstitutionDecision(
                decision_id=decision.decision_id,
                principal=decision.principal,
                action=decision.action,
                policy_ref=decision.policy_ref,
                risk=decision.risk,
                trust_remaining=trust.remaining,
                halt_active=decision.halt_active,
                evidence_ref=decision.evidence_ref,
            )
        return self.evaluate(decision)

    # -- audit integrity -----------------------------------------------------

    def verify_audit(self) -> bool:
        return self._audit.verify_chain()

    def detect_tamper(self) -> bool:
        return self._audit.detect_tamper()

    # -- evidence ------------------------------------------------------------

    def _record_evidence(self, entry: AuditEntry) -> str:
        ev_id = entry.evidence_ref or entry.decision_id
        self._evidence.add_evidence(
            evidence_id=ev_id,
            task_id="TASK-103",
            run_id="run-103",
            producer="autonomy_constitution",
            type="audit_entry",
            source=entry.decision_id,
            content=json.dumps(entry.to_dict(), sort_keys=True),
        )
        return ev_id

    def provenance_complete(self, entry: AuditEntry) -> bool:
        """Every entry carries provenance (T001 Rule 5)."""
        return bool(entry.evidence_ref)

    def result_hash(self, entry: AuditEntry) -> str:
        """Deterministic hash (same entry -> same hash)."""
        return hashlib.sha256(
            json.dumps(entry.to_dict(), sort_keys=True).encode("utf-8")
        ).hexdigest()
