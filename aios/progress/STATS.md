# AIOS Progress Stats

Auto-tracked metrics for the development system. Updated as tasks move through the lifecycle.

## Totals
- Tasks in master spec: 218 (TASK-001 … TASK-218)
- Milestones: M0 … M26
- Tasks with a progress folder: _(count folders under `tasks/`)_
- Tasks CLOSED (gate PASS): _(run `python aios/scripts/gate_check.py TASK-xxx`)_

## Governance health
- Registry uniqueness violations: 0 (enforced by `aios/governance/task_registry`)
- Architecture violations: 0 (enforced by `aios/governance/architecture`)
- Deterministic-first compliance: tracked per task via `EVIDENCE.md`

## How to refresh
```
python aios/scripts/parse_spec.py   # regenerate registry (Rule 1/2)
python aios/scripts/gate_check.py TASK-xxx   # per-task gate (Rule 6/5/7)
```
