# TASK-057 — Test Report

## How to run
```
python -m pytest aios/autonomous_memory/tests -q
python -m pytest aios -q
```

## Coverage
- Failure memory requires valid evidence (provenance chain).
- Goal memory: observation + lesson_candidate, untrusted on write.
- Verify promotes to TRUSTED; trusted-only read excludes unverified.
- Governor denial blocks persist.
- Deduplicate failure entries.
- Deterministic retention eviction.
- No parallel memory store created.

## Results
- `autonomous_memory/tests`: 8 passed
- Architecture gate: PASS
- Status: ALL PASS
