# TASK-066 — Test

## How to run
```
python -m pytest aios/durable -q
```

## What is covered
- **AC1 / Matrix "restart"**: `test_checkpoint_persists_across_restart`, `test_store_recovers_multiple_checkpoints_after_restart` — checkpoint durable qua restart (file-backed store).
- **AC2 / Matrix "unverified checkpoint"**: `test_resume_only_from_verified`, `test_resume_fail_closed_on_unverified_only`, `test_resume_fail_closed_on_no_checkpoints`, `test_can_resume_probe` — fail-closed, chỉ resume từ verified.
- **AC3 / Matrix "resume done step"**: `test_idempotency_no_double_execute`, `test_resume_done_step_idempotent` — không double side-effect.
- **AC4 / Matrix "checkpoint has evidence"**: `test_checkpoint_has_evidence` — provenance đầy đủ, round-trip giữ `evidence_ref`.
- **AC5 / Matrix "same checkpoint + protocol"**: `test_deterministic_resume`, `test_checkpoint_content_hash_deterministic` — deterministic.
- **AC6 / AC7**: `test_integration_with_runtime_state`, `test_reuses_runtime_state_store_hash` — tích hợp T065/T055, reuse runtime state store (không song song).
- **Matrix "crash mid-step"**: `test_crash_mid_step_resume_from_verified` — resume từ verified gần nhất.

Kết quả: **14 passed**.
