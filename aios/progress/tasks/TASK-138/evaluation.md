# TASK-138 — Evaluation

| AC | Status | Evidence |
|----|--------|----------|
| Resource limit cpu/mem (T039) | PASS | `test_evaluate_deny_cpu`, `test_evaluate_deny_mem` |
| Network egress allow/deny (T040) | PASS | `test_evaluate_deny_network` |
| Command allow/deny | PASS | `test_evaluate_deny_command` |
| Vi phạm -> BLOCK (fail-closed, T078) | PASS | `evaluate` returns DENY |
| Provenance (T001 Rule 5) | PASS | `provenance()` content_hash |
| Cùng policy + request -> cùng decision | PASS | deterministic `evaluate` |
| Regression milestone trước PASS | PASS | full suite 2738 passed |

Verdict: DONE.
