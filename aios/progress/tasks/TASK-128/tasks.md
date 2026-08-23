# Breakdown — TASK-128

1. `aios/coder/patch.py` — `PatchEngine` (diff + apply + rollback).
2. `diff()` — unified diff, deterministic (cùng artifact + target → cùng diff).
3. `apply()` — backup-before-apply (T020); exception → rollback to certified (T020/T066), fail-closed.
4. `PatchRun` — `content_hash` (sha256, T078) + `evidence_id` (T001 Rule 5) + `backup_ref`.
5. Policy boundary: `policy_ok=False` → `PatchError` (T113).
6. Tests (8) theo Test Matrix TASK-128 + architecture guard.
7. Tích hợp: T127 -> T128 -> T129/T130 (M19).
