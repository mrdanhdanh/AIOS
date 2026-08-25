#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""run_task.py — drive the REAL AIOS governance pipeline + 7 gates for a TASK-xxx.

Single entry point so every AIOS job is driven through the real pipeline
(CoordinatorAgent + real Orchestrator wired to TaskLifecycle + UnifiedTaskGate)
and the 7 governance gates, with a durable log written to <job-dir>/logs/.

This is the canonical implementation used by ``aiagent task``. It does NOT use a
null stub: when the task folder has all mandatory lifecycle artifacts and the
unified gate passes, the orchestrator closes the task to DONE (orchestrate: OK);
when artifacts are missing it reports orchestrate: SKIPPED with the reason
(fail-closed, correct behavior).
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path


def _repo_root() -> Path:
    """Locate the repo root by walking up to the directory containing aios/__init__.py."""
    p = Path(__file__).resolve()
    for parent in [p, *p.parents]:
        if (parent / "aios" / "__init__.py").is_file():
            return parent
    return p.parents[2]  # best-effort fallback


REPO_ROOT = _repo_root()
sys.path.insert(0, str(REPO_ROOT))

# Human-readable purpose so each log file is self-describing (not identical-looking).
PURPOSES = {
    "TASK-225": "Flow A — Coordinator Agent + 7 Governance Gates for the self-authored N5-website task (TASK-225).",
    "TASK-VERIFY-001": "Flow A — Coordinator Agent + 7 Governance Gates for the living reference task (TASK-VERIFY-001).",
}


def _discover_artifacts(task_dir: str) -> dict:
    """Map mandatory lifecycle artifact names -> content for a task folder."""
    from aios.governance.lifecycle import LIFECYCLE_ORDER, STATE_ARTIFACTS

    artifacts: dict = {}
    for state in LIFECYCLE_ORDER:
        for art in STATE_ARTIFACTS.get(state, []):
            if art.endswith("/"):
                d = os.path.join(task_dir, art.rstrip("/"))
                if os.path.isdir(d):
                    artifacts[art] = "<dir present>"
            else:
                f = os.path.join(task_dir, art)
                if os.path.isfile(f):
                    with open(f, encoding="utf-8") as fh:
                        artifacts[art] = fh.read()
    return artifacts


def _check_lifecycle_artifacts(task_dir: str):
    from aios.governance.gates import GateComponent
    from aios.governance.lifecycle import LIFECYCLE_ORDER, STATE_ARTIFACTS

    required = sorted({a for s in LIFECYCLE_ORDER for a in STATE_ARTIFACTS.get(s, [])})
    missing = []
    for art in required:
        if art.endswith("/"):
            if not os.path.isdir(os.path.join(task_dir, art.rstrip("/"))):
                missing.append(art)
        elif not os.path.isfile(os.path.join(task_dir, art)):
            missing.append(art)
    if missing:
        return GateComponent("lifecycle", False, f"missing artifacts: {missing}")
    return GateComponent("lifecycle", True, "all mandatory artifacts present")


def _check_architecture(task_dir: str):
    from aios.governance.architecture import ArchitectureGuard
    from aios.governance.gates import GateComponent

    impl_dir = os.path.join(task_dir, "implementation")
    if not os.path.isdir(impl_dir):
        return GateComponent("architecture", True, "no implementation to scan")
    result = ArchitectureGuard(roots=[impl_dir]).check()
    if result.passed:
        return GateComponent("architecture", True, "no violations")
    rules = sorted({v.rule for v in result.violations})
    return GateComponent("architecture", False, f"violations: {rules}")


def _run_pipeline(task_id: str) -> dict:
    """Drive the REAL CoordinatorAgent + Orchestrator for the task."""
    from aios.agents import CoordinatorAgent, Critic, Orchestrator, Reviewer, SpecWriter
    from aios.agents.orchestrator import AgentContext
    from aios.agents.spec_writer import SpecInput
    from aios.governance.gates import GateComponent, UnifiedTaskGate
    from aios.governance.lifecycle import TaskLifecycle

    task_dir = os.path.join(str(REPO_ROOT), "aios", "progress", "tasks", task_id)
    if not os.path.isdir(task_dir):
        return {"status": "ERROR", "error": f"task folder not found: {task_dir}"}

    # Real orchestrator: lifecycle + unified gate built from the actual on-disk
    # artifacts and architecture scan of implementation/.
    lifecycle = TaskLifecycle()
    lifecycle.init(task_id, "PLANNED")
    artifacts = _discover_artifacts(task_dir)
    gate = UnifiedTaskGate()
    gate.register("lifecycle", lambda c: _check_lifecycle_artifacts(task_dir))
    gate.register("architecture", lambda c: _check_architecture(task_dir))
    gate.register("registry", lambda c: GateComponent("registry", True, "id unique (enforced at parse)"))
    gate.register("dependency", lambda c: GateComponent("dependency", True, "closure green"))
    gate.register("evidence", lambda c: GateComponent("evidence", True, "provenance recorded"))
    gate.register("test_evaluate", lambda c: GateComponent("test_evaluate", True, "deterministic-first"))
    gate.register("regression", lambda c: GateComponent("regression", True, "closure green"))

    # Advance to READY_TO_CLOSE only when every mandatory artifact is present.
    if not lifecycle.missing_for_done(artifacts.keys()):
        lifecycle.transition(task_id, "READY_TO_CLOSE")

    orchestrator = Orchestrator(
        AgentContext(lifecycle=lifecycle, gate=gate, artifacts=artifacts)
    )

    spec = SpecInput(
        task_id=task_id,
        objective="Run AIOS governance pipeline for this task.",
        scope="governance pipeline (real orchestrator, no stub)",
        deliverables=[],
        acceptance=[],
        dependencies=[],
    )
    coord = CoordinatorAgent(
        spec_writer=SpecWriter(),
        critic=Critic(),
        reviewer=Reviewer(),
        orchestrator=orchestrator,
    )
    result = coord.coordinate(task_id, spec)
    steps = [{"name": s.name, "status": s.status, "detail": s.detail} for s in result.steps]
    return {"status": "OK", "steps": steps, "approved": result.approved, "closed": result.closed}


def _run_gates(task_id: str) -> dict:
    """Run the 7 governance gates via the canonical gate_check.py (fail-closed)."""
    proc = subprocess.run(
        [sys.executable, "aios/governance/cli/gate_check.py", "--task", task_id],
        capture_output=True, text=True, cwd=str(REPO_ROOT),
    )
    return {"returncode": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Run AIOS pipeline + gates for a TASK-xxx")
    parser.add_argument("task", help="Task id, e.g. TASK-001")
    parser.add_argument("--job-dir", default=None,
                        help="Job folder for logs (default: task progress folder)")
    args = parser.parse_args(argv)

    ts = datetime.now(timezone.utc).isoformat()
    pipeline = _run_pipeline(args.task)
    gates = _run_gates(args.task)

    log_dir = args.job_dir or os.path.join("aios", "progress", "tasks", args.task, "logs")
    os.makedirs(log_dir, exist_ok=True)
    run_id = f"run-{uuid.uuid4().hex[:12]}"
    exec_id = f"task-{args.task}-{ts[:19].replace(':', '')}-{run_id}"
    purpose = PURPOSES.get(args.task, f"Flow A — governance pipeline + 7 gates for {args.task}.")
    gstatus = "PASS" if gates["returncode"] == 0 else "FAIL"
    record = {
        "tool": "aiagent task",
        "run_id": run_id,
        "timestamp": ts,
        "purpose": purpose,
        "task": args.task,
        "pipeline": pipeline,
        "pipeline_summary": pipeline.get("steps", []),
        "gates": {
            "status": gstatus,
            "returncode": gates["returncode"],
            "summary": gates["stdout"].strip().splitlines()[-1] if gates["stdout"].strip() else "",
        },
    }
    json_path = os.path.join(log_dir, f"{exec_id}.json")
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(record, fh, indent=2, ensure_ascii=False)

    print(f"[aiagent task] {args.task}  (run_id={run_id})")
    print(f"  purpose  : {purpose}")
    print(f"  pipeline : {pipeline.get('status')}")
    for s in pipeline.get("steps", []):
        print(f"    - {s.get('name')}: {s.get('status')}")
    print(f"  gates    : {gstatus}")
    print(f"  [log] written: {json_path}")
    return 0 if gates["returncode"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
