# TASK-160 — Security Verifier

## Objective
Deterministic security gate: any finding at blocking severity (high/critical) fails verification. Fail-closed: a scan with no provenance is rejected; blocking findings -> INSUFFICIENT.

## Scope
- Package: `aios/verification/` (unknown/infra layer, deterministic-first, fail-closed, provenance-bearing).
- Module: `aios/verification/security.py` — class `SecurityVerifier`.
- No LLM, no I/O, no provider/filesystem imports (ARCH-001..004 N/A for unknown layer).

## Deliverables
- Implementation + contract/schema + deterministic tests + evidence + documentation.

## Acceptance Criteria
- SecurityScan/SecurityReport immutable with non-empty scan_id (Rule 1).
- verify gates on high/critical findings (case-insensitive); PASS when none.
- Empty scan_id or non-SecurityScan input raises VerificationError (fail-closed).
- Blocking findings -> status INSUFFICIENT (never promoted).
- report_id deterministic (sha256 of inputs).

## Dependencies
- T001 (Evidence/Rule 1/5/6), T078 (Integrity), T033 (Regression), T144 (Execution Evidence).
