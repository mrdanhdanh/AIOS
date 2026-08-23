# TASK-156 — Test Adequacy Analyzer + Mutation Verifier

## Objective
Deterministic mutation scoring: mutation_score = killed / total mutants. Fail-closed: a suite with no provenance is rejected; UNKNOWN is never promoted to PASS.

## Scope
- Package: `aios/verification/` (unknown/infra layer, deterministic-first, fail-closed, provenance-bearing).
- Module: `aios/verification/test_adequacy.py` — class `TestAdequacyAnalyzer`.
- No LLM, no I/O, no provider/filesystem imports (ARCH-001..004 N/A for unknown layer).

## Deliverables
- Implementation + contract/schema + deterministic tests + evidence + documentation.

## Acceptance Criteria
- MutationSuite/AdequacyReport immutable with non-empty suite_id (Rule 1).
- analyze returns mutation_score = killed/mutants; PASS when >= 0.5 threshold.
- killed > mutants or empty suite_id raises VerificationError (fail-closed).
- Zero mutants -> status UNKNOWN (never promoted, T078).
- report_id deterministic (sha256 of inputs).

## Dependencies
- T001 (Evidence/Rule 1/5/6), T078 (Integrity), T033 (Regression), T144 (Execution Evidence).
