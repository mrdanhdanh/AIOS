# TASK-163 — Evidence Collector + Evidence Integrity

## Objective
Deterministic evidence collection with content hashing and integrity verification. Fail-closed: collected evidence must carry a content hash; integrity check recomputes and compares (tamper -> INSUFFICIENT).

## Scope
- Package: `aios/verification/` (unknown/infra layer, deterministic-first, fail-closed, provenance-bearing).
- Module: `aios/verification/evidence_collector.py` — class `EvidenceCollector`.
- No LLM, no I/O, no provider/filesystem imports (ARCH-001..004 N/A for unknown layer).

## Deliverables
- Implementation + contract/schema + deterministic tests + evidence + documentation.

## Acceptance Criteria
- CollectedEvidence/IntegrityReport immutable with non-empty evidence_id (Rule 1).
- collect computes content_hash (sha256) and redacts secrets; verify_integrity recomputes.
- Empty source or empty evidence_id raises VerificationError (fail-closed).
- Tampered content -> integrity_ok False -> INSUFFICIENT (never promoted).
- evidence_id deterministic (sha256 of source+content).

## Dependencies
- T001 (Evidence/Rule 1/5/6), T078 (Integrity), T033 (Regression), T144 (Execution Evidence).
