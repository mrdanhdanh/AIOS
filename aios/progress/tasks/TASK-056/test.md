# TASK-056 — Test Report

## How to run
```
python -m pytest aios/goal_durability/tests -q
python -m pytest aios -q
```

## Coverage
- Atomic monotonic checkpoint sequence.
- Old checkpoint cannot overwrite new.
- Content-hash tamper detection.
- Resume skips completed tasks (idempotency).
- Side-effect idempotency keys.
- Invalid/inconclusive checkpoint → fail-closed (no resume).
- Stale checkpoint → re-plan bridge.
- Policy invalid → block resume.
- 6 interruption causes recorded.

## Results
- `goal_durability/tests`: 9 passed
- Architecture gate: PASS
- Status: ALL PASS
