# TASK-060 — Breakdown

## Steps
1. `aios/autonomous_evaluation/contracts.py` — Decision, DecisionPolicy, EvaluationRecord.
2. `aios/autonomous_evaluation/evaluator.py` — StepEvaluator (Harness reuse), DecisionMapper (policy-driven), LoopGate (Governor authorize), evaluate_step.
3. `aios/autonomous_evaluation/tests/test_autonomous_evaluation.py` — 10 tests.
4. Run architecture guard — no subprocess/provider/filesystem import.
5. Run full suite — no regressions.

## Exit Criteria
- All AC-060-01..14 PASS, gate PASS, no regressions.
