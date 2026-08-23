# TASK-161 — Performance Verifier

## Objective
Deterministic performance budget check: observed must be within limit. Fail-closed: a budget with no provenance is rejected; over-budget -> INSUFFICIENT.

## Scope
- Package: `aios/verification/` (unknown/infra layer, deterministic-first, fail-closed, provenance-bearing).
- Module: `aios/verification/performance.py` — class `PerformanceVerifier`.
- No LLM, no I/O, no provider/filesystem imports (ARCH-001..004 N/A for unknown layer).

## Deliverables
- Implementation + contract/schema + deterministic tests + evidence + documentation.

## Acceptance Criteria
- PerfBudget/PerfReport immutable with non-empty budget_id (Rule 1).
- verify returns within_budget = observed <= limit; PASS when within.
- Empty budget_id or non-PerfBudget input raises VerificationError (fail-closed).
- Over-budget -> status INSUFFICIENT (never promoted).
- report_id deterministic (sha256 of inputs).

## Dependencies
- T001 (Evidence/Rule 1/5/6), T078 (Integrity), T033 (Regression), T144 (Execution Evidence).
