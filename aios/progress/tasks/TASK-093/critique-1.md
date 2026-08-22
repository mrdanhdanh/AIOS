# Critique 1 — TASK-093

- Spec cần làm rõ `BehavioralDocReviewer.review` phải kiểm tra (1) doc cover đủ
  T089-T093, (2) ADR-0008 có rationale, (3) reference không stale/404, (4) deterministic.
- Cần đảm bảo reference trỏ đến module thật (`aios/behavioral/...`, `aios/harness_coverage/...`,
  `aios/meta_harness/...`, `aios/readiness_trust/...`) và doc thật (`docs/adr/ADR-0008.md`).
- Tích hợp DX (T071): doc reference đến `aios/devkit/` (developer tooling).
- Đề xuất test: thiếu coverage → blocked; thiếu rationale → blocked; stale ref → blocked.
- Kết luận: spec đủ, implementation cover đủ AC.
