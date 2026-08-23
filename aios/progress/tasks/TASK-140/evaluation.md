# TASK-140 — Evaluation

| AC | Status | Evidence |
|----|--------|----------|
| Chạy build/lint trong sandbox (T136) + workspace (T137) | PASS | `test_build_pass` |
| Vi phạm policy -> BLOCK (fail-closed, T078) | PASS | `test_policy_denied` |
| Result có `content_hash` (T078) + provenance | PASS | `test_content_hash` |
| Không chạy ngoài sandbox (T136/T040) | PASS | `test_outside_sandbox_blocked` |
| Cùng target + env -> cùng result | PASS | `test_deterministic` |
| Regression milestone trước PASS | PASS | full suite 2738 passed |

Verdict: DONE.
