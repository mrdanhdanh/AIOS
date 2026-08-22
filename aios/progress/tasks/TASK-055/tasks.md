# TASK-055 — Breakdown

## Steps
1. `aios/autonomous_recovery/contracts.py` — FailureClass/CircuitState/RecoveryStrategy/RecoveryVerdict/RecoveryAttempt.
2. `aios/autonomous_recovery/circuit.py` — CircuitBreaker state machine.
3. `aios/autonomous_recovery/recovery.py` — FailureClassifier, RecoveryController, RecoveryPolicy (fail-closed verify).
4. `aios/autonomous_recovery/tests/test_autonomous_recovery.py` — 8 tests.
5. Run architecture guard — no subprocess/provider/filesystem import.
6. Run full suite — no regressions.

## Exit Criteria
- All AC-055-01..10 PASS, gate PASS, no regressions.
