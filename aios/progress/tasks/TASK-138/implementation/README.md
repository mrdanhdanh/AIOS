# TASK-138 Implementation

Module: `aios/execution/policy.py`

Public classes:
- `PolicyEngine` — fail-closed policy enforcement for executions.
- `ExecutionPolicy` — resource/network/command policy bound to an execution.
- `ResourceLimit` — cpu/mem quota (T039).
- `PolicyDecision` / `Decision` — allow/deny outcome with provenance.

Properties: I/O-free, deterministic, fail-closed (any violation -> deny -> BLOCK). Provenance via `provenance()`.
