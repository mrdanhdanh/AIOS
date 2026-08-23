# TASK-165 — Adversarial Evaluation Harness

## Objective
Aggregates attack results into an adversarial resilience report. Deterministic, fail-closed: any attack with no provenance is rejected; a BREACH is never promoted to PASS (T078).

## Scope
- Package: `aios/adversarial/` (unknown/infra layer, deterministic-first, fail-closed, provenance-bearing).
- Module: `aios/adversarial/adversarial_evaluation.py` — class `AdversarialEvaluationHarness`.
- No LLM, no I/O, no provider/filesystem imports (ARCH-001..004 N/A for unknown layer).

## Deliverables
- Implementation + contract/schema + deterministic tests + evidence + documentation.

## Acceptance Criteria
- AttackResult/AdversarialReport immutable with non-empty attack_id (Rule 1).
- evaluate aggregates: BREACH present -> INSUFFICIENT; UNKNOWN present -> UNKNOWN; else PASS.
- Empty attack_id or non-AttackResult input raises AdversarialError (fail-closed).
- BREACH/UNKNOWN never promoted to PASS (T078 integrity invariant).
- report_id deterministic (sha256 of attack_id:status pairs).

## Dependencies
- T001 (Evidence/Rule 1/5/6), T078 (Integrity), T164 (Verification Harness), T033 (Regression).
