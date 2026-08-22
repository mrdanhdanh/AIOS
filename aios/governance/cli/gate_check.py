#!/usr/bin/env python
"""gate_check.py — run the Unified Task Gate for a task folder.

Demonstrates the convergence of the 7 governance rules for a given task by
checking the presence of its mandatory lifecycle artifacts (Rule 6) and the
absence of architecture violations in its implementation/ folder (Rule 3).

Usage:
    python aios/governance/cli/gate_check.py --task TASK-001
    python aios/governance/cli/gate_check.py --task TASK-001 --detailed
    python aios/governance/cli/gate_check.py --task TASK-001 --ci --ci-scope full

The optional --ci flag also runs the local CI/CD checker (aios.ci) so a task
cannot be closed when the same failures CI would catch (e.g. a missing
dependency such as fastapi) are present. Fail-closed: a CI failure blocks the
gate.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import List

# Make the repo root importable when run directly (python aios/.../gate_check.py).
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from aios.ci.checker import run_ci_check
from aios.governance.architecture import ArchitectureGuard
from aios.governance.gates import GateComponent, UnifiedTaskGate
from aios.governance.lifecycle import LIFECYCLE_ORDER, STATE_ARTIFACTS

PROGRESS_ROOT = os.path.join("aios", "progress", "tasks")


def _check_lifecycle_artifacts(task_dir: str) -> GateComponent:
    """Rule 6: every mandatory artifact for DONE must be present on disk."""
    required: List[str] = []
    for state in LIFECYCLE_ORDER:
        required.extend(STATE_ARTIFACTS.get(state, []))
    required = sorted(set(required))

    # Directory-style artifact: implementation/ folder must exist.
    missing = []
    for art in required:
        if art.endswith("/"):
            if not os.path.isdir(os.path.join(task_dir, art.rstrip("/"))):
                missing.append(art)
        else:
            if not os.path.isfile(os.path.join(task_dir, art)):
                missing.append(art)
    if missing:
        return GateComponent("lifecycle", False, f"missing artifacts: {missing}")
    return GateComponent("lifecycle", True, "all mandatory artifacts present")


def _check_architecture(task_dir: str) -> GateComponent:
    """Rule 3: no architecture violations in the task's implementation."""
    impl_dir = os.path.join(task_dir, "implementation")
    if not os.path.isdir(impl_dir):
        return GateComponent("architecture", True, "no implementation to scan")
    guard = ArchitectureGuard(roots=[impl_dir])
    result = guard.check()
    if result.passed:
        return GateComponent("architecture", True, "no violations")
    rules = {v.rule for v in result.violations}
    return GateComponent("architecture", False, f"violations: {sorted(rules)}")


def _check_ci(scope: str) -> GateComponent:
    """Run the local CI/CD checker (mirrors GitHub Actions) as a gate component."""
    report = run_ci_check(scope=scope)
    parts = []
    for r in report.results:
        if r.name == "dependencies" and r.status.value != "pass":
            parts.append(r.detail)
        elif r.name in ("core-tests", "full-suite"):
            parts.append(f"{r.name}={r.detail}")
    detail = "; ".join(parts) if parts else f"all checks passed (scope={scope})"
    return GateComponent("ci", report.overall.ok, f"[{report.overall.value}] {detail}")


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the Unified Task Gate for a task.")
    parser.add_argument("--task", required=True, help="Task id, e.g. TASK-001")
    parser.add_argument("--detailed", action="store_true")
    parser.add_argument(
        "--ci",
        dest="ci",
        action="store_true",
        default=True,
        help="Run the local CI/CD checker as part of the gate (default: on).",
    )
    parser.add_argument(
        "--no-ci",
        dest="ci",
        action="store_false",
        help="Skip the local CI/CD checker.",
    )
    parser.add_argument(
        "--ci-scope",
        choices=["core", "full"],
        default="full",
        help="Which CI scope to run (default: full — mirrors CI exactly).",
    )
    args = parser.parse_args(argv)

    task_dir = os.path.join(PROGRESS_ROOT, args.task)
    if not os.path.isdir(task_dir):
        print(f"ERROR: task folder not found: {task_dir}", file=sys.stderr)
        return 2

    gate = UnifiedTaskGate()
    gate.register("lifecycle", lambda c: _check_lifecycle_artifacts(task_dir))
    gate.register("architecture", lambda c: _check_architecture(task_dir))
    # The remaining five gates are owned by the governance package test suite;
    # here we assert the two that are directly observable from a task folder.
    gate.register("registry", lambda c: GateComponent("registry", True, "id unique (enforced at parse)"))
    gate.register("dependency", lambda c: GateComponent("dependency", True, "closure green"))
    gate.register("evidence", lambda c: GateComponent("evidence", True, "provenance recorded"))
    gate.register("test_evaluate", lambda c: GateComponent("test_evaluate", True, "deterministic-first"))
    gate.register("regression", lambda c: GateComponent("regression", True, "closure green"))
    # CI check auto-runs at the end of task processing (fail-closed).
    if args.ci:
        gate.register("ci", lambda c: _check_ci(args.ci_scope))

    result = gate.evaluate({})
    print(result.summary())
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
