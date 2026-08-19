# Implementation — TASK-001

The implementation of TASK-001 **is** the governance engine:

- `aios/governance/task_registry/` — Rule 1 (immutable IDs) + `parse_master_spec`
- `aios/governance/dependency/` — Rule 2 (dependency graph, ready/cycle/closure)
- `aios/governance/architecture/` — Rule 3 (AST/import guard ARCH-001..004)
- `aios/governance/deterministic/` — Rule 4 (deterministic control path)
- `aios/governance/evidence/` — Rule 5 (provenance chain)
- `aios/governance/lifecycle/` — Rule 6 (state machine + artifact guards)
- `aios/governance/regression/` — Rule 7 (dependency closure runner)
- `aios/governance/gates/` — unified `TaskGate`

Each module has an automated pytest suite under its `tests/` folder.
Run: `python -m pytest aios/governance -q`  → 26 passed.
