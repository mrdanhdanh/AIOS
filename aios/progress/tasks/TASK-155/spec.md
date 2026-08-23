# TASK-155 — Requirement -> Evidence Mapping

## Objective
Maps requirements to collected evidence with deterministic coverage measurement. Fail-closed: a requirement with no provenance cannot be mapped; UNKNOWN coverage is never promoted to PASS.

## Scope
- Package: `aios/verification/` (unknown/infra layer, deterministic-first, fail-closed, provenance-bearing).
- Module: `aios/verification/requirement_evidence.py` — class `RequirementEvidenceMapper`.
- No LLM, no I/O, no provider/filesystem imports (ARCH-001..004 N/A for unknown layer).

## Deliverables
- Implementation + contract/schema + deterministic tests + evidence + documentation.

## Acceptance Criteria
- Requirement/EvidenceLink/MappingReport are immutable with non-empty ids (Rule 1).
- map_requirement computes coverage_ratio = linked/total evidence; PASS when >= 0.5 threshold.
- Empty evidence_ref or non-Requirement input raises VerificationError (fail-closed).
- Zero evidence -> status UNKNOWN (never promoted to PASS, T078).
- report_id is deterministic (sha256 of inputs, no clock).

## Dependencies
- T001 (Evidence/Rule 1/5/6), T078 (Integrity), T033 (Regression), T144 (Execution Evidence).
