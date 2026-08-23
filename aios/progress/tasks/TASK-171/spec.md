# TASK-171 — Execution Integrity Attackers

## Objective
Probe whether execution integrity holds under tamper. Deterministic, fail-closed: a tamper attempt that passes integrity verification is BREACH; detected tamper or no tamper is BLOCKED.

## Scope
- Package: `aios/adversarial/` (unknown/infra layer, deterministic-first, fail-closed, provenance-bearing).
- Module: `aios/adversarial/execution_integrity_attackers.py` — class `ExecutionIntegrityAttacker`.
- No LLM, no I/O, no provider/filesystem imports (ARCH-001..004 N/A for unknown layer).

## Deliverables
- Implementation + contract/schema + deterministic tests + evidence + documentation.

## Acceptance Criteria
- ExecutionIntegrityAttack/Result immutable with non-empty attack_id (Rule 1).
- attack: breached = tamper_attempt AND integrity_verified; BREACH when breached else BLOCKED.
- Empty attack_id or non-attack input raises AdversarialError (fail-closed).
- BREACH never promoted to PASS (T078).
- result_id deterministic (sha256 of inputs).

## Dependencies
- T001 (Evidence/Rule 1/5/6), T078 (Integrity), T164 (Verification Harness), T033 (Regression).
