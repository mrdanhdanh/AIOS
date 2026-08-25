# TASK-229 — Critique 1

## Thiếu sót
- Spec chưa nêu rõ pre-check dùng API nào của `PolicyEngine` (`evaluate` trả `PolicyResult.decision`, không phải `.check`).
- Chưa chỉ định `simulate` phải emit Evidence (SIMULATED) qua `record_execution_evidence`.
- Chưa nêu RetryGuard tích hợp ở đâu (vòng lặp exec).

## Rủi ro
- Nếu pre-check sai API → runtime error (đã bắt gặp `policy.check` không tồn tại).
- Thiếu simulate-evidence → M32 (Evidence-Native) không có dữ liệu từ simulation.

## Đề xuất
- Dùng `policy.evaluate(req).decision` + `broker.has(subject, scope, resource)`.
- `record_execution_evidence(..., simulated=True)` khi `--simulate`.
- RetryGuard quanh vòng lặp kết quả step FAILED.
