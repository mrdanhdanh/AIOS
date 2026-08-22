# TASK-063 — AIOS Architecture 1.0

## Objective
Freeze (không redesign) the AIOS architecture baseline 1.0: standardize and
officially record the layer contract `Agent → Orchestrator → Runtime →
Capability → Tool` (real order `api > agent > orchestrator > worker > runtime >
skill > capability > tool`) together with rules `ARCH-001..004` as a stable
reference ADR + codified Architecture Guard. TASK-063 is **documentation +
guard codification**, not a new runtime feature.

## Scope
- In: ADR doc, `baseline.py` frozen reference, guard hardening/verification,
  full test matrix, 9 progress artifacts.
- Out: any new runtime behavior, new layers, new providers.

## Deliverables
- `docs/adr/ADR-ARCH-1.0.md` — frozen baseline ADR (5 layers + ARCH-001..004 +
  freeze-safety principles).
- `aios/governance/architecture/baseline.py` — `ARCHITECTURE_VERSION="1.0"` and
  `frozen_layer_contract()` re-exporting `LAYER_ORDER`/`ARCH_RULES` from
  `guard.py` (single source of truth).
- `aios/governance/architecture/guard.py` — ARCH-001..004 fail-closed +
  deterministic (verified, no new behavior needed).
- `aios/governance/architecture/tests/test_baseline.py` — full T063 test matrix.
- 9 progress artifacts under `aios/progress/tasks/TASK-063/`.

## Acceptance Criteria
- AC1: Layer contract recorded officially (ADR).
- AC2: ARCH-001..004 codified in Architecture Guard.
- AC3: Violating import → ARCHITECTURE GATE FAIL (test PASS).
- AC4: Guard runs in CI before every DONE.
- AC5: Layer-contract change requires ADR + version bump (no silent change).
- AC6: Guard fail-closed (parse error → BLOCK).
- AC7: Guard deterministic (same source + version → same result).
- AC8: No second parallel layer introduced.
- AC9: Prior-milestone regression PASS; invariants intact.

## Dependencies
- TASK-062 (Autonomous Scheduler) — done.
- Feeds TASK-064 (Public Contract Freeze).

## Governance references
- Rule 3 (Architecture) via `aios/governance/architecture/*`.
- Rule 6 (Lifecycle) artifacts per `STATE_ARTIFACTS`.
