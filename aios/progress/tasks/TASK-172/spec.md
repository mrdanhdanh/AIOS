# TASK-172 — Environment / Dependency Attackers

## Objective
Probe whether malicious dependencies are contained. Deterministic, fail-closed: a malicious dependency that is not blocked is BREACH; blocked malicious dep or clean dep is BLOCKED.

## Scope
- Package: `aios/adversarial/` (unknown/infra layer, deterministic-first, fail-closed, provenance-bearing).
- Module: `aios/adversarial/environment_dependency_attackers.py` — class `EnvironmentDependencyAttacker`.
- No LLM, no I/O, no provider/filesystem imports (ARCH-001..004 N/A for unknown layer).

## Deliverables
- Implementation + contract/schema + deterministic tests + evidence + documentation.

## Acceptance Criteria
- EnvironmentDependencyAttack/Result immutable with non-empty attack_id (Rule 1).
- attack: breached = malicious_dep AND not blocked; BREACH when breached else BLOCKED.
- Empty attack_id or non-attack input raises AdversarialError (fail-closed).
- BREACH never promoted to PASS (T078).
- result_id deterministic (sha256 of inputs).

## Dependencies
- T001 (Evidence/Rule 1/5/6), T078 (Integrity), T164 (Verification Harness), T033 (Regression).
