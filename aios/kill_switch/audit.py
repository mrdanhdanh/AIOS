"""Audit log + evidence provenance for Kill Switch (TASK-068).

Uses the governance evidence store public API (``aios.governance.evidence``)
to record every halt with a complete provenance chain (Rule 5). The
``evidence_ref`` of each ``HaltSignal`` points back to the recorded evidence.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from aios.governance.evidence.store import (
    Artifact,
    EvidenceStore,
    Requirement,
    Run,
    TaskRecord,
    compute_hash,
)

from aios.kill_switch.contracts import HaltSignal

_TASK_ID = "TASK-068"
_REQUIREMENT_ID = "T068-REQ"
_ARTIFACT_ID = "T068-ART"
_RUN_ID = "T068-RUN"


class AuditLog:
    """Records halt events as admissible evidence with full provenance."""

    def __init__(self, evidence_store: Optional[EvidenceStore] = None) -> None:
        self._store = evidence_store or EvidenceStore()
        self._scaffold()

    # ----- provenance scaffolding (idempotent) ------------------------- #
    def _scaffold(self) -> None:
        if _REQUIREMENT_ID not in self._store._requirements:
            self._store.add_requirement(
                Requirement(_REQUIREMENT_ID, "Kill Switch emergency stop", "T068")
            )
        if _TASK_ID not in self._store._tasks:
            self._store.add_task_record(TaskRecord(_TASK_ID, _REQUIREMENT_ID))
        if _ARTIFACT_ID not in self._store._artifacts:
            self._store.add_artifact(
                Artifact(_ARTIFACT_ID, _TASK_ID, _REQUIREMENT_ID, "implementation")
            )
        if _RUN_ID not in self._store._runs:
            self._store.add_run(Run(_RUN_ID, _ARTIFACT_ID, _TASK_ID, "kill_switch.issue"))

    # ----- record ------------------------------------------------------ #
    def record_halt(
        self, signal: HaltSignal, affected: List[str], drained: List[str]
    ) -> str:
        evidence_id = f"ks-evt-{signal.signal_id}"
        content = json.dumps(
            {
                "signal": signal.to_dict(),
                "affected": affected,
                "drained": drained,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        chash = compute_hash(content)
        # Idempotent: do not duplicate evidence for the same signal.
        try:
            existing = self._store.get(evidence_id)
            return existing.evidence_id
        except Exception:  # noqa: BLE001 - EvidenceError when missing
            pass
        self._store.add_evidence(
            evidence_id=evidence_id,
            task_id=_TASK_ID,
            run_id=_RUN_ID,
            producer="kill_switch.controller",
            type="halt_signal",
            source="aios.kill_switch",
            content=content,
            content_hash=chash,
            parent_artifact=_ARTIFACT_ID,
        )
        return evidence_id

    def provenance_complete(self, evidence_id: str) -> bool:
        return self._store.is_admissible(evidence_id)

    def store(self) -> EvidenceStore:
        return self._store
