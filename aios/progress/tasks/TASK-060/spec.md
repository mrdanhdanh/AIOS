# TASK-060 — Autonomous Evaluation

## Objective
Build the **decision layer** for the Autonomous Loop: after each step/cycle, evaluate the outcome (via Harness T030/T032) and map the verdict to a *decision candidate*. The Governor (T054) then decides whether the agent is *allowed* to execute that decision. Evaluation ≠ Decision ≠ Governor — three distinct tiers, no second control plane.

## Scope
### In scope
- `EvaluationRecord` (step_id, verdict, decision_candidate, governor_verdict, evidence_ref, metrics, evaluator_version, policy_version).
- `Decision` (CONTINUE/REVISE/RECOVER/ESCALATE/SAFE_STOP/BLOCK).
- `DecisionPolicy` (policy-driven mapping, not 1:1 hard-coded).
- StepEvaluator: outcome reached? (reuse Harness T030/T032). Missing evidence → INCONCLUSIVE.
- DecisionMapper: EvalVerdict → decision candidate via Decision Policy.
- LoopGate: execute decision only when Governor authorizes + autonomy suffices.
- Fail-closed: INCONCLUSIVE/UNKNOWN never auto-promote to PASS.
- Deterministic: same normalized input + evidence snapshot + evaluator version + policy version → same verdict.

### Out of scope
- Execution layer, recovery engine, governor, memory engine, promotion of artifacts/knowledge/strategy.

## Deliverables
- `aios/autonomous_evaluation/contracts.py` — Decision, DecisionPolicy, EvaluationRecord.
- `aios/autonomous_evaluation/evaluator.py` — StepEvaluator, DecisionMapper, LoopGate, evaluate_step.
- `aios/autonomous_evaluation/tests/` — unit/contract/integration/architecture tests.

## Acceptance Criteria
- AC-060-01: Every step evaluated before continuing.
- AC-060-02: Evaluation ≠ Decision ≠ Governor (3 tiers).
- AC-060-03: INCONCLUSIVE → no promote; policy → ESCALATE/REVISE/SAFE_STOP.
- AC-060-04: FAIL (hard) → RECOVER (T055).
- AC-060-05: WARNING → policy-driven (CONTINUE/REVISE/ESCALATE/STOP), not hard-coded continue.
- AC-060-06: PASS → authorize continuation (not promote).
- AC-060-07: Next step from Execution Plan/Graph (M5 DAG), not linear cursor.
- AC-060-08: Decision respects autonomy level (budget exceeded → BLOCK).
- AC-060-09: Evaluation has evidence (missing → INCONCLUSIVE).
- AC-060-10: UNKNOWN/INCONCLUSIVE never auto-promote to PASS.
- AC-060-11: Deterministic (same input+versions → same verdict).
- AC-060-12: Integrates with Autonomous Loop (T053).
- AC-060-13: No second autonomous control plane.
- AC-060-14: Regression M0–M8 PASS.

## Dependencies
- TASK-030 Verification, TASK-032 Evaluation Harness, TASK-053 Autonomous Loop, TASK-054 Autonomy Governor

## Governance references
- Rule 1..7 satisfied via `aios/governance/*`.
