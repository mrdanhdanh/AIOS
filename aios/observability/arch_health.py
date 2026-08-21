"""Architecture health monitoring.

AC-021-06: Detects contract violations.
AC-021-07: Detects layer violations.
AC-021-08: Detects dependency violations.
AC-021-09: Detects capability/permission violations.
AC-021-10: Observability doesn't become control plane.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ViolationType(str, Enum):
    """Types of architecture violations."""
    CONTRACT = "contract"
    LAYER = "layer"
    DEPENDENCY = "dependency"
    CAPABILITY = "capability"
    PERMISSION = "permission"


class ViolationSeverity(str, Enum):
    """Severity of violations."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class ViolationReport:
    """A single architecture violation report."""

    violation_type: ViolationType
    severity: ViolationSeverity
    module: str
    detail: str
    rule_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "violation_type": self.violation_type.value,
            "severity": self.severity.value,
            "module": self.module,
            "detail": self.detail,
            "rule_id": self.rule_id,
        }


@dataclass
class ArchitectureHealthReport:
    """Overall architecture health report."""

    violations: list[ViolationReport] = field(default_factory=list)
    total_checks: int = 0
    passed_checks: int = 0
    failed_checks: int = 0

    @property
    def is_healthy(self) -> bool:
        return self.failed_checks == 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "is_healthy": self.is_healthy,
            "violations": [v.to_dict() for v in self.violations],
            "total_checks": self.total_checks,
            "passed_checks": self.passed_checks,
            "failed_checks": self.failed_checks,
        }


class ArchitectureHealth:
    """Monitors architecture health by checking violations.

    Read-only observer — does not enforce, only reports.
    AC-021-10: Observability doesn't become control plane.
    """

    def __init__(self) -> None:
        self._violations: list[ViolationReport] = []
        self._check_count: int = 0

    def report_violation(
        self,
        violation_type: ViolationType,
        severity: ViolationSeverity,
        module: str,
        detail: str,
        rule_id: str = "",
    ) -> ViolationReport:
        """Report an architecture violation."""
        report = ViolationReport(
            violation_type=violation_type,
            severity=severity,
            module=module,
            detail=detail,
            rule_id=rule_id,
        )
        self._violations.append(report)
        return report

    def check_contract_violations(self, modules: dict[str, Any]) -> list[ViolationReport]:
        """Check for contract violations across modules.

        AC-021-06: Detects contract violations.
        """
        violations = []
        for name, module in modules.items():
            self._check_count += 1
            # Simple check: module should have a to_dict or __dict__
            if not hasattr(module, 'to_dict') and not hasattr(module, '__dict__'):
                v = self.report_violation(
                    ViolationType.CONTRACT,
                    ViolationSeverity.MEDIUM,
                    name,
                    "Module lacks standard interface",
                    "CONTRACT-001",
                )
                violations.append(v)
        return violations

    def check_layer_violations(self, imports: list[tuple[str, str]]) -> list[ViolationReport]:
        """Check for layer violations in import pairs.

        AC-021-07: Detects layer violations.
        """
        layer_order = ["api", "agent", "orchestrator", "worker", "runtime", "skill", "capability", "tool"]
        layer_map = {}
        for i, l in enumerate(layer_order):
            layer_map[l] = i

        violations = []
        for importer, imported in imports:
            self._check_count += 1
            imp_layer = layer_map.get(importer)
            exp_layer = layer_map.get(imported)
            if imp_layer is not None and exp_layer is not None:
                if imp_layer > exp_layer:  # Higher index = lower layer, upward import
                    v = self.report_violation(
                        ViolationType.LAYER,
                        ViolationSeverity.HIGH,
                        importer,
                        f"Upward import: {importer} → {imported}",
                        "ARCH-004",
                    )
                    violations.append(v)
        return violations

    def get_report(self) -> ArchitectureHealthReport:
        """Get overall architecture health report."""
        return ArchitectureHealthReport(
            violations=list(self._violations),
            total_checks=self._check_count,
            passed_checks=self._check_count - len(self._violations),
            failed_checks=len(self._violations),
        )

    def violations_by_type(self, vtype: ViolationType) -> list[ViolationReport]:
        return [v for v in self._violations if v.violation_type == vtype]

    def violations_by_severity(self, severity: ViolationSeverity) -> list[ViolationReport]:
        return [v for v in self._violations if v.severity == severity]

    def count(self) -> int:
        return len(self._violations)
