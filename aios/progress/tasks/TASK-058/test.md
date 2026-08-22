# TASK-058 — Test Report

## How to run
```
python -m pytest aios/autonomous_experimentation/tests -q
python -m pytest aios -q
```

## Coverage
- Propose rejects vague metric / mutable baseline version.
- Valid experiment proposed + authorized.
- Governor denial → REJECTED.
- Promotion READY only with improvement + no regression + policy pass.
- Cost regression → NOT_PROMOTED.
- INCONCLUSIVE → NOT_PROMOTED.
- Policy fail → NOT_PROMOTED.
- Run uses Harness only.

## Results
- `autonomous_experimentation/tests`: 9 passed
- Architecture gate: PASS
- Status: ALL PASS
