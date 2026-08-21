# TASK-013 — Breakdown

- [x] **13.1** Create `aios/progress/tasks/TASK-013/` scaffold — `spec.md`, `critique-1.md`, `critique-2.md`, `tasks.md`, `review.md`.
- [x] **13.2** Update `aios/governance/architecture/guard.py` — add `worker` layer to `LAYER_ORDER`, `LAYER_KEYWORDS`, `ALLOWED_IMPORT_LAYERS`, extend `AGENT_FORBIDDEN` for worker.
- [x] **13.3** Implement `aios/worker/contract.py` — `WorkerContract`, `WorkerRequest`, `WorkerContext`, `WorkerResult`, `WorkerEvidence`, `WorkerType`, `WorkerResultStatus`, validation, to_dict/from_dict.
- [x] **13.4** Implement `aios/worker/lifecycle.py` — `WorkerStatus`, `WorkerHealth`, `WorkerLifecycle` state machine, valid transitions, thread-safe, fail-closed.
- [x] **13.5** Implement `aios/worker/registry.py` — `WorkerRegistry` register/get/list/remove, health tracking, thread-safe, duplicate/unknown reject.
- [x] **13.6** Implement `aios/worker/router.py` — `WorkerRouter` capability-based routing, health/policy/availability, deterministic, fallback policy-gated.
- [x] **13.7** Implement `aios/worker/execution.py` — `BaseWorker` abstract, capability-only access, permission boundary, execution_context isolation, structured result, evidence, failure propagation.
- [x] **13.8** Implement `aios/worker/workers.py` — `GeneralWorker`, `CoderWorker`, `DoctorWorker`, `SystemDoctorWorker` concrete workers.
- [x] **13.9** Update `aios/worker/__init__.py` — re-exports for TASK-013.
- [x] **13.10** Create `aios/worker/tests/` — 8 test files covering AC-013-01..11 (≥60 tests) + architecture + integration.
- [x] **13.11** Run `python -m pytest aios -q` — verify 750+ tests PASS, no architecture violations.
- [x] **13.12** Write `test.md` + `evaluation.md` + `REGRESSION.md` with evidence.
- [x] **13.13** Update `aios/progress/PLAN.md`, `LOG.md`, `STATS.md` — mark TASK-013 DONE.
