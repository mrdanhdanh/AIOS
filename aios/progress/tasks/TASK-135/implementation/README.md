# TASK-135 Implementation

Module: `aios/execution/contract.py`

Public classes:
- `ExecutionContract` — canonical execution contract (request/response + sandbox/policy/artifact/evidence refs).
- `ExecutionRequest` / `ExecutionResponse` — standard request/response schema.
- `ExecutionStatus` — outcome enum.
- `CapabilityDispatcher` — Protocol for injected execution capability (ARCH-004).

Properties: I/O-free, deterministic, fail-closed. Provenance via `content_hash()` + `provenance()`.
