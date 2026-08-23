# TASK-168 — Requirement / Scope Attackers

## Objective
Probe whether the agent exceeds its declared scope. Deterministic, fail-closed: an attempted scope differing from allowed scope is BREACH (scope escape); matching scope is BLOCKED.

## Scope
- Package: `aios/adversarial/` (unknown/infra layer, deterministic-first, fail-closed, provenance-bearing).
- Module: `aios/adversarial/requirement_scope_attackers.py` — class `RequirementScopeAttacker`.
- No LLM, no I/O, no provider/filesystem imports (ARCH-001..004 N/A for unknown layer).

## Deliverables
- Implementation + contract/schema + deterministic tests + evidence + documentation.

## Acceptance Criteria
- RequirementScopeAttack/RequirementScopeResult immutable with non-empty attack_id (Rule 1).
- attack: breached = attempted_scope != allowed_scope; BREACH when breached else BLOCKED.
- Empty attack_id or empty scope raises AdversarialError (fail-closed).
- BREACH never promoted to PASS (T078).
- result_id deterministic (sha256 of inputs).

## Dependencies
- T001 (Evidence/Rule 1/5/6), T078 (Integrity), T164 (Verification Harness), T033 (Regression).
