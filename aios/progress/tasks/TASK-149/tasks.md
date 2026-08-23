# TASK-149 — Task Breakdown

1. Định nghĩa `RepairPlan` (immutable `plan_id`, `diagnostic_ref`, `patch_spec`, `rollback_ref`, `evidence_ref`).
2. `RepairPlanner.plan` fail-closed: yêu cầu diagnostic có provenance (T001 Rule 5) + rollback_ref (T055).
3. UNKNOWN diagnosis → reject (T078).
4. Deterministic `patch_spec` từ root cause.
5. `provenance()` (content_hash).
6. Tests (`test_repair.py`): 7 tests.
7. Chạy pytest + gate_check + full suite.
