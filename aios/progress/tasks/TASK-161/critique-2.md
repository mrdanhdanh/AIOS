# TASK-161 — Critique 2

## Focus: fail-closed invariants / provenance gaps
- Verifier is deterministic-first; LLM is never the default path (Rule 4).
- Fail-closed: missing provenance (empty id) raises VerificationError, never silently passes.
- UNKNOWN is never promoted to PASS (T078 integrity invariant).
- Immutable ids enforce Rule 1 (unique/immutable task & artifact ids).
- Provenance chain: result -> requirement/scan/check -> evidence (Rule 5).
- No architecture violations: `aios/verification` is unknown layer.

## Verdict
Spec + implementation satisfy the milestone acceptance criteria. No blocking gaps.
