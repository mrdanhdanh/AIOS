# TASK-055 — Autonomous Recovery

## Objective
Build controlled Autonomous Recovery: detect execution/goal failure or degradation, trigger controlled recovery, and fail-closed when recovery is not safe. The Autonomy Governor (T054) remains the authority; this module does not create a second policy engine or control plane.

## Scope
### In scope
- Failure Classification: TRANSIENT / RESOURCE / DEPENDENCY / POLICY / STATE / LOGICAL / UNKNOWN (deterministic).
- Circuit Breaker state machine: CLOSED → OPEN (failure threshold) → HALF_OPEN (cooldown) → CLOSED (recovery success) / OPEN (recovery failure). No infinite retry.
- Recovery Policy: retry / resume / fallback / rollback / escalate / safe-stop, decided by policy, not by the loop arbitrarily.
- Recovery Safety: every attempt recorded (`RecoveryAttempt`) with pre/post state, verification, evidence, outcome. No evidence loss.
- Safe-Stop: retry budget exhausted / circuit OPEN / policy violation / no valid checkpoint / incompatible fallback / unverified post-state / failure loop / side-effect exceeds autonomy / insufficient evidence → SAFE-STOP.
- Fail-closed: recovery success whose post-condition cannot be *verified* is NOT treated as recovered.

### Out of scope
- Policy Engine (Governor owns approval), goal-level durability (T056), memory promotion (T057).

## Deliverables
- `aios/autonomous_recovery/contracts.py` — FailureClass, CircuitState, RecoveryStrategy, RecoveryVerdict, RecoveryAttempt.
- `aios/autonomous_recovery/circuit.py` — CircuitBreaker state machine.
- `aios/autonomous_recovery/recovery.py` — FailureClassifier, RecoveryController, RecoveryPolicy.
- `aios/autonomous_recovery/tests/` — unit/contract/integration/architecture tests.

## Acceptance Criteria
- AC-055-01: Failure classification covers all 7 classes deterministically.
- AC-055-02: Circuit breaker opens at threshold, half-opens after cooldown, closes on success.
- AC-055-03: Recovery strategy decided by policy per failure class.
- AC-055-04: Recovery attempt records full provenance (pre/post/verification/evidence).
- AC-055-05: Unverified recovery → NOT_RECOVERED (fail-closed, no auto-promote).
- AC-055-06: Unknown failure → SAFE_STOP.
- AC-055-07: Governor denial → NOT_RECOVERED (no recovery without authority).
- AC-055-08: Circuit OPEN blocks recovery.
- AC-055-09: No subprocess/provider/filesystem import (architecture gate).
- AC-055-10: Regression M0–M8 PASS.

## Dependencies
- TASK-053 Autonomous Loop
- TASK-054 Autonomy Governor

## Governance references
- Rule 1..7 satisfied via `aios/governance/*`.
