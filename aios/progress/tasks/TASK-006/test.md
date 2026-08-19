# TASK-006 — Test

## How to run
```
cd d:\AIOS
python -m pytest aios -q
```

## What is covered (27 new automated tests)

| Module | Tests | Coverage |
|--------|-------|----------|
| runtime/providers/contract | 5 | capability `supports`/`satisfies`, `UsageRecord.estimate` cost, request defaults, error code, capability values |
| runtime/providers/adapters | 10 | mock offline + completion + call count + queued response, openai not-offline + SDK-required error, ollama not-offline + urllib call (monkeypatched), capability spread |
| runtime/providers/registry | 12 | default mock, register/list, get provider/model, unknown-provider error, `select_model` by capability/offline-first/cost/prefer/no-match, `complete` records call, capability routing, explicit-model complete, contract swap |

## Total
- TASK-001: 39 | TASK-002: 43 | TASK-003: 78 | TASK-004: 45 | TASK-005: 34 | TASK-006: 27
- **Total suite: 266 tests, 0 failures**

## Architecture gate
- `python aios/governance/cli/gate_check.py --task TASK-006` — lifecycle
  artifacts present; no architecture violations (relative imports only within
  `aios/runtime`).
