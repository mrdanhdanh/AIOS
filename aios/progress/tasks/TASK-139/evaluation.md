# TASK-139 — Evaluation

| AC | Status | Evidence |
|----|--------|----------|
| Chạy test trong sandbox (T136) + workspace (T137) | PASS | `test_run_pass_in_sandbox` |
| Vi phạm policy -> BLOCK (fail-closed, T078) | PASS | `test_run_policy_denied` |
| Result có `content_hash` (T078) + provenance | PASS | `test_result_has_hash` |
| Không chạy ngoài sandbox (T136/T040) | PASS | `test_run_outside_sandbox_blocked` |
| Cùng suite + env -> cùng result | PASS | `test_deterministic_same_env` |
| Regression milestone trước PASS | PASS | full suite 2738 passed |

Verdict: DONE.
