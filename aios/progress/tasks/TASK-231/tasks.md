# TASK-231 — Breakdown

## Sub-tasks
1. **T231.1** — Thêm `CodingEdition.execute_code(handler, generated_code, work_dir, run_tests)` trong `integration.py`.
2. **T231.2** — Ghi file qua `handler` (scope WRITE); tùy chọn chạy test (scope EXECUTE); trả `verification_report`.
3. **T231.3** — Test: write thành công / thiếu handler / denied không permission.
4. **T231.4** — Architecture gate + pytest.

## Verification
`pytest aios/coding_edition/tests/test_coding_edition.py -k execute_code` + `pytest aios/governance/architecture`.
