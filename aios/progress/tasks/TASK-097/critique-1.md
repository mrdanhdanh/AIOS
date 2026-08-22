# Critique 1 — TASK-097

- Spec cần làm rõ pipeline fail-closed: thiếu permission (T070) → không apply;
  high-risk thiếu human approval (T054/T067) → không apply.
- Cần đảm bảo re-test FAIL → rollback (T074/T066) và ghi audit trail.
- Tích hợp Permission (T070) qua `PermissionBroker.check`, Certification (T073) qua
  `Certifier.issue/certify`.
- Đề xuất test deterministic: cùng candidate + cùng policy → cùng apply result.
- Kết luận: spec đủ, implementation cover đủ AC.
