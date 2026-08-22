"""Memory Controller (TASK-057).

A capability on the existing Memory (T007). It validates provenance, applies
safety/redaction (consuming the T040 contract), enforces the trust/verification
guard (INV-034), applies deterministic retention, deduplicates, and only
persists when the Autonomy Governor (T054) allows the write.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from aios.autonomous_memory.contracts import (
    FailureMemoryEntry,
    GoalMemoryEntry,
    MemoryScope,
    TrustStatus,
    VerificationStatus,
)
from aios.autonomous_memory.retention import RetentionPolicy


@dataclass
class WriteResult:
    persisted: bool
    reason: str = ""
    entry_id: str = ""


class MemoryController:
    def __init__(
        self,
        store: dict[str, list[Any]] | None = None,
        evidence_valid: Callable[[str], bool] | None = None,
        governor_allow: Callable[[str], bool] | None = None,
        redact: Callable[[dict[str, Any]], dict[str, Any]] | None = None,
        retention: RetentionPolicy | None = None,
    ) -> None:
        # scope -> list of entries
        self._store: dict[str, list[Any]] = store if store is not None else {}
        self._evidence_valid = evidence_valid or (lambda e: bool(e))
        self._governor_allow = governor_allow  # callable(action) -> bool
        self._redact = redact or (lambda d: d)
        self._retention = retention or RetentionPolicy()

    # ---- provenance -----------------------------------------------------
    def _validate_provenance(self, evidence_ref: str) -> bool:
        if not evidence_ref:
            return False
        return bool(self._evidence_valid(evidence_ref))

    # ---- write ----------------------------------------------------------
    def write_failure(self, entry: FailureMemoryEntry, governor_action: str = "write") -> WriteResult:
        if not self._validate_provenance(entry.evidence_ref):
            return WriteResult(False, "invalid or missing evidence_ref")
        if self._governor_allow is not None and not self._governor_allow(governor_action):
            return WriteResult(False, "governor denied")
        # Deduplicate by (goal_id, failure_class, outcome).
        scope = entry.scope.value
        for existing in self._store.get(scope, []):
            if (isinstance(existing, FailureMemoryEntry)
                    and existing.goal_id == entry.goal_id
                    and existing.failure_class == entry.failure_class
                    and existing.outcome == entry.outcome):
                # Update in place instead of creating a duplicate.
                existing.classification = entry.classification
                existing.recovery_strategy = entry.recovery_strategy
                return WriteResult(True, "deduplicated", existing.entry_id)
        self._store.setdefault(scope, []).append(entry)
        self._enforce_retention(scope)
        return WriteResult(True, "persisted", entry.entry_id)

    def write_goal(self, entry: GoalMemoryEntry, governor_action: str = "write") -> WriteResult:
        if not self._validate_provenance(entry.evidence_ref):
            return WriteResult(False, "invalid or missing evidence_ref")
        if self._governor_allow is not None and not self._governor_allow(governor_action):
            return WriteResult(False, "governor denied")
        # Redact raw observation before persisting (consume T040 contract).
        entry.observation = self._redact(entry.observation)
        # lesson_candidate is NEVER trusted on write (INV-034).
        entry.verification_status = VerificationStatus.UNVERIFIED
        entry.trust_status = TrustStatus.UNTRUSTED
        # Deduplicate by (goal_id, execution_id, outcome).
        scope = entry.scope.value
        for existing in self._store.get(scope, []):
            if (isinstance(existing, GoalMemoryEntry)
                    and existing.goal_id == entry.goal_id
                    and existing.execution_id == entry.execution_id
                    and existing.outcome == entry.outcome):
                existing.observation = entry.observation
                existing.lesson_candidate = entry.lesson_candidate
                return WriteResult(True, "deduplicated", existing.entry_id)
        self._store.setdefault(scope, []).append(entry)
        self._enforce_retention(scope)
        return WriteResult(True, "persisted", entry.entry_id)

    # ---- trust / verification ------------------------------------------
    def verify_entry(self, entry_id: str, scope: str = MemoryScope.GOAL.value) -> bool:
        for e in self._store.get(scope, []):
            if e.entry_id == entry_id:
                if not self._validate_provenance(e.evidence_ref):
                    return False
                e.verification_status = VerificationStatus.VERIFIED
                e.trust_status = TrustStatus.TRUSTED
                return True
        return False

    # ---- read -----------------------------------------------------------
    def read(self, scope: str, trusted_only: bool = True) -> list[Any]:
        entries = self._store.get(scope, [])
        if trusted_only:
            return [e for e in entries if str(getattr(e, "trust_status", "untrusted").value) == "trusted"]
        return list(entries)

    def _enforce_retention(self, scope: str) -> None:
        entries = self._store.get(scope, [])
        # Expire by TTL.
        live = [e for e in entries if not self._retention.is_expired(e)]
        # Evict by max size (deterministic lowest-priority first).
        while len(live) > self._retention.max_size:
            victim = self._retention.select_eviction(live)
            if victim is None:
                break
            live.remove(victim)
        self._store[scope] = live
