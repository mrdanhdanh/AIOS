# TASK-141 — Task Breakdown

1. Định nghĩa `redact` (secret token scan, T040/T113).
2. Định nghĩa `OutputCapture` (kind/content/content_hash) + `CollectedArtifact` (immutable `collector_id`).
3. `capture_output` fail-closed: empty -> reject; redact + hash.
4. `collect` tập hợp outputs + artifact refs (T130).
5. `content_hash` rỗng khi không có gì (fail-closed, T078).
6. `provenance()` với `content_hash` (T001/T078).
7. Tests (`test_collector.py`): 7 tests.
8. Chạy pytest + gate_check.
