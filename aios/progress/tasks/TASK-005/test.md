# TASK-005 — Test

## How to run
```
cd d:\AIOS
python -m pytest aios -q
```

## What is covered (34 new automated tests)

| Module | Tests | Coverage |
|--------|-------|----------|
| runtime/execution | 8 | complete run, retry, fail-after-retries, timeout, policy-deny blocks, cancel-between-steps, EventBus events, plan-type guard |
| runtime/scheduler | 7 | FIFO, priority ordering, running-mark, done/cancel, cancel-skip on dequeue, peek, pending count |
| runtime/state | 7 | save/load roundtrip, missing->None, serialize roundtrip, snapshot independence, reject-non-state, delete/list, resume cursor |
| runtime/resource | 7 | register/grant, reject-when-full, queue-when-full, release-promotes-waiting, unknown-resource error, negative-capacity error, usage tracking |
| runtime/kernel | 5 | wires all 9 services, singletons shared, executor-runs-through-wiring, external container, health snapshot |

## Total
- TASK-001: 39 | TASK-002: 43 | TASK-003: 78 | TASK-004: 45 | TASK-005: 34
- **Total suite: 239 tests, 0 failures**

## Architecture gate
- `python aios/governance/cli/gate_check.py --task TASK-005` — lifecycle
  artifacts present; no architecture violations (relative imports only).
