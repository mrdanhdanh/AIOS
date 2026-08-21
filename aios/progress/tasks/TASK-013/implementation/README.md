# TASK-013 — Implementation

Worker Plane implementation:

- `aios/worker/contract.py` — WorkerContract, WorkerRequest, WorkerContext, WorkerResult, WorkerEvidence (10 mandatory fields, SemVer, provenance)
- `aios/worker/lifecycle.py` — WorkerStatus, WorkerHealth, WorkerLifecycle (state machine, thread-safe)
- `aios/worker/registry.py` — WorkerRegistry (health-aware, thread-safe)
- `aios/worker/router.py` — WorkerRouter (capability-based, deterministic, policy-gated)
- `aios/worker/execution.py` — BaseWorker (capability-only, permission boundary, isolation)
- `aios/worker/workers.py` — GeneralWorker, CoderWorker, DoctorWorker, SystemDoctorWorker
- `aios/worker/__init__.py` — re-exports
- `aios/governance/architecture/guard.py` — worker layer added (LAYER_ORDER, LAYER_KEYWORDS, ALLOWED_IMPORT_LAYERS, WORKER_FORBIDDEN)
- `aios/worker/tests/` — 8 test files, 161 tests

Tests: `python -m pytest aios -q` — 851 passed.
