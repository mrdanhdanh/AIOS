# TASK-060 Implementation

## Modules
- `contracts.py` — `Decision`, `DecisionPolicy` (policy-driven mapping), `EvaluationRecord`.
- `evaluator.py` — `StepEvaluator` (reuses Harness T030/T032; missing evidence → INCONCLUSIVE), `DecisionMapper` (EvalVerdict → candidate via policy), `LoopGate` (Governor authorize + autonomy budget), `evaluate_step` (end-to-end).

## Design notes
- Three distinct tiers: Evaluator (verdict) ≠ DecisionMapper (candidate) ≠ LoopGate (allowed?). The Governor decides *permission*, never the verdict.
- Fail-closed: INCONCLUSIVE/UNKNOWN never auto-promote to PASS.
- Deterministic: same normalized input + evidence snapshot + evaluator version + policy version → same verdict.
