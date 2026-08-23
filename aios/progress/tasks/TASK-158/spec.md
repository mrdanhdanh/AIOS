# TASK-158 — Contract Verifier

## Objective
Deterministic contract verification: every precondition and postcondition must hold against observed values. Fail-closed: a contract with no provenance is rejected; any violation -> INSUFFICIENT.

## Scope
- Package: `aios/verification/` (unknown/infra layer, deterministic-first, fail-closed, provenance-bearing).
- Module: `aios/verification/contract.py` — class `ContractVerifier`.
- No LLM, no I/O, no provider/filesystem imports (ARCH-001..004 N/A for unknown layer).

## Deliverables
- Implementation + contract/schema + deterministic tests + evidence + documentation.

## Acceptance Criteria
- Contract/ContractReport immutable with non-empty contract_id (Rule 1).
- verify enumerates precondition/postcondition violations; PASS when none.
- Empty contract_id or non-Contract input raises VerificationError (fail-closed).
- Any violation -> status INSUFFICIENT (never promoted).
- report_id deterministic (sha256 of inputs).

## Dependencies
- T001 (Evidence/Rule 1/5/6), T078 (Integrity), T033 (Regression), T144 (Execution Evidence).
