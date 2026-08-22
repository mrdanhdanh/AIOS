# Critique 2 — TASK-100

- Confirm `FailureCorpus.add` dedupe bằng content_hash, trả về entry cũ nếu trùng.
- `gaps()` chỉ trả về entry `covered_by_harness=False` (fail-closed gap report).
- `analysis_hash` dùng sha256 của JSON sort_keys → deterministic.
- Integration import-level với Detect/Loop/Coverage/Evidence, không rewrite dependency.
- Kết luận: implementation đủ điều kiện qua review.
