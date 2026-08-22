# TASK-060 — Critique 1

## Missing spec sections
- Three-tier separation (Evaluator/DecisionMapper/LoopGate) in `evaluator.py`.
- DecisionPolicy (policy-driven, not 1:1) in `contracts.py`.

## Risks
- Evaluation could become a second Governor. Mitigation: `LoopGate` only asks the injected Governor; it never decides the verdict.
- INCONCLUSIVE could be promoted. Mitigation: `StepEvaluator` returns INCONCLUSIVE on missing evidence; `DecisionMapper` maps it to ESCALATE/REVISE/SAFE_STOP, never CONTINUE.

## Verdict
Implementable. Proceed.
