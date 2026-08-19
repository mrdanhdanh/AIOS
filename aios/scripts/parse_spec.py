"""Generate the AIOS task registry + index from the master spec.

Enforces Rule 1 (unique/immutable IDs) and Rule 2 (milestone derivation).
Run:  python aios/scripts/parse_spec.py
"""
import sys
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]  # aios/
sys.path.insert(0, str(ROOT.parent))

from aios.governance.task_registry import parse_master_spec  # validates uniqueness

PROGRESS = ROOT / "progress"


def main():
    reg = parse_master_spec()
    tasks = [
        {
            "id": t.task_id,
            "num": int(t.task_id.split("-")[1]),
            "title": t.title,
            "milestone": t.milestone,
        }
        for t in reg.all()
    ]
    tasks.sort(key=lambda x: x["num"])

    registry = {"source": "docs/AIOS_Master_Task_Specification_M0-M26.md",
                "total": len(tasks), "tasks": tasks}
    PROGRESS.mkdir(parents=True, exist_ok=True)
    (PROGRESS / "task-registry.json").write_text(
        json.dumps(registry, indent=2, ensure_ascii=False), encoding="utf-8")

    # human index grouped by milestone
    by_ms = {}
    for t in tasks:
        by_ms.setdefault(t["milestone"], []).append(t)
    lines = ["# AIOS Task Index (generated)\n",
             f"Total tasks: {len(tasks)} — generated from master spec. DO NOT EDIT BY HAND.\n"]
    for ms in sorted(by_ms):
        lines.append(f"\n## {ms} ({len(by_ms[ms])} tasks)\n")
        for t in by_ms[ms]:
            lines.append(f"- [{t['id']}](tasks/{t['id']}/spec.md) — {t['title']}\n")
    (PROGRESS / "task-index.md").write_text("".join(lines), encoding="utf-8")

    print(f"OK: {len(tasks)} tasks registered; milestones: {sorted(by_ms)}")


if __name__ == "__main__":
    main()
