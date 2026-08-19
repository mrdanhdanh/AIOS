# Breakdown — TASK-002

## Work items
- [x] 1. Tạo `aios/core/` package: `__init__.py`, `scaffold.py` (metadata/logging/config/healthcheck).
- [x] 2. Tạo skeleton `aios/runtime/__init__.py`, `aios/harness/__init__.py`.
- [x] 3. Viết `aios/core/tests/test_core.py` (4 test).
- [x] 4. Viết task artifact `implementation/aios_core.py` (re-export) + `implementation/test_aios_core.py`.
- [x] 5. Viết tài liệu task (spec/critique×2/review/test/evaluation).
- [x] 6. Ghi EVIDENCE.md (provenance) + REGRESSION.md (TASK-001).
- [x] 7. Chạy `gate_check.py TASK-002` → PASS, cập nhật STATUS.md → DONE.

## Execution plan
Deterministic-first: scaffold thuần Python (logging/sys/dataclasses/typing), không LLM.
Không có bước nào cần LLM fallback. Test bootstrap chạy offline.
