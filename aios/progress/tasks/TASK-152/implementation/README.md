# TASK-152 — Implementation

Module: `aios/coding_loop/patch_chain.py`

Exports:
- `ContextRefreshPatchChain` — deterministic context refresh + patch chain; fail-closed on mismatch.
- `PatchChain` — immutable-by-id patch chain (`chain_id`, `verification_ref`, `context_ref`, `patch_links`, `snapshot_ref`, `evidence_ref`, `authority="aios"`).

Key invariants:
- `refresh_and_chain()` fail-closed: requires verification result with `evidence_ref` (T001 Rule 5).
- `chain_id` immutable (T001 Rule 1).
- Snapshot before/after mismatch → rejected (T137).
- Only verified (PASS) output may be chained (T078).
- `refresh_context()` deterministic: same state → same context (T024).
- `provenance()` carries `content_hash` (T078).

Integration: built on Verification Gate T151 + Context Optimizer T024 + Workspace/Snapshot T137 + Evidence T001.
