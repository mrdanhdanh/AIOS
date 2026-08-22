"""Recovery manager — builds a recovery plan with an evidence chain."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any


@dataclass
class RecoveryEvidence:
    step_id: str
    action: str
    result: str
    checksum: str = ""
    previous_checksum: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "step_id": self.step_id,
            "action": self.action,
            "result": self.result,
            "checksum": self.checksum,
            "previous_checksum": self.previous_checksum,
        }


class RecoveryManager:
    """Produces a recovery plan and chains evidence for auditability."""

    def __init__(self) -> None:
        self._chain: list[RecoveryEvidence] = []
        self._prev = "0" * 64

    def record_step(self, step_id: str, action: str, result: str) -> RecoveryEvidence:
        payload = f"{step_id}|{action}|{result}|{self._prev}"
        checksum = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        ev = RecoveryEvidence(
            step_id=step_id,
            action=action,
            result=result,
            checksum=checksum,
            previous_checksum=self._prev,
        )
        self._chain.append(ev)
        self._prev = checksum
        return ev

    def chain(self) -> list[RecoveryEvidence]:
        return list(self._chain)

    def verify_chain(self) -> bool:
        """Recompute checksums to ensure the evidence chain is intact."""
        prev = "0" * 64
        for ev in self._chain:
            payload = f"{ev.step_id}|{ev.action}|{ev.result}|{prev}"
            expected = hashlib.sha256(payload.encode("utf-8")).hexdigest()
            if expected != ev.checksum:
                return False
            prev = ev.checksum
        return True
