# TASK-052 — Test Report

## How to run
```
python -m pytest aios/world_model/tests -q
python -m pytest aios -q
```

## Coverage
- Observation without provenance rejected.
- Entity creation + status transition recorded & traceable.
- Idempotent observation produces no transition.
- Invalid status transition rejected.
- Relation requires provenance.
- Snapshot + diff between two points.
- World Model separated from Memory.

## Results
- `world_model/tests`: 8 passed
- Architecture gate: PASS
- Status: ALL PASS
