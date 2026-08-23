# TASK-153 — Implementation

Module: `aios/coding_loop/safety.py`

Exports:
- `AutonomousSafetyController` — deterministic safety controller; fail-closed kill switch on violation.
- `SafetyDecision` — immutable-by-id safety decision (`decision_id`, `chain_ref`, `boundary_status`, `kill_switch`, `guardrail_ref`, `evidence_ref`, `authority="aios"`).

Key invariants:
- `evaluate()` fail-closed: requires patch chain with `evidence_ref` (T001 Rule 5).
- `decision_id` immutable (T001 Rule 1).
- Boundary violation → `kill_switch=True` (T068).
- Deterministic: same state → same decision.
- `provenance()` carries `content_hash` (T078).

Integration: built on Context Refresh + Patch Chain T152 + Autonomy Safety T067 + Kill Switch T068 + Evidence T001.
