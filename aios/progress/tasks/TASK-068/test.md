# TASK-068 — Test

## How to run
```
python -m pytest aios/kill_switch -q
```

## What is covered
- `tests/test_contracts.py` — `HaltSignal`/`HaltSource`/`HaltScope` invariants,
  deterministic `canonical()`, `HaltViolation` là Exception.
- `tests/test_controller.py` — mọi AC + Test Matrix:
  - manual global halt → mọi context dừng fail-closed + `begin_action` chặn.
  - policy GOAL-scoped halt → đúng scope, context khác vẫn chạy.
  - halt mid in-flight → `drain()` gọi + state persist (durable).
  - layer skip halt → `HaltViolation` + authoritative state vẫn chặn.
  - failing drain → không phá fail-closed.
  - audit evidence có provenance đầy đủ.
  - deterministic/idempotent (same signal → same result).
  - verified state không bị destroy sau halt.
- `tests/test_integration.py` — `GovernorHaltBridge` delegate/block, fallback
  T066/T067.
- `tests/test_audit.py` — evidence admissible + idempotent + shared store.

## Result
23 passed.
