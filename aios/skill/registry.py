"""Skill Registry — thread-safe registry of SkillContract (TASK-015, M2).

Registry is the discovery source for Skills. Skills declare capabilities
and the registry builds reverse index. Offline-first, deterministic,
thread-safe via RLock. No LLM, no network.

Layering: ``skill`` layer — stdlib + ``aios.core`` only.
Never imports ``runtime`` / ``agent`` / ``orchestrator`` / ``capability`` / ``tool``.
"""

from __future__ import annotations

import threading
from typing import Dict, List, Optional

from .contracts import SkillContract, SkillError, SkillStatus

__all__ = ["SkillRegistry"]


class SkillRegistry:
    """Thread-safe registry of :class:`SkillContract` with capability index."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._skills: Dict[str, SkillContract] = {}
        # capability -> list[skill_id]
        self._cap_index: Dict[str, List[str]] = {}
        # skill_id -> SkillStatus (mirrors contract.status but tracked separately for transitions)
        self._status: Dict[str, SkillStatus] = {}

    # -- helpers ---------------------------------------------------------
    def _index_capabilities(self, skill_id: str, caps: List[str]) -> None:
        for cap in caps:
            self._cap_index.setdefault(cap, [])
            if skill_id not in self._cap_index[cap]:
                self._cap_index[cap].append(skill_id)

    def _unindex_capabilities(self, skill_id: str, caps: List[str]) -> None:
        for cap in caps:
            lst = self._cap_index.get(cap, [])
            if skill_id in lst:
                lst.remove(skill_id)
            if not lst:
                self._cap_index.pop(cap, None)

    # -- CRUD ------------------------------------------------------------
    def register(self, contract: SkillContract) -> None:
        if not isinstance(contract, SkillContract):
            raise SkillError("contract must be SkillContract")
        contract.validate()
        with self._lock:
            sid = contract.skill_id
            if sid in self._skills:
                raise SkillError(f"skill already registered: {sid!r}")
            self._skills[sid] = contract
            self._status[sid] = contract.status if isinstance(contract.status, SkillStatus) else SkillStatus.PENDING
            self._index_capabilities(sid, contract.required_capabilities)

    def unregister(self, skill_id: str) -> None:
        with self._lock:
            contract = self._skills.get(skill_id)
            if contract is None:
                raise SkillError(f"unknown skill: {skill_id!r}")
            self._unindex_capabilities(skill_id, contract.required_capabilities)
            del self._skills[skill_id]
            self._status.pop(skill_id, None)

    def get(self, skill_id: str) -> SkillContract:
        with self._lock:
            c = self._skills.get(skill_id)
        if c is None:
            raise SkillError(f"unknown skill: {skill_id!r}")
        return c

    def list(self) -> List[SkillContract]:
        with self._lock:
            return sorted(self._skills.values(), key=lambda c: c.skill_id)

    def find(self, query: str) -> List[SkillContract]:
        if not isinstance(query, str) or not query.strip():
            raise SkillError("query must be non-empty string")
        q = query.lower()
        with self._lock:
            out: List[SkillContract] = []
            for c in self._skills.values():
                hay = " ".join([c.skill_id, c.name, c.description, " ".join(c.required_capabilities)]).lower()
                for v in c.metadata.values():
                    if isinstance(v, str):
                        hay += " " + v.lower()
                if q in hay:
                    out.append(c)
            return sorted(out, key=lambda c: c.skill_id)

    def find_by_capability(self, capability: str) -> List[SkillContract]:
        if not isinstance(capability, str) or not capability.strip():
            raise SkillError("capability must be non-empty string")
        with self._lock:
            sids = list(self._cap_index.get(capability, []))
            return [self._skills[sid] for sid in sids if sid in self._skills]

    def list_capabilities(self) -> Dict[str, List[str]]:
        with self._lock:
            return {cap: list(sids) for cap, sids in self._cap_index.items()}

    def capabilities(self) -> List[str]:
        with self._lock:
            return sorted(self._cap_index.keys())

    # -- status ----------------------------------------------------------
    def get_status(self, skill_id: str) -> SkillStatus:
        with self._lock:
            if skill_id not in self._skills:
                raise SkillError(f"unknown skill: {skill_id!r}")
            return self._status.get(skill_id, SkillStatus.PENDING)

    def set_status(self, skill_id: str, status: SkillStatus | str) -> None:
        if isinstance(status, str):
            try:
                status = SkillStatus(status)
            except ValueError as exc:
                raise SkillError(f"Unknown status {status!r}") from exc
        if not isinstance(status, SkillStatus):
            raise SkillError(f"status must be SkillStatus, got {type(status).__name__}")
        with self._lock:
            if skill_id not in self._skills:
                raise SkillError(f"unknown skill: {skill_id!r}")
            self._status[skill_id] = status
            # Also update contract
            self._skills[skill_id].status = status
            self._skills[skill_id].enabled = (status == SkillStatus.ENABLED)
            import datetime
            self._skills[skill_id].updated_at = datetime.datetime.now(datetime.timezone.utc).isoformat()

    def is_enabled(self, skill_id: str) -> bool:
        return self.get_status(skill_id) == SkillStatus.ENABLED

    def enable(self, skill_id: str) -> None:
        self.set_status(skill_id, SkillStatus.ENABLED)

    def disable(self, skill_id: str) -> None:
        self.set_status(skill_id, SkillStatus.DISABLED)

    # -- update ----------------------------------------------------------
    def update(self, contract: SkillContract) -> None:
        """Update an existing skill contract (for upgrade)."""
        if not isinstance(contract, SkillContract):
            raise SkillError("contract must be SkillContract")
        contract.validate()
        with self._lock:
            sid = contract.skill_id
            if sid not in self._skills:
                raise SkillError(f"unknown skill: {sid!r}")
            old = self._skills[sid]
            # Update capability index if changed
            if set(old.required_capabilities) != set(contract.required_capabilities):
                self._unindex_capabilities(sid, old.required_capabilities)
                self._index_capabilities(sid, contract.required_capabilities)
            self._skills[sid] = contract
            self._status[sid] = contract.status if isinstance(contract.status, SkillStatus) else SkillStatus.PENDING

    # -- misc ------------------------------------------------------------
    def __len__(self) -> int:
        with self._lock:
            return len(self._skills)

    def __contains__(self, skill_id: str) -> bool:
        with self._lock:
            return skill_id in self._skills

    def clear(self) -> None:
        with self._lock:
            self._skills.clear()
            self._cap_index.clear()
            self._status.clear()
