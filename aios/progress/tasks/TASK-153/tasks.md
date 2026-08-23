# TASK-153 — Task Breakdown

1. Định nghĩa `SafetyDecision` (immutable `decision_id`, `chain_ref`, `boundary_status`, `kill_switch`, `guardrail_ref`, `evidence_ref`).
2. `AutonomousSafetyController.evaluate` fail-closed: yêu cầu patch chain có provenance (T001 Rule 5).
3. Boundary violation → `kill_switch=True` (T068).
4. Deterministic decision (cùng state → cùng decision).
5. `provenance()` (content_hash).
6. Tests (`test_safety.py`): 7 tests.
7. Chạy pytest + gate_check + full suite.
