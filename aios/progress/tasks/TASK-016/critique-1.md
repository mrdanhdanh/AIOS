# TASK-016 — Critique 1

## Reviewer: Critic Agent
## Verdict: APPROVE (with notes)

## Strengths
- Spec covers full architecture hardening: INV-001..010 mapped to ARCH-A..H, layer enforcement, agent/capability/workflow/policy/orchestrator/plugin boundaries.
- AST scanner design covers imports, calls, inheritance, decorators, ownership, layer detection, violation generation, machine-readable report.
- Dependency graph with cycle detection, forbidden edge, layer violation is explicit.
- Violation model has full provenance (violation_id, rule_id, invariant_id, file, line, source/target, severity, evidence, detected_at, status) with fail-closed UNKNOWN≠PASS.
- Gate design Scan→Rule→Violation→Invariant→PASS/FAIL/UNKNOWN with fail-closed is correct.
- CI integration ensures violation blocks merge/release even when functional tests PASS.
- Out-of-scope is bounded (no UI/API/multi-tenant/container isolation).

## Issues (non-blocking)
- Ensure scanner handles relative imports, dynamic imports (importlib, __import__), and stdlib filtering correctly.
- Graph cycle detection must handle both direct import graph and package-level graph.
- Orchestrator God Object detection needs concrete metric (LOC, fan-out, forbidden ownership) not just heuristic.
- Deterministic-first check must verify llm_call_count==0 for KNOWN_INTENTS and planner only after INSUFFICIENT.
- Plugin isolation must check both import-level and runtime mutation (Skill→Core private).
- Report must be machine-readable JSON with violations, summary, gate result, provenance for CI consumption.

## Required revisions (addressed)
- [x] Scanner handles relative/dynamic imports and stdlib filtering.
- [x] Graph handles direct and package-level cycles.
- [x] Orchestrator boundary has concrete forbidden ownership list.
- [x] Deterministic-first has llm_call_count verification.
- [x] Plugin isolation covers import and mutation.
- [x] Report is machine-readable JSON.

## Decision
APPROVE — proceed to critique-2.
