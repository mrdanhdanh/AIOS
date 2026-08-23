# TASK-166 — Evidence Attackers

## Objective
Probe whether evidence can be tampered undetected. Deterministic, fail-closed: tampered-but-undetected is BREACH; detected tamper or no tamper is BLOCKED.

## Scope
- Package: `aios/adversarial/` (unknown/infra layer, deterministic-first, fail-closed, provenance-bearing).
- Module: `aios/adversarial/evidence_attackers.py` — class `EvidenceAttacker`.
- No LLM, no I/O, no provider/filesystem imports (ARCH-001..004 N/A for unknown layer).

## Deliverables
- Implementation + contract/schema + deterministic tests + evidence + documentation.

## Acceptance Criteria
- EvidenceAttack/EvidenceAttackResult immutable with non-empty attack_id (Rule 1).
- attack: breached = tampered AND not detected; BREACH when breached else BLOCKED.
- Empty attack_id or non-EvidenceAttack input raises AdversarialError (fail-closed).
- BREACH never promoted to PASS (T078).
- result_id deterministic (sha256 of inputs).

## Dependencies
- T001 (Evidence/Rule 1/5/6), T078 (Integrity), T164 (Verification Harness), T033 (Regression).
