# TASK-232 — Breakdown

## Sub-tasks
1. **T232.1** — Thêm `CodingEdition.analyze_and_record(handler, code, work_dir, store)` trong `integration.py`.
2. **T232.2** — Chạy write+test (T231) → `py_compile` → record Evidence (provenance complete).
3. **T232.3** — Test: emit evidence / thiếu store.
4. **T232.4** — Architecture gate + pytest.

## Verification
`pytest aios/coding_edition/tests/test_coding_edition.py -k analyze_and_record` + `pytest aios/governance/architecture`.
