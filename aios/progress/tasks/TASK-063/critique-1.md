# TASK-063 — Critique 1

## Strengths
- Scope is correctly limited to freeze + document; no runtime feature creep.
- Existing `guard.py` already implements ARCH-001..004 fail-closed + deterministic
  via pure AST scanning — minimal new code required.
- `LAYER_ORDER` already matches the real frozen order
  (`api>agent>orchestrator>worker>runtime>skill>capability>tool`).

## Risks / Gaps
- `baseline.py` must NOT redefine layer rules (single source of truth risk) — it
  must re-export from `guard.py`.
- Test matrix must explicitly cover `tool → runtime` (ARCH-004) and determinism,
  which are not all asserted in one place.
- "No parallel architecture" (AC8) is a process guarantee, not a runtime check —
  document it as a principle, not a testable gate.

## Required revisions
- Add `ARCHITECTURE_VERSION="1.0"` + `frozen_layer_contract()` re-exporting
  `guard.py` constants (no duplication).
- Add `test_baseline.py` covering the full matrix incl. ARCH-004 skip-layer and
  determinism.
- Record freeze-safety principles (no-silent-change / fail-closed / deterministic /
  no-parallel-architecture) in the ADR.
