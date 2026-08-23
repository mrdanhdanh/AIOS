# TASK-159 — Regression Verifier

## Objective
Deterministic regression detection: a metric regresses when current is worse than baseline (direction-aware). Fail-closed: a check with no provenance is rejected; regression -> INSUFFICIENT.

## Scope
- Package: `aios/verification/` (unknown/infra layer, deterministic-first, fail-closed, provenance-bearing).
- Module: `aios/verification/regression.py` — class `RegressionVerifier`.
- No LLM, no I/O, no provider/filesystem imports (ARCH-001..004 N/A for unknown layer).

## Deliverables
- Implementation + contract/schema + deterministic tests + evidence + documentation.

## Acceptance Criteria
- RegressionCheck/RegressionReport immutable with non-empty check_id (Rule 1).
- verify is direction-aware via higher_is_better; PASS when not regressed.
- Empty check_id or non-RegressionCheck input raises VerificationError (fail-closed).
- Regression -> status INSUFFICIENT (never promoted).
- report_id deterministic (sha256 of inputs).

## Dependencies
- T001 (Evidence/Rule 1/5/6), T078 (Integrity), T033 (Regression), T144 (Execution Evidence).
