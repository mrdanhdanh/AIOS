# TASK-168 — Test Report

## Suite
`aios/adversarial/tests/test_requirement_scope_attackers.py`

## Cases (7, all deterministic)
1. Construction / immutable id guard.
2. Happy path -> BLOCKED (attack contained).
3. Fail-closed: empty provenance id raises AdversarialError.
4. Breach path -> BREACH (attack succeeds).
5. Wrong-type input rejected.
6. Boundary / direction-aware case.
7. Deterministic result id (same inputs -> same id).

## Result
7 passed.
