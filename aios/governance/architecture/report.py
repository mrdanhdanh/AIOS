"""Machine-readable architecture report (TASK-016).

Generates JSON report with violations, summary, gate result, provenance.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .gate import GateResult
from .violations import ArchitectureViolation


@dataclass
class ArchitectureReport:
    """Machine-readable report for CI consumption."""

    gate_result: GateResult
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    version: str = "1.0.0"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "generated_at": self.generated_at,
            "gate": self.gate_result.to_dict(),
            "summary": {
                "status": self.gate_result.status,
                "passed": self.gate_result.passed,
                "total_violations": len(self.gate_result.violations),
                "by_severity": self._by_severity(),
                "by_rule": self._by_rule(),
                "by_invariant": self._by_invariant(),
                "scanned_files": self.gate_result.scanned_files,
            },
            "violations": [v.to_dict() for v in self.gate_result.violations],
            "invariant_results": dict(self.gate_result.invariant_results),
        }

    def _by_severity(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for v in self.gate_result.violations:
            counts[v.severity] = counts.get(v.severity, 0) + 1
        return counts

    def _by_rule(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for v in self.gate_result.violations:
            counts[v.rule_id] = counts.get(v.rule_id, 0) + 1
        return counts

    def _by_invariant(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for v in self.gate_result.violations:
            inv = v.invariant_id or "unknown"
            counts[inv] = counts.get(inv, 0) + 1
        return counts

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    def save(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(self.to_json())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ArchitectureReport":
        gate_data = data.get("gate", {})
        gate = GateResult(
            status=gate_data.get("status", "UNKNOWN"),
            passed=gate_data.get("passed", False),
            violations=[ArchitectureViolation.from_dict(v) for v in gate_data.get("violations", [])],
            invariant_results=gate_data.get("invariant_results", {}),
            scanned_files=gate_data.get("scanned_files", 0),
            scanned_at=gate_data.get("scanned_at", ""),
            summary=gate_data.get("summary", ""),
        )
        return cls(
            gate_result=gate,
            generated_at=data.get("generated_at", ""),
            version=data.get("version", "1.0.0"),
        )

    @classmethod
    def from_json(cls, text: str) -> "ArchitectureReport":
        return cls.from_dict(json.loads(text))

    @classmethod
    def load(cls, path: str) -> "ArchitectureReport":
        with open(path, "r", encoding="utf-8") as fh:
            return cls.from_json(fh.read())


def generate_report(gate_result: GateResult) -> ArchitectureReport:
    """Generate report from gate result."""
    return ArchitectureReport(gate_result=gate_result)


def generate_report_json(gate_result: GateResult, indent: int = 2) -> str:
    """Generate JSON string from gate result."""
    return generate_report(gate_result).to_json(indent=indent)


__all__ = ["ArchitectureReport", "generate_report", "generate_report_json"]
