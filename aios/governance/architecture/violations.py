"""Architecture violation model with provenance (TASK-016).

Defines ArchitectureViolation with full provenance chain:
  violation_id, rule_id, invariant_id, file, line, source_component,
  target_component, violation_type, severity, message, evidence,
  detected_at, status.

Fail-closed: UNKNOWN never promoted to PASS.
"""

from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional


class Severity(str, Enum):
    """Violation severity."""

    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


class ViolationStatus(str, Enum):
    """Gate/violation status — fail-closed."""

    PASS = "PASS"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"


class ViolationType(str, Enum):
    """Category of architecture violation."""

    IMPORT_BOUNDARY = "import_boundary"
    FORBIDDEN_DEPENDENCY = "forbidden_dependency"
    REVERSE_DEPENDENCY = "reverse_dependency"
    CIRCULAR_DEPENDENCY = "circular_dependency"
    CONTRACT_BOUNDARY = "contract_boundary"
    POLICY_BYPASS = "policy_bypass"
    DETERMINISTIC_BYPASS = "deterministic_bypass"
    PLUGIN_ISOLATION = "plugin_isolation"
    ORCHESTRATOR_GOD_OBJECT = "orchestrator_god_object"
    LAYER_VIOLATION = "layer_violation"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _gen_violation_id() -> str:
    return f"viol-{uuid.uuid4().hex[:12]}"


@dataclass
class ArchitectureViolation:
    """Full provenance violation model (TASK-016 §8)."""

    violation_id: str = field(default_factory=_gen_violation_id)
    rule_id: str = ""
    invariant_id: Optional[str] = None
    file: str = ""
    line: Optional[int] = None
    source_component: str = ""
    target_component: str = ""
    violation_type: str = ViolationType.IMPORT_BOUNDARY.value
    severity: str = Severity.ERROR.value
    message: str = ""
    evidence: str = ""
    detected_at: str = field(default_factory=_now_iso)
    status: str = ViolationStatus.FAIL.value

    def to_dict(self) -> Dict[str, Any]:
        return {
            "violation_id": self.violation_id,
            "rule_id": self.rule_id,
            "invariant_id": self.invariant_id,
            "file": self.file,
            "line": self.line,
            "source_component": self.source_component,
            "target_component": self.target_component,
            "violation_type": self.violation_type,
            "severity": self.severity,
            "message": self.message,
            "evidence": self.evidence,
            "detected_at": self.detected_at,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ArchitectureViolation":
        return cls(
            violation_id=data.get("violation_id", _gen_violation_id()),
            rule_id=data.get("rule_id", ""),
            invariant_id=data.get("invariant_id"),
            file=data.get("file", ""),
            line=data.get("line"),
            source_component=data.get("source_component", ""),
            target_component=data.get("target_component", ""),
            violation_type=data.get("violation_type", ViolationType.IMPORT_BOUNDARY.value),
            severity=data.get("severity", Severity.ERROR.value),
            message=data.get("message", ""),
            evidence=data.get("evidence", ""),
            detected_at=data.get("detected_at", _now_iso()),
            status=data.get("status", ViolationStatus.FAIL.value),
        )

    def content_hash(self) -> str:
        """Deterministic hash of violation content for provenance."""
        content = f"{self.rule_id}|{self.file}|{self.line}|{self.source_component}|{self.target_component}|{self.message}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    @property
    def is_error(self) -> bool:
        return self.severity == Severity.ERROR.value

    @property
    def is_fail(self) -> bool:
        return self.status == ViolationStatus.FAIL.value


def create_violation(
    rule_id: str,
    file: str,
    message: str,
    *,
    invariant_id: Optional[str] = None,
    line: Optional[int] = None,
    source_component: str = "",
    target_component: str = "",
    violation_type: str = ViolationType.IMPORT_BOUNDARY.value,
    severity: str = Severity.ERROR.value,
    evidence: str = "",
    status: str = ViolationStatus.FAIL.value,
) -> ArchitectureViolation:
    """Factory for ArchitectureViolation with auto-generated id and timestamp."""
    return ArchitectureViolation(
        violation_id=_gen_violation_id(),
        rule_id=rule_id,
        invariant_id=invariant_id,
        file=file,
        line=line,
        source_component=source_component,
        target_component=target_component,
        violation_type=violation_type,
        severity=severity,
        message=message,
        evidence=evidence or message,
        detected_at=_now_iso(),
        status=status,
    )


__all__ = [
    "ArchitectureViolation",
    "Severity",
    "ViolationStatus",
    "ViolationType",
    "create_violation",
]
