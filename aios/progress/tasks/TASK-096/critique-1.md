# Critique 1 — TASK-096

- Spec cần làm rõ `Sandbox` isolation fail-closed: sandbox không isolated → không
  chạy simulation (tránh ảnh hưởng production).
- Cần đảm bảo gate fail-closed: simulate FAIL hoặc meta-verify FAIL → REJECT.
- Tích hợp Meta (T091) qua `MetaHarness.known_answer_check` + `evaluate` để xác nhận
  verdict của simulation.
- Đề xuất test deterministic: cùng candidate + cùng sandbox → cùng outcome.
- Kết luận: spec đủ, implementation cover đủ AC.
