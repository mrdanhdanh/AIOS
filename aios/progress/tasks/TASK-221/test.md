# Test — TASK-221

## Commands
```
python -m pytest aios/api/tests/test_coordinator_router.py -q
python -m pytest aios/governance/architecture -q -k api
python -m pytest aios -q
```

## Results
- `test_coordinator_router.py`: **6 passed** (run happy path, validation 422, get after run, get 404).
- Architecture gate (`api` layer): clean (api → agents downward OK).
- Full suite regression: green.
