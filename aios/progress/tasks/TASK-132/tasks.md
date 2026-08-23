# Breakdown — TASK-132

1. `aios/coder/autonomy.py` — `AutonomyLevel` (3 mức) + `_LEVEL_OPS` map.
2. `AutonomyPermissionBroker` — `check()` fail-closed (T113), `require()` raise khi denied.
3. `PermissionDecision` — allowed/reason + `evidence_id` + `content_hash` (T001 Rule 5).
4. Policy boundary: `policy_ok=False` → denied.
5. Tests (9) theo Test Matrix TASK-132 + architecture guard.
6. Tích hợp: T125→T131 -> T132 (M19).
