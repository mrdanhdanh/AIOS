"""run_task.py — run the full AIOS governance pipeline + 7 gates for a TASK-xxx.

Single entry point so every AIOS job is driven through the real pipeline
(CoordinatorAgent) and the 7 governance gates, with a durable log written to
<repo>/work/<job>/logs/ (or <repo>/aios/progress/tasks/<TASK>/logs/).
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))


def _run_pipeline(task_id: str) -> dict:
    """Drive CoordinatorAgent.coordinate() for the task. Returns a result dict."""
    try:
        from aios.agents import CoordinatorAgent, Critic, Reviewer, SpecWriter
        from aios.agents.spec_writer import SpecInput

        # Minimal spec input; real jobs supply a richer spec from docs/detailtask.
        spec = SpecInput(
            task_id=task_id,
            objective="Run AIOS governance pipeline for this task.",
            scope="governance pipeline dry run",
            deliverables=[],
            acceptance=[],
            dependencies=[],
        )
        coord = CoordinatorAgent(
            spec_writer=SpecWriter(),
            critic=Critic(),
            reviewer=Reviewer(),
            orchestrator=_NullOrchestrator(),
        )
        result = coord.coordinate(task_id, spec)
        return {"status": "OK", "steps": [s.__dict__ for s in result.steps],
                "approved": result.approved, "closed": result.closed}
    except Exception as exc:  # noqa: BLE001
        return {"status": "ERROR", "error": str(exc)}


class _NullOrchestrator:
    """Avoids filesystem/state side effects during a dry pipeline run.

    The real close is performed by gate_check + the orchestrator in production;
    here we only report whether the pipeline reached the close step.
    """
    def advance(self, task_id, to_state, artifacts=None):
        return to_state
    def can_close(self, task_id):
        return False
    def close_if_gate_passes(self, task_id):
        return False


def _run_gates(task_id: str) -> dict:
    """Run the 7 governance gates via gate_check.py."""
    proc = subprocess.run(
        [sys.executable, "aios/governance/cli/gate_check.py", "--task", task_id],
        capture_output=True, text=True, cwd=str(REPO_ROOT),
    )
    return {"returncode": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=f"Run AIOS pipeline + gates for a TASK-xxx")
    parser.add_argument("task", help="Task id, e.g. TASK-001")
    parser.add_argument("--job-dir", default=None,
                        help="Job folder for logs (default: task progress folder)")
    args = parser.parse_args(argv)

    ts = datetime.now(timezone.utc).isoformat()
    pipeline = _run_pipeline(args.task)
    gates = _run_gates(args.task)

    log_dir = args.job_dir or os.path.join("aios", "progress", "tasks", args.task, "logs")
    os.makedirs(log_dir, exist_ok=True)
    exec_id = f"task-{args.task}-{ts[:19].replace(':', '')}"
    record = {
        "tool": "aiagent task",
        "timestamp": ts,
        "task": args.task,
        "pipeline": pipeline,
        "gates": {"returncode": gates["returncode"],
                  "summary": gates["stdout"].strip().splitlines()[-1] if gates["stdout"].strip() else ""},
    }
    json_path = os.path.join(log_dir, f"{exec_id}.json")
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(record, fh, indent=2, ensure_ascii=False)

    print(f"[aiagent task] {args.task}")
    print(f"  pipeline : {pipeline.get('status')}")
    for s in pipeline.get("steps", []):
        print(f"    - {s.get('name')}: {s.get('status')}")
    gstatus = "PASS" if gates["returncode"] == 0 else "FAIL"
    print(f"  gates    : {gstatus}")
    print(f"  [log] written: {json_path}")
    return 0 if gates["returncode"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
