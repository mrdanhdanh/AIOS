# TASK-236 — Unified Remediation Lifecycle

> **Trạng thái:** PLANNED (2026-08-25) — phase AIOS 2.x / M33.
> Chi tiết đầy đủ: `docs/AIOS_Master_Task_Specification_M29-M35.md`.

## Mục tiêu
Flow hợp nhất: `Failure → Detect → Diagnose → Candidate → Risk Score → Simulation → Independent Verification → Approval / Auto-Apply → Rollback nếu FAIL`. Chuyển từ autonomous execution → autonomous recovery.

## Phạm vi
- `remediation_detect` → `autonomous_recovery`/`stuck_detection` (diagnose) → `remediation_candidate` → risk → `remediation_simulation` → `verification`/`oracle` (verify) → `remediation_apply` (policy-gated) → `remediation_integrity` → rollback nếu FAIL.
- `kill_switch` là guard cứng. Không tạo package mới.

## Deliverables
- `aios/autonomous_recovery/lifecycle.py` (Unified Remediation Lifecycle) + test + artifacts + evidence.

## Acceptance Criteria
- Flow chạy end-to-end trên scenario failure giả lập.
- Auto-Apply chỉ khi risk < threshold + independent verify PASS.
- Rollback kích hoạt khi apply FAIL (integrity check).
- KillSwitch override mọi bước.
- Architecture gate 0 violations; full suite không regress.

## Dependencies / Gate
TASK-233, TASK-011, TASK-041, TASK-001. Milestone M33.
