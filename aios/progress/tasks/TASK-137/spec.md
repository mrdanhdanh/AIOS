# TASK-137 — Workspace / Snapshot Manager

## Objective
Triển khai **Workspace / Snapshot Manager** (M20) như một năng lực có contract, evidence và harness riêng — quản lý workspace (thư mục làm việc) và snapshot (checkpoint) để execution (T135) có thể resume/rollback. TASK-137 là **workspace/snapshot manager, không phải execution mới** (dựa trên Execution Contract T135 + Durable T066 + Upgrade/Migration T020).

## Scope
**In scope:** `aios/execution/workspace.py` — `WorkspaceManager`, `WorkspaceRecord`, `SnapshotRecord`, `WorkspaceStatus`.
**Out of scope:** execution runner mới (T139/T140).

## Deliverables
- `aios/execution/workspace.py` implementation + snapshot/restore.
- Unit + Contract + Integration + Architecture + Regression tests (`test_workspace.py`).
- Tích hợp: T135 -> T137 -> T139/T140.

## Acceptance Criteria
- Workspace Manager quản lý thư mục làm việc riêng biệt.
- Snapshot checkpoint state (T066) hoạt động.
- Restore rollback về snapshot khi fail (T020/T066).
- `workspace_id`/`snapshot_id` immutable (T001 Rule 1).
- Mọi snapshot có `state_hash` (T078) + provenance (T001 Rule 5).
- Tích hợp được với Execution Contract + Durable + Upgrade + Evidence.
- Regression của các milestone trước PASS; không vi phạm invariants.

## Dependencies
- T135 (Execution Contract) -> T137 -> T139/T140.
- T001 (Rule 1/5), T066 (Durable), T020 (Upgrade), T078 (Integrity).

## Governance references
- Rule 1..7 via `aios/governance/*`. `execution` là `unknown` (infra) layer.
