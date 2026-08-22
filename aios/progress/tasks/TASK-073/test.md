# TASK-073 — Test

## How to run
```
python -m pytest aios/certification -q
```

## What is covered
- All gates pass → certificate issued (AC1, AC2, AC4, AC5, AC6).
- One gate fails → no certificate fail-closed (AC3).
- Architecture violation → cert FAIL.
- Deterministic same build + suite (AC5).
