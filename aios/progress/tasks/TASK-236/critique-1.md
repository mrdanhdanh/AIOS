# TASK-236 — Critique 1

## Thiếu sót
- Spec chưa nêu rõ kill switch là hard guard (phase HALTED ngay bước 0).
- Chưa chỉ định verdict cuối = applied ∧ re_test_passed ∧ ¬rolled_back ∧ integrity.passed.

## Rủi ro
- Nếu apply thiếu permission/approval mà vẫn claim success → vi phạm fail-closed.

## Đề xuất
- `UnifiedRemediationLifecycle.run` kiểm tra `kill.is_halted(GLOBAL)` trước mọi bước.
- `RemediationReport.success` chỉ True khi mọi gate pass.
