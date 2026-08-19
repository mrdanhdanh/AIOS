# TASK-003 — Breakdown

- [x] **3.1** Implement `aios/core/version.py` — SemVer parsing, comparison, pre-release handling
- [x] **3.2** Implement `aios/core/contracts.py` — typed contracts with version metadata + compatibility checker
- [x] **3.3** Implement `aios/core/container.py` — DI container with singleton/scoped/transient + thread safety
- [x] **3.4** Implement `aios/core/events.py` — event bus with typed events, ordered dispatch, error handling
- [x] **3.5** Implement `aios/core/planner.py` — ExecutionPlan, Step, StepStatus primitives
- [x] **3.6** Write `aios/core/tests/test_version.py` — version parsing, comparison, edge cases
- [x] **3.7** Write `aios/core/tests/test_contracts.py` — contract compatibility, error cases
- [x] **3.8** Write `aios/core/tests/test_container.py` — DI lifetimes, thread safety, factory registration
- [x] **3.9** Write `aios/core/tests/test_events.py` — publish/subscribe, ordering, error handling
- [x] **3.10** Write `aios/core/tests/test_planner.py` — plan creation, step transitions, status tracking
- [x] **3.11** Update `aios/core/__init__.py` — export new public API
- [x] **3.12** Run full test suite — all TASK-001/002/003 tests green (160 passed)
- [x] **3.13** Write regression.md — verify TASK-001/002 dependency closure green
