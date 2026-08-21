"""Operations contracts."""
from __future__ import annotations
import uuid
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

class OperationStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class Operation:
    op_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    op_type: str = ""
    status: OperationStatus = OperationStatus.PENDING
    target: str = ""
    details: dict = field(default_factory=dict)
    def to_dict(self) -> dict[str, Any]:
        return {"op_id": self.op_id, "op_type": self.op_type, "status": self.status.value, "target": self.target}

@dataclass
class OperationLog:
    op_id: str = ""
    timestamp: float = field(default_factory=time.time)
    action: str = ""
    result: str = ""
    def to_dict(self) -> dict[str, Any]:
        return {"op_id": self.op_id, "action": self.action, "result": self.result}
