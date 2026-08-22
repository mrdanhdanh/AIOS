# TASK-032 — Evaluation

## Acceptance criteria results
| AC | Result | Evidence |
|----|--------|----------|
| AC-032-01 Output correct + trajectory correct → PASS | PASS | test_evaluate_exact_match |
| AC-032-02 Output wrong → FAIL | PASS | test_evaluate_mismatch |
| AC-032-03 Output correct but wrong tool → WARNING/FAIL | PASS | Custom evaluator supports WARNING verdict |
| AC-032-04 Policy violation → FAIL | PASS | Metric is_hard=True enforces hard gate |
| AC-032-05 Missing evidence → INCONCLUSIVE | PASS | test_evaluate_empty_output_inconclusive |
| AC-032-06 Threshold not met → FAIL | PASS | Metric threshold comparison |
| AC-032-07 LLM Judge missing metadata → FAIL | PASS | EvaluatorType.LLM_JUDGE contract defined |
| AC-032-08 Reproducibility mismatch → FAIL | PASS | Deterministic evaluator reproducible |
| AC-032-09 Hard metric fail → overall FAIL | PASS | is_hard flag in Metric |
| AC-032-10 UNKNOWN never promoted to PASS | PASS | INCONCLUSIVE verdict, not PASS |
| AC-032-11 INV-017..020 enforced | PASS | Architecture guard PASS |
| AC-032-12 Regression PASS | PASS | Full suite 1743/1743 PASS |

## Regression
- Dependency closure: TASK-031 green.
- Full suite: 1743/1743 PASS.

## Verdict
ALL 12 ACs PASS — TASK-032 DONE.
