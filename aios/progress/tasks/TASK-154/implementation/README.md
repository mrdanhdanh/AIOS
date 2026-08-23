# TASK-154 — Implementation

Module: `aios/coding_loop/harness.py`

Exports:
- `AutonomousCodingHarness` — drives the full coding loop T145→T153 end-to-end, fail-closed.
- `CodingHarnessRun` — immutable-by-id harness run record (`run_id`, `loop_ref`, `safety_ref`, `test_ref`, `eval_ref`, `evidence_ref`, `status`, `authority="aios"`).
- `HarnessStatus` — PASS / FAIL.

Key invariants:
- `run()` fail-closed: any break in the loop (UNKNOWN diagnosis, regression, snapshot mismatch, kill switch) → FAIL (never promoted, T078).
- `run_id` immutable (T001 Rule 1); duplicate → rejected.
- Deterministic: same input → same output (T029/T079).
- `provenance()` carries `content_hash` (T078).

Integration: built on toàn bộ M21 (T145→T153) + Harness Kernel T029 + Test Harness T031 + Evaluation Harness T032 + Evidence T001.
