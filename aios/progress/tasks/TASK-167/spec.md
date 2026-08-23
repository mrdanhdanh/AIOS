# TASK-167 — Test Weakness Attackers

## Objective
Probe whether tests are weak (a mutation survives). Deterministic, fail-closed: a surviving mutation is BREACH (weak test); a killed mutation is BLOCKED.

## Scope
- Package: `aios/adversarial/` (unknown/infra layer, deterministic-first, fail-closed, provenance-bearing).
- Module: `aios/adversarial/test_weakness_attackers.py` — class `TestWeaknessAttacker`.
- No LLM, no I/O, no provider/filesystem imports (ARCH-001..004 N/A for unknown layer).

## Deliverables
- Implementation + contract/schema + deterministic tests + evidence + documentation.

## Acceptance Criteria
- TestWeaknessAttack/TestWeaknessResult immutable with non-empty attack_id (Rule 1).
- attack: breached = not mutation_killed; BREACH when breached else BLOCKED.
- Empty attack_id or non-attack input raises AdversarialError (fail-closed).
- BREACH never promoted to PASS (T078).
- result_id deterministic (sha256 of inputs).

## Dependencies
- T001 (Evidence/Rule 1/5/6), T078 (Integrity), T164 (Verification Harness), T033 (Regression).
