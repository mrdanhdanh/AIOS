# TASK-228 — Unified ExecutionPlan Contract

> **Trạng thái:** PLANNED (2026-08-25) — phase AIOS 2.x / M29.
> Chi tiết đầy đủ: `docs/AIOS_Master_Task_Specification_M29-M35.md`.

## Mục tiêu
Chuẩn hóa một schema `ExecutionPlan` duy nhất dùng bởi CẢ `aiagent task` (Flow A) và `aiagent execute` (Flow B). Hiện Flow B parse `plan.yaml` nhưng không qua governance; Flow A chạy qua `Orchestrator` + `UnifiedTaskGate`. Task định nghĩa contract chung `Planner → ExecutionPlan → Policy → Capability → Runtime`.

## Phạm vi
- `ExecutionPlan` schema (nodes, scope, resource, permission, policy_ref, evidence_ref) trong `aios/runtime/workflow/` (kế thừa `to_execution_plan`).
- `aiagent execute` sinh `ExecutionPlan` chuẩn, mọi node qua `PolicyEngine.check()` + `PermissionBroker`.
- Converter 2 chiều `WorkflowDefinition ↔ ExecutionPlan` (tương thích ngược, DX stability).
- Không thêm package mới.

## Deliverables
- `aios/runtime/workflow/definition.py` (ExecutionPlan contract + converter) + test.
- `aios/runtime/kernel.py` (`execute_plan` dùng ExecutionPlan chuẩn, policy-checked).

## Acceptance Criteria
- `aiagent execute plan.yaml` sinh ExecutionPlan có `policy_ref` + `permission` mỗi node.
- Node thiếu permission → DENY fail-closed (giống Flow A).
- Converter round-trip không mất trường.
- `python -m pytest aios/governance/architecture -q` → 0 violations.
- Full suite không regress.

## Dependencies / Gate
TASK-222, TASK-008, TASK-010, TASK-001. Milestone M29.
