# TASK-001 — Test

## How to run
```
cd d:\AIOS
python -m pytest aios -q
```

## What is covered (38 automated gate tests)
| Module | Tests | Rule |
|--------|-------|------|
| aios/governance/task_registry/tests | 6 | Rule 1 |
| aios/governance/dependency/tests | 5 | Rule 2 |
| aios/governance/lifecycle/tests | 4 | Rule 6 |
| aios/governance/evidence/tests | 3 | Rule 5 |
| aios/governance/architecture/tests | 6 | Rule 3 |
| aios/governance/deterministic/tests | 4 | Rule 4 |
| aios/governance/regression/tests | 3 | Rule 7 |
| aios/governance/gates/tests | 3 | Unified |
| aios/agents/tests | 4 | Roles |

## Integration test
`aios/governance/gates/tests/test_unified_gate.py` wires all 7 real submodules
and proves the convergence rule (all pass -> DONE; any fail -> BLOCKED).
