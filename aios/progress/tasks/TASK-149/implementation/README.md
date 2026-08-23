# TASK-149 — Implementation

Module: `aios/coding_loop/repair.py`

Exports:
- `RepairPlanner` — deterministic repair planner; fail-closed on missing rollback / UNKNOWN.
- `RepairPlan` — immutable-by-id repair plan (`plan_id`, `diagnostic_ref`, `patch_spec`, `rollback_ref`, `evidence_ref`, `authority="aios"`).

Key invariants:
- `plan()` fail-closed: requires diagnostic report with `evidence_ref` (T001 Rule 5) and `rollback_ref` (T055).
- `plan_id` immutable (T001 Rule 1).
- UNKNOWN diagnosis → rejected (T078).
- Deterministic: same diagnosis → same patch spec.
- `provenance()` carries `content_hash` (T078).

Integration: built on Diagnostic Agent T148 + Planning Engine T026 + Autonomous Recovery T055 + Evidence T001.
