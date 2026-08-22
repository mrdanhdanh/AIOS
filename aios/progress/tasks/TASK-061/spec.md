# TASK-061 — Advanced Stuck Detection

## Objective
Build a **stuck detection layer** for the Autonomous Loop that identifies stuck / loop / oscillation / plateau / resource-burn / deadlock states and triggers fail-closed escalation. Detect ≠ Decide ≠ Recover: the detector emits a signal, the Stuck Policy maps it to a candidate action, and the Governor (T054) / Recovery (T055) decide whether the action is *allowed*.

## Scope
### In scope
- `StuckSignal` (kind, severity, iteration_first_seen, confidence, evidence_ref). Kinds: NO_PROGRESS / OSCILLATION / PLATEAU / RESOURCE_BURN / DEADLOCK.
- `StuckPolicy` (policy-driven mapping, fail-closed: low confidence / missing evidence → escalate).
- Progress Monitor (every iteration monitored, no gaps).
- Oscillation Detector (repeated trajectory hash, not guessed from one point).
- Plateau Detector (progress < threshold over N iterations).
- Resource-Burn Detector (cost rises, progress flat).
- Stuck Gate (trigger action only when Governor authorizes + autonomy suffices).
- Deterministic: same trajectory + detector version/config → same verdict.

### Out of scope
- Recovery engine (T055), Governor (T054), Scheduler (T062).

## Deliverables
- `aios/stuck_detection/contracts.py` — StuckSignal, StuckKind, StuckSeverity, StuckPolicy.
- `aios/stuck_detection/detector.py` — StuckDetector (monitors + detectors), StuckGate.
- `aios/stuck_detection/tests/` — unit/contract/integration/architecture tests.

## Acceptance Criteria
- AC-061-01: Every iteration monitored (no gaps).
- AC-061-02: Detect ≠ Decide ≠ Recover (3 tiers).
- AC-061-03: OSCILLATION from repeated trajectory hash.
- AC-061-04: PLATEAU when progress < threshold over N iterations.
- AC-061-05: RESOURCE_BURN when cost rises, progress flat.
- AC-061-06: Low confidence / missing evidence → escalate (fail-closed).
- AC-061-07: Stuck signal never auto-promoted to "progressing".
- AC-061-08: Action respects autonomy (budget exceeded → BLOCK via Governor).
- AC-061-09: Signal has evidence (provenance).
- AC-061-10: Deterministic (same trajectory + version → same verdict).
- AC-061-11: Integrates with Loop (T053) + Evaluation (T060).
- AC-061-12: No second autonomous control plane.
- AC-061-13: Regression M0–M8 PASS.

## Dependencies
- TASK-053 Autonomous Loop, TASK-055 Recovery, TASK-060 Evaluation, TASK-054 Governor

## Governance references
- Rule 1..7 satisfied via `aios/governance/*`.
