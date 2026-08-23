# TASK-152 — Task Breakdown

1. Định nghĩa `PatchChain` (immutable `chain_id`, `verification_ref`, `context_ref`, `patch_links`, `snapshot_ref`, `evidence_ref`).
2. `ContextRefreshPatchChain.refresh_context` deterministic (cùng state → cùng context, T024).
3. `refresh_and_chain` fail-closed: snapshot mismatch (T137) → reject; unverified (T078) → reject.
4. `provenance()` (content_hash).
5. Tests (`test_patch_chain.py`): 7 tests.
6. Chạy pytest + gate_check + full suite.
