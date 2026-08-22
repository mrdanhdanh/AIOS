# TASK-055 Implementation

## Modules
- `contracts.py` — `FailureClass`, `CircuitState`, `RecoveryStrategy`, `RecoveryVerdict`, `RecoveryAttempt`.
- `circuit.py` — `CircuitBreaker` state machine (CLOSED/OPEN/HALF_OPEN) with threshold/cooldown/probe.
- `recovery.py` — `FailureClassifier` (deterministic keyword map), `RecoveryController` (decide + orchestrate + verify, fail-closed), `RecoveryPolicy`.

## Design notes
- Governor (T054) remains the authority; recovery asks the governor for approval-required strategies and fails closed on denial.
- Verification is mandatory: an unverified post-state is NEVER treated as recovered.
- Circuit breaker prevents infinite retry; OPEN state blocks new recovery attempts until cooldown elapses.
