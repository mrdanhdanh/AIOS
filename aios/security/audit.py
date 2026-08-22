"""Audit trail for privileged actions (TASK-070).

Every privileged action writes an audit evidence record carrying provenance.
When the governance :class:`~aios.governance.evidence.store.EvidenceStore`
public API is available it is used; otherwise a local audit log is kept that
still carries an ``evidence_ref`` so provenance can be established later.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from aios.governance.evidence.store import EvidenceStore


@dataclass
class AuditRecord:
    """A single audit record for a secured action."""

    audit_id: str
    principal: str
    action: str
    target: str
    decision: str  # ALLOW | BLOCK
    evidence_ref: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "audit_id": self.audit_id,
            "principal": self.principal,
            "action": self.action,
            "target": self.target,
            "decision": self.decision,
            "evidence_ref": self.evidence_ref,
            "metadata": dict(self.metadata),
        }


class SecurityAudit:
    """Writes an audit evidence record for every privileged action.

    Integration: uses the governance EvidenceStore public API when supplied,
    otherwise keeps a local log with synthetic ``evidence_ref`` values.
    """

    def __init__(
        self,
        evidence_store: Optional[EvidenceStore] = None,
        task_id: str = "TASK-070",
    ) -> None:
        self._store = evidence_store
        self._task_id = task_id
        self._local: List[AuditRecord] = []

    def record(
        self,
        principal: str,
        action: str,
        target: str,
        decision: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AuditRecord:
        rec = AuditRecord(
            audit_id=uuid.uuid4().hex[:12],
            principal=principal,
            action=action,
            target=target,
            decision=decision,
            metadata=metadata or {},
        )
        if self._store is not None:
            content = str(rec.to_dict())
            ev = self._store.add_evidence(
                evidence_id=f"evt-{rec.audit_id}",
                task_id=self._task_id,
                run_id=f"run-{rec.audit_id}",
                producer="aios.security.audit",
                type="security_audit",
                source="SecurityAudit.record",
                content=content,
            )
            rec.evidence_ref = ev.evidence_id
        else:
            rec.evidence_ref = f"local-{rec.audit_id}"
        self._local.append(rec)
        return rec

    def records(self) -> List[AuditRecord]:
        return list(self._local)

    def last(self) -> Optional[AuditRecord]:
        return self._local[-1] if self._local else None
