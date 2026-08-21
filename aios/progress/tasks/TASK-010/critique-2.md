# TASK-010 — Critique 2 (Architecture & Test Review)

## Strengths
- Orchestrator package is pure Python, no LLM on fast path, offline-first.
- DecisionPipeline evidence chain `Request → NormalizedRequest → Decision → Workflow/Planner → ExecutionPlan` supports M6 harness trajectory verification.
- Governance `DeterministicControlPath` remains backward compatible; new orchestrator pipeline is the canonical M2 implementation.

## Risks / Gaps
- `aios/orchestrator` must not import `aios.agents` (layering: orchestrator may import runtime/capability/tool/unknown only). Verify via guard.
- Planner must not directly execute tools; it only produces ExecutionPlan.
- Policy checker must be injectable so tests can simulate DENY without real PolicyEngine.
- Tests must cover all 10 ACs distinctly, not just parametric copies: normalization stability, deterministic no LLM, workflow reuse, planner fallback, validation, policy, offline, evidence, architecture, regression.

## Required revisions
- [x] Verify orchestrator imports only runtime/capability/tool/unknown (no agent).
- [x] Ensure Planner never calls tool; only produces plan.
- [x] Add injectable policy_checker and capability_resolver to DecisionPipeline.
- [x] Create 7 test files covering AC-010-01..10 with ≥40 tests total.

## Decision
- APPROVE with required revisions addressed — proceed to review.
