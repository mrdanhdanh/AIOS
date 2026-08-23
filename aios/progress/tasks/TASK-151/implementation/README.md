# TASK-151 — Implementation

Module: `aios/coding_loop/verification_gate.py`

Exports:
- `VerificationGate` — fail-closed verification gate.
- `VerificationResult` — immutable-by-id verification result (`result_id`, `progress_ref`, `verification_result`, `integrity_verified`, `evidence_ref`, `authority="aios"`).
- `VerifyStatus` — PASS / FAIL / INCONCLUSIVE.

Key invariants:
- `verify()` fail-closed: requires progress report with `evidence_ref` (T001 Rule 5).
- `result_id` immutable (T001 Rule 1).
- No output hash → INCONCLUSIVE; regression → FAIL (never promoted, T078).
- Deterministic: same output → same result.
- `provenance()` carries `content_hash` (T078).

Integration: built on Progress/Regression Detection T150 + Verification Engine T142 + Integrity T078 + Evidence T001.
