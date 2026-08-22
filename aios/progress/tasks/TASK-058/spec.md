# TASK-058 — Autonomous Experimentation

## Objective
Build a capability to propose and run improvement experiments *under the existing Harness* (T029–T034) with verification + evaluation, reversible and fail-closed. The Experiment Controller only produces a `PromotionDecision` artifact — it never self-deploys a production change and never creates a sandbox/control plane of its own.

## Scope
### In scope
- `Experiment` contract: experiment_id, hypothesis, baseline_ref, baseline_version (immutable), candidate_ref, candidate_version (immutable), scenario_ref, metric_spec (validated, not LLM-defined), policy_scope, evidence_ref, evaluation_ref, status.
- Experiment Proposer: validates metric_spec is concrete (rejects vague/LLM-defined criteria).
- Harness Runner: runs candidate only in Harness execution context (no production side effect).
- Result Evaluator: A/B vs baseline via T032/T033.
- Promotion Decision: `PROMOTION_READY` artifact (not self-deploy).
- Promotion Gate (multi-dimensional): verified improvement (quality) AND no prohibited regression (cost/latency/failure) AND policy PASS.
- INCONCLUSIVE/UNKNOWN → NOT_PROMOTED (fail-closed, return to Governor/Loop).
- Anti-poisoning: only verified result → trusted memory (T057, INV-034).
- Autonomy-gated scope (T054); Governor deny → BLOCK.

### Out of scope
- Deployment/change mechanism, sandbox engine, evaluation engine, experiment DB, second control plane.

## Deliverables
- `aios/autonomous_experimentation/contracts.py` — Experiment, ExperimentStatus, MetricSpec, PromotionDecision.
- `aios/autonomous_experimentation/controller.py` — ExperimentController (propose/authorize/run/evaluate/promotion gate).
- `aios/autonomous_experimentation/tests/` — unit/contract/integration/architecture tests.

## Acceptance Criteria
- AC-058-01: Experiment defines hypothesis + validated metric_spec (not LLM-defined).
- AC-058-02: Baseline/candidate/scenario immutable/versioned; mutable version → BLOCK.
- AC-058-03: Experiment runs in Harness context, no production side effect.
- AC-058-04: Evaluation compares vs baseline via T032/T033.
- AC-058-05: Promotion only when verified improvement AND no prohibited regression AND policy PASS.
- AC-058-06: Quality up but cost/policy regression → NOT_PROMOTED.
- AC-058-07: INCONCLUSIVE/UNKNOWN → NOT_PROMOTED, return to Governor/Loop.
- AC-058-08: Unverified result → Memory NOT_TRUSTED (INV-034).
- AC-058-09: Promotion creates artifact, not self-deploy.
- AC-058-10: Governor deny → BLOCK.
- AC-058-11: No Experiment Runtime/Sandbox/Evaluation Engine/DB/Control Plane.
- AC-058-12: Regression M0–M8 PASS.

## Dependencies
- TASK-032 Evaluation Harness, TASK-033 Benchmark+Regression, T030 Verification, T054 Governor, T057 Memory, T055 Recovery

## Governance references
- Rule 1..7 satisfied via `aios/governance/*`.
