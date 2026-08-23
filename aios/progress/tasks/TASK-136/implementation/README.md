# TASK-136 Implementation

Module: `aios/execution/sandbox.py`

Public classes:
- `SandboxManager` — lifecycle create/destroy/isolate, health, `is_usable`.
- `SandboxRecord` — immutable-by-id sandbox record.
- `IsolationLevel` — process/fs/network (T040).
- `SandboxStatus` — created/isolated/destroyed.

Properties: I/O-free, deterministic, fail-closed (isolate requires policy_ref). Provenance via `provenance()`.
