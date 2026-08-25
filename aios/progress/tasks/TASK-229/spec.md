# TASK-229 — Unified Execution Entry-Point (Governance-aware execute)

> **Trạng thái:** PLANNED (2026-08-25) — phase AIOS 2.x / M29.
> Chi tiết đầy đủ: `docs/AIOS_Master_Task_Specification_M29-M35.md`.

## Mục tiêu
Biến `aiagent execute` thành entry-point hợp nhất: simulation và real execution dùng CÙNG contract; approval / permission / resource / sandbox nằm trong MỘT flow; mọi execution sinh `Run + Artifact + Evidence`. Đóng khoảng cách Flow A ∧ Flow B.

## Phạm vi
- `aiagent execute` chạy pre-check governance (Policy/Permission/Risk/Approval/KillSwitch) trước exec.
- `--simulate` dùng cùng `ExecutionPlan` contract, chỉ khác bước thực thi (dry-run), vẫn sinh Evidence (loại SIMULATED).
- Mọi execution ghi `Run` + `Artifact` + `Evidence` (provenance đầy đủ).
- Tích hợp `RetryGuard` (T226) vào loop thực thi.

## Deliverables
- `aios/cli/workflow_cli.py` (`execute` governance-aware) + test.
- `aios/runtime/kernel.py` (unified exec loop + evidence emission).

## Acceptance Criteria
- `aiagent execute plan.yaml` chạy pre-check governance trước exec.
- `--simulate` sinh Evidence (SIMULATED) + Run nhưng 0 OS exec.
- Mọi execution sinh đủ `Run + Artifact + Evidence` (provenance complete).
- `RetryGuard` kích hoạt auto-stop khi lỗi lặp ≥ threshold.
- Architecture gate 0 violations; full suite không regress.

## Dependencies / Gate
TASK-228, TASK-222, TASK-226, TASK-001. Milestone M29.
