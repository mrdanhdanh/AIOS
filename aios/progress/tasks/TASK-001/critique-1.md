# TASK-001 — Critique 1

## Strengths
- Maps each of the 7 rules to a concrete, testable component.
- Keeps the architecture guard decoupled from any specific test framework.
- Unified gate fails closed (exceptions -> FAIL).

## Risks / Gaps
- The deterministic path (Rule 4) could become a "god object" if every stage is
  hard-coded; keep stages injectable.
- Evidence provenance requires linked Run/Artifact/Task/Requirement records; if
  any link is missing the chain must be explicitly incomplete (not silently OK).
- Architecture layering must recognize the `agents/` directory as the `agent`
  layer (plural vs singular).

## Required revisions
- Make pipeline stages (Normalizer, RuleEngine, WorkflowMatcher, CapabilityResolver,
  Policy) injectable (done in design).
- Mark provenance `complete=False` when any link missing (done).
- Fix `classify_module` to map `agents -> agent` (done).
