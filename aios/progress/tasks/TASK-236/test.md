# TASK-236 — Test

- `test_lifecycle_runs_to_done_with_low_risk_candidate`: low-risk candidate → DONE/APPLIED, simulation PASS, integrity pass.
- `test_lifecycle_escalates_without_traceable_diagnosis`: không symptom → DIAGNOSED, escalated, success=False.
- `test_lifecycle_halts_under_kill_switch`: halt active → HALTED, halted=True.
- `test_lifecycle_deterministic_same_inputs`: cùng input → cùng remediation_id/phase/success.

Kết quả: 4 passed.
