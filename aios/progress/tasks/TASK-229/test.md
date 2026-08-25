# TASK-229 — Test Report

## Unit tests (mới)
- `test_simulate_emits_evidence`: `--simulate` in ra "SIMULATED evidence record(s) emitted".
- `test_governance_precheck_denies_missing_permission`: kernel không grant → pre-check DENY.
- `test_governance_precheck_allows_granted`: kernel grant EXECUTE → pre-check PASS.

## Kết quả
```
python -m pytest aios/cli/tests/test_execute.py -q
6 passed
```

## Architecture gate
```
python -m pytest aios/governance/architecture -q
124 passed
```
