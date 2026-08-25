# TASK-235 — Test Report

## Tests (mới)
- `test_detect_conflicts_finds_disagreement`: PASS vs FAIL cùng req → conflict.
- `test_replay_reconstructs_from_run`: replay trả đúng evidence của run.
- `test_quality_score_and_validity`: score=1.0 khi trust=1/fresh/PASS; STALE → invalid.

## Kết quả
```
pytest aios/governance/evidence/tests/test_evidence.py -k "conflict or replay or quality"
3 passed
```
## Architecture gate: 124 passed.
