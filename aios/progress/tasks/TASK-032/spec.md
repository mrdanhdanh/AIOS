# TASK-032 — Evaluation Harness + Metrics

## Objective
Build the Evaluation Harness that assesses output and trajectory quality via an evaluator suite (Deterministic → Semantic → LLM Judge → Human → Composite). Evaluates final output, execution trajectory, tool usage, policy compliance, correctness, cost, latency, and token usage with evidence and provenance. LLM Judge is optional/fallback, not default.

## Scope
### In scope
- Evaluation contracts: EvaluationSuite, EvaluationCase, Evaluator, EvaluationInput, Metric, MetricResult, EvaluationResult, EvaluationReport
- EvaluationSuite with metrics (task_completion, correctness, policy_compliance, tool_accuracy, cost, latency) and thresholds
- Evaluator types: Deterministic (exact match, tests_pass, policy_violations==0), Semantic, LLM Judge (with model/prompt/temperature metadata), Human, Composite
- Trajectory evaluation (tool sequence, policy violations, recovery)
- Evidence and reproducibility (model version, prompt version, input hash, raw output)
- Integration with TASK-029 Kernel, TASK-030 Evidence, TASK-031 Scenarios

### Out of scope
- Benchmark/Regression Gate (TASK-033)
- Replacing Test Harness or Execution Verification
- Creating a parallel evaluation control plane

## Deliverables
- `aios/harness/evaluation.py` — EvaluationSuite, EvaluationCase, EvaluationResult, Metric, EvalVerdict, EvaluatorType
- `aios/harness/tests/test_evaluation.py` — evaluation tests

## Acceptance Criteria
- AC-032-01: Output correct + trajectory correct → PASS
- AC-032-02: Output wrong → FAIL
- AC-032-03: Output correct but wrong tool → WARNING/FAIL per policy
- AC-032-04: Policy violation → FAIL
- AC-032-05: Missing evidence → INCONCLUSIVE
- AC-032-06: Threshold not met → FAIL
- AC-032-07: LLM Judge missing metadata → FAIL
- AC-032-08: Reproducibility mismatch → FAIL
- AC-032-09: Hard metric fail → overall FAIL
- AC-032-10: UNKNOWN/INCONCLUSIVE never auto-promoted to PASS
- AC-032-11: INV-017..020 enforced
- AC-032-12: Regression M0–M5 + TASK-029/030/031 PASS

## Dependencies
- TASK-031 — Test Harness + Scenario + Simulation

## Governance references
- Rule 1..7 satisfied via `aios/governance/*`.
- INV-017 Harness Isolation, INV-018 Evidence First, INV-019 Verification Before Verdict, INV-020 Evaluation Determinism.
