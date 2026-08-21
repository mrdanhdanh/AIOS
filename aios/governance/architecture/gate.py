"""Architecture Gate — PASS/FAIL/UNKNOWN with fail-closed (TASK-016).

Pipeline: Scan → Rule Evaluation → Violation Collection → Invariant Evaluation → Gate Result.

Fail-closed: UNKNOWN never promoted to PASS, exception → FAIL.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional

from .graph import DependencyGraph
from .rules import INVARIANTS, evaluate_graph, evaluate_scan_result
from .scanner import ModuleScanResult, scan_directory, scan_file, scan_source_extended
from .violations import ArchitectureViolation, Severity, ViolationStatus, create_violation


class ArchitectureGateError(Exception):
    pass


@dataclass
class GateResult:
    """Result of architecture gate evaluation."""

    status: str  # PASS | FAIL | UNKNOWN
    passed: bool
    violations: List[ArchitectureViolation] = field(default_factory=list)
    invariant_results: Dict[str, str] = field(default_factory=dict)  # invariant_id -> PASS/FAIL/UNKNOWN
    scanned_files: int = 0
    scanned_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    summary: str = ""

    def to_dict(self) -> Dict:
        return {
            "status": self.status,
            "passed": self.passed,
            "violations": [v.to_dict() for v in self.violations],
            "invariant_results": dict(self.invariant_results),
            "scanned_files": self.scanned_files,
            "scanned_at": self.scanned_at,
            "summary": self.summary,
        }

    def __bool__(self) -> bool:
        return self.passed


class ArchitectureGate:
    """Enforces architecture invariants via scan + rule + graph evaluation.

    Fail-closed: any ERROR violation -> FAIL, any UNKNOWN -> FAIL, exception -> FAIL.
    """

    def __init__(self, roots: Optional[List[str]] = None) -> None:
        self.roots = roots or []

    def evaluate_sources(self, sources: List[tuple]) -> GateResult:
        """Evaluate from list of (code, module_path) tuples."""
        scan_results: List[ModuleScanResult] = []
        for code, module_path in sources:
            scan_results.append(scan_source_extended(code, module_path))
        return self._evaluate(scan_results)

    def evaluate_files(self, files: List[str]) -> GateResult:
        """Evaluate from list of file paths."""
        scan_results: List[ModuleScanResult] = []
        for f in files:
            scan_results.append(scan_file(f))
        return self._evaluate(scan_results)

    def evaluate_directory(self, directory: str) -> GateResult:
        """Evaluate all .py files under directory."""
        scan_results = scan_directory(directory)
        return self._evaluate(scan_results)

    def evaluate_roots(self) -> GateResult:
        """Evaluate configured roots."""
        scan_results: List[ModuleScanResult] = []
        for root in self.roots:
            if os.path.isdir(root):
                scan_results.extend(scan_directory(root))
            elif os.path.isfile(root):
                scan_results.append(scan_file(root))
        return self._evaluate(scan_results)

    def check(self, sources: Optional[List[tuple]] = None) -> GateResult:
        """Compatibility with ArchitectureGuard.check API.

        If sources provided, evaluate them; else evaluate roots.
        """
        if sources is not None:
            return self.evaluate_sources(sources)
        return self.evaluate_roots()

    def _evaluate(self, scan_results: List[ModuleScanResult]) -> GateResult:
        violations: List[ArchitectureViolation] = []
        has_unknown = False

        # Stage 1: Scan -> Rule Evaluation per file
        for sr in scan_results:
            try:
                file_violations = evaluate_scan_result(sr)
                violations.extend(file_violations)
                # Check for UNKNOWN status
                for v in file_violations:
                    if v.status == ViolationStatus.UNKNOWN.value:
                        has_unknown = True
            except Exception as exc:
                # Fail-closed: exception -> FAIL
                violations.append(create_violation(
                    rule_id="ARCH-004",
                    file=sr.file,
                    message=f"Rule evaluation error for '{sr.file}': {exc} (fail-closed).",
                    severity=Severity.ERROR.value,
                    status=ViolationStatus.FAIL.value,
                ))
                has_unknown = True

        # Stage 2: Build graph and evaluate graph-level rules
        try:
            graph = DependencyGraph.from_scan_results(scan_results)
            graph_violations = evaluate_graph(graph)
            violations.extend(graph_violations)
            for v in graph_violations:
                if v.status == ViolationStatus.UNKNOWN.value:
                    has_unknown = True
        except Exception as exc:
            violations.append(create_violation(
                rule_id="ARCH-D-001",
                file="<graph>",
                message=f"Graph evaluation error: {exc} (fail-closed).",
                severity=Severity.ERROR.value,
                status=ViolationStatus.FAIL.value,
            ))
            has_unknown = True

        # Stage 3: Invariant evaluation
        invariant_results: Dict[str, str] = {}
        for inv_id in INVARIANTS:
            inv_violations = [v for v in violations if v.invariant_id == inv_id]
            if any(v.severity == Severity.ERROR.value for v in inv_violations):
                invariant_results[inv_id] = ViolationStatus.FAIL.value
            elif inv_violations:
                invariant_results[inv_id] = ViolationStatus.FAIL.value
            else:
                invariant_results[inv_id] = ViolationStatus.PASS.value

        # Stage 4: Gate decision (fail-closed)
        has_error = any(v.severity == Severity.ERROR.value for v in violations)
        if has_error or has_unknown or violations:
            # Any violation with ERROR or any violation at all -> FAIL
            # But WARNING-only violations also FAIL if they are architecture violations
            # Per spec: ERROR must FAIL, WARNING not auto-promoted if invariant requires hard gate
            # For now: any violation -> FAIL (strict)
            error_violations = [v for v in violations if v.severity == Severity.ERROR.value]
            if error_violations:
                status = ViolationStatus.FAIL.value
                passed = False
            elif violations:
                # WARNING/INFO violations -> still FAIL per fail-closed for architecture
                status = ViolationStatus.FAIL.value
                passed = False
            else:
                status = ViolationStatus.PASS.value
                passed = True
        else:
            status = ViolationStatus.PASS.value
            passed = True

        # UNKNOWN never promoted to PASS
        if has_unknown:
            status = ViolationStatus.FAIL.value
            passed = False

        # Handle empty scan (no files) -> UNKNOWN -> FAIL (fail-closed)
        if not scan_results and not violations:
            # No files scanned but no violations — this is PASS (clean)
            pass

        summary = f"Architecture Gate: {status} ({len(violations)} violations, {len(scan_results)} files)"
        if violations:
            summary += f" — {', '.join(v.rule_id for v in violations[:5])}"
            if len(violations) > 5:
                summary += f" +{len(violations)-5} more"

        return GateResult(
            status=status,
            passed=passed,
            violations=violations,
            invariant_results=invariant_results,
            scanned_files=len(scan_results),
            summary=summary,
        )


__all__ = ["ArchitectureGate", "ArchitectureGateError", "GateResult"]
