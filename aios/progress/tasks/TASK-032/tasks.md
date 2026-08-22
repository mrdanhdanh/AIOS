# TASK-032 — Breakdown

## Steps
1. Create `aios/harness/evaluation.py` — Metric, EvaluationCase, EvaluationResult, EvalVerdict, EvaluatorType, EvaluationSuite
2. Implement EvaluationSuite: add_case, evaluate (with optional evaluator_fn), _default_evaluate (exact match, empty → INCONCLUSIVE)
3. Implement Metric with is_hard flag for hard gate enforcement
4. Implement provenance tracking via provenance list
5. Create `aios/harness/tests/test_evaluation.py` — 4 tests (exact match PASS, mismatch FAIL, empty INCONCLUSIVE, custom evaluator)
6. Run architecture guard — verify no Harness → Runtime implementation
7. Run full suite — 1743/1743 PASS (4 new), no regressions

## Dependencies
- TASK-031 Test Harness

## Exit Criteria
- All AC-032-01..12 PASS, gate PASS, no regressions
