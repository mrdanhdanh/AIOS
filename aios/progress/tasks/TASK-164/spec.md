# TASK-164 — Trust Evaluator + CodingCertificate + Verification Harness

## Objective
Integration harness aggregating verifier results into a CodingCertificate and TrustReport. Deterministic, fail-closed: any verifier result not PASS lowers trust; UNKNOWN never promoted to PASS.

## Scope
- Package: `aios/verification/` (unknown/infra layer, deterministic-first, fail-closed, provenance-bearing).
- Module: `aios/verification/trust_certificate.py` — class `VerificationHarness`.
- No LLM, no I/O, no provider/filesystem imports (ARCH-001..004 N/A for unknown layer).

## Deliverables
- Implementation + contract/schema + deterministic tests + evidence + documentation.

## Acceptance Criteria
- CodingCertificate/TrustReport immutable with non-empty cert_id (Rule 1).
- TrustEvaluator.evaluate maps trust_score -> HIGH/MEDIUM/LOW/NONE; PASS at >= 0.8.
- VerificationHarness.run rejects empty subject/verifier name or invalid status (fail-closed).
- Any non-PASS result -> trust below HIGH (never promoted to PASS).
- report_id deterministic (sha256 of inputs).

## Dependencies
- T001 (Evidence/Rule 1/5/6), T078 (Integrity), T033 (Regression), T144 (Execution Evidence).
