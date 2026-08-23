# TASK-168 — Critique 2

## Focus: fail-closed invariants / provenance gaps
- Attacker is deterministic-first; LLM is never the default path (Rule 4).
- Fail-closed: missing provenance (empty id) raises AdversarialError, never silently passes.
- BREACH/UNKNOWN is never promoted to PASS (T078 integrity invariant).
- Immutable ids enforce Rule 1 (unique/immutable task & artifact ids).
- Provenance chain: result -> attack -> evidence (Rule 5).
- No architecture violations: `aios/adversarial` is unknown layer.

## Verdict
Spec + implementation satisfy the milestone acceptance criteria. No blocking gaps.
