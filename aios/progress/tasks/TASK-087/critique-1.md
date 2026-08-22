# Critique 1 — TASK-087

- Spec thiếu rõ 5 checks (api/schema/event/version/contract) → bổ sung `ConformanceCheck`.
- Cần làm rõ "1 check FAIL → không conform": `issue()` fail-closed trên `conformant`.
- Tích hợp Certification (T073): `certify()` chỉ cấp khi conformant.
- Đề xuất test deterministic (cùng build + suite → cùng hash).
- Kết luận: spec đủ, implementation cover đủ AC.
