# TASK-238 — Self-Evolution Lifecycle

> **Trạng thái:** PLANNED (2026-08-25) — phase AIOS 2.x / M35.
> Chi tiết đầy đủ: `docs/AIOS_Master_Task_Specification_M29-M35.md`.

## Mục tiêu
Flow: `Observe → Evaluate → Find weakness → Propose → Experiment → Harness verify → Independent verify → Risk → Human/Policy approval → Apply → Regression → Promote`. AIOS KHÔNG tự sửa chính nó trực tiếp; dùng Experiment → Harness → Evidence → Verification → Policy → Promotion.

## Phạm vi
- `SelfImproverAgent` (T225) sinh `ImprovementProposal` → pipeline thử nghiệm (không apply trực tiếp).
- Experiment trong sandbox/harness; Evidence qua `EvidenceStore`.
- Promotion chỉ khi Harness PASS + Oracle PASS + Policy approve + Regression green.
- `KillSwitch` + `RetryGuard` guard toàn bộ.

## Deliverables
- `aios/agents/self_improver.py` (promotion pipeline hook) + `aios/autonomous_experimentation/` + test + artifacts + evidence.

## Acceptance Criteria
- Proposal → Experiment → Harness → Independent → Policy → Regression → Promote chạy end-to-end trên scenario giả lập.
- AIOS KHÔNG sửa `aios/` trực tiếp không qua pipeline (fail-closed).
- Promotion bị chặn nếu bất kỳ gate FAIL.
- Architecture gate 0 violations; full suite không regress.

## Dependencies / Gate
TASK-225, TASK-233, TASK-235, TASK-029, TASK-001. Milestone M35.
