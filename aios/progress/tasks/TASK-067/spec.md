# TASK-067 — Autonomy Safety 1.0 (Bounded Autonomy)

## Objective
Establish **bounded autonomy** for goals/loops: assign a per-context autonomy
level (L0..L4), enforce a clear boundary via the Autonomy Governor (T054), and
apply a fail-closed SAFE_STOP policy when the boundary is violated. TASK-067 is
a *safety layer* on top of the Governor — it does **not** re-implement a
parallel autonomy controller.

## Scope
**In scope**
- `AutonomyContext` dataclass (level, allowed_surfaces, budget, escalate_on, evidence_ref).
- `AutonomyLevelRegistry` (assign/get; raise level only via policy + human approval).
- Boundary check delegated to Governor (T054); out-of-boundary → BLOCK.
- SAFE_STOP fail-closed policy; hook into Kill Switch (T068) if present, else define `SafeStopSignal`.
- Integration with Governor (T054), Recovery (T055), Stuck (T061).

**Out of scope**
- A new autonomy controller (use Governor T054).
- Kill Switch implementation (T068) — only a hook + signal type.

## Deliverables
- New package `aios/autonomy_safety/` (`__init__.py`, `contracts.py`, `registry.py`, `boundary.py`, `safe_stop.py`).
- `implementation/` README pointer to the real module.
- Pytest suite `aios/autonomy_safety/tests/` covering every AC + Test Matrix row.

## Acceptance Criteria
- AC1: Every goal/loop has an autonomy level assigned + clear boundary.
- AC2: Action out of boundary → BLOCK via Governor (T054).
- AC3: Autonomy level only raised via policy (+ human approval if required).
- AC4: Boundary violated → SAFE_STOP (fail-closed).
- AC5: Same autonomy context + action → same decision (deterministic).
- AC6: Integrates with Governor (T054) + Kill Switch (T068) hook.
- AC7: No parallel autonomy controller — Governor (T054) is the authority.
- AC8: No regression of prior milestones; no invariant violations.

## Dependencies
- TASK-054 Autonomy Governor (boundary authority).
- TASK-055 Autonomous Recovery (SAFE_STOP alignment).
- TASK-061 Stuck Detection (safe-stop trigger source).
- TASK-066 Durable Execution (prerequisite milestone).
- TASK-068 Kill Switch (downstream; hook only).

## Governance references
- Rule 3 (Architecture): `autonomy_safety` is an `unknown`-layer package; imports only downward/peer packages (`autonomy_governor`, `autonomous_recovery`, `stuck_detection`); never `agents/`.
- Rule 4 (Deterministic): no LLM calls; decisions are pure functions of context+action.
- Rule 5 (Evidence): `SafeStopSignal` carries `evidence_ref` provenance.
