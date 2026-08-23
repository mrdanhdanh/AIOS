# Critique 1 — TASK-125

## Missing / weak sections in spec.md
- Spec thiếu định nghĩa rõ ràng về "mandatory artifacts" cho mỗi coding state — cần map cụ thể (plan/generated_code/review_result/final_artifact/evidence).
- Chưa nêu rõ hành vi khi transition bị policy reject (T113) — phải fail-closed.

## Risks
- Nếu state machine cho phép backward transition tùy tiện → vi phạm T001 Rule 6.
- Nếu không ghi provenance trên mọi transition → mất traceability (T001 Rule 5).

## Recommendations
- Thêm bảng `_CODING_ARTIFACTS` ràng buộc artifact theo state (đã làm trong implementation).
- Đảm bảo `transition()` raise `CoderAgentError` khi `policy_ok=False` hoặc thiếu artifact.
- Test phải cover cả architecture (module không import subprocess/os/providers/filesystem).
