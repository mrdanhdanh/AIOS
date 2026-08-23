# TASK-137 Implementation

Module: `aios/execution/workspace.py`

Public classes:
- `WorkspaceManager` — create/archive workspaces, snapshot/restore.
- `WorkspaceRecord` — immutable-by-id workspace record.
- `SnapshotRecord` — immutable-by-id snapshot with `state_hash` (T066/T078).
- `WorkspaceStatus` — active/archived.

Properties: I/O-free, deterministic, fail-closed (snapshot requires non-empty state). Provenance via `provenance()`.
