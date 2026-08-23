# TASK-125 Implementation

Coder Agent Contract + State Machine lives in:

- `aios/coder/contract.py` — `CoderAgentContract`, `CoderAgentStateMachine`, `CodingTaskState`, `TransitionRecord`.
- Tests trong `aios/coder/tests/test_coder.py` (12 tests, Test Matrix TASK-125).

Design:
- `CoderAgentContract` — I/O-free, capability-injected; `agent_id` immutable (T001 Rule 1); `io_free` luôn `True` (ARCH-001..004).
- `CodingTaskState` — PLANNED → CODING → REVIEWING ↔ PATCHING → DONE (T001 Rule 6).
- `CoderAgentStateMachine` — fail-closed: thiếu artifact hoặc policy reject → `CoderAgentError` (T001 Rule 6 / T113). Mọi transition ghi `TransitionRecord` (evidence_id, run_id, content_hash) → provenance (T001 Rule 5). Deterministic: cùng (state, artifacts) → cùng transition + content_hash.

Integration (import-level, no rewrite):
- `aios.governance.evidence` (T001) — provenance schema
- `aios.governance.architecture` (ARCH) — layer classification (unknown)
- `aios.worker` (T013) — capability injection boundary
- `aios.coder.contract` (T125) -> `aios.coder.planner` (T126) / `aios.coder.generation` (T127)
