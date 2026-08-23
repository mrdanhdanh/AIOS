# TASK-157 — Behavioral Verifier

## Objective
Deterministic behavioral equivalence check: expected == actual. Fail-closed: a spec with no provenance is rejected; mismatch is INSUFFICIENT, never silently promoted.

## Scope
- Package: `aios/verification/` (unknown/infra layer, deterministic-first, fail-closed, provenance-bearing).
- Module: `aios/verification/behavioral.py` — class `BehavioralVerifier`.
- No LLM, no I/O, no provider/filesystem imports (ARCH-001..004 N/A for unknown layer).

## Deliverables
- Implementation + contract/schema + deterministic tests + evidence + documentation.

## Acceptance Criteria
- BehaviorSpec/BehaviorReport immutable with non-empty spec_id (Rule 1).
- verify returns match = (expected == actual); PASS on match.
- Empty spec_id or non-BehaviorSpec input raises VerificationError (fail-closed).
- Mismatch -> status INSUFFICIENT (never promoted to PASS).
- report_id deterministic (sha256 of inputs).

## Dependencies
- T001 (Evidence/Rule 1/5/6), T078 (Integrity), T033 (Regression), T144 (Execution Evidence).
