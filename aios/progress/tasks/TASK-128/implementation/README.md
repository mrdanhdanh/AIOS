# TASK-128 Implementation

Patch Engine lives in:

- `aios/coder/patch.py` — `PatchEngine`, `PatchRun`, `PatchStatus`, `PatchError`.
- Tests trong `aios/coder/tests/test_patch.py` (8 tests, Test Matrix TASK-128).

Design:
- `PatchEngine.diff()` — unified diff, deterministic (cùng artifact + target → cùng diff).
- `PatchEngine.apply()` — backup-before-apply (T020); nếu `apply_fn` raise hoặc `policy_ok=False` → rollback to certified state (T020/T066), fail-closed (`PatchError`). Repository không bao giờ hỏng.
- `PatchRun` ghi `content_hash` (sha256, T078) + `evidence_id` (T001 Rule 5) + `backup_ref`.

Integration (import-level, no rewrite):
- `aios.coder.generation` (T127) — artifact input
- `aios.upgrade` (T020) — backup/migration semantics
- `aios.durable` (T066) — certified-state rollback
- `aios.verification_integrity` (T078) / `aios.governance.evidence` (T001)
- `aios.coder.patch` (T128) -> `aios.coder.review` (T129) / `aios.coder.artifact` (T130)
