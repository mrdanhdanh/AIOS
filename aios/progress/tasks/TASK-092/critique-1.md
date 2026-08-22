# Critique 1 — TASK-092

- Spec cần làm rõ `CombinedTrust` có 3 trạng thái: READY_TRUSTED / READY_UNTRUSTED /
  NOT_READY — chỉ READY_TRUSTED mới certify (fail-closed).
- Cần đảm bảo `harness_trusted` = (coverage READY) AND (meta PASS) — cả hai điều kiện.
- Tích hợp T090/T091: `evaluate` nhận `CoverageReport` + `MetaResult`.
- Đề xuất test: ready+trusted → certify; ready+untrusted → không certify.
- Kết luận: spec đủ, implementation cover đủ AC.
