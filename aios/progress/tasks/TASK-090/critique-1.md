# Critique 1 — TASK-090

- Spec cần làm rõ `CoverageMap.gaps()` phải trả mọi surface chưa harnessed (no
  hidden gap) — fail-closed readiness dựa trên `coverage_ratio >= threshold`.
- Cần đảm bảo `certify()` chỉ cấp chứng chỉ khi `readiness == READY` (T073).
- Tích hợp T089: `CoverageMap.from_behavior_scenarios` đăng ký surface từ behavior
  scenarios.
- Đề xuất test deterministic: cùng surfaces + cùng map → cùng coverage_ratio + hash.
- Kết luận: spec đủ, implementation cover đủ AC.
