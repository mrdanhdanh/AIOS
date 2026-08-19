# TASK-004 — Test

## How to run
```
cd d:\AIOS
python -m pytest aios -q
```

## What is covered (45 new automated tests)

| Module | Tests | Coverage |
|--------|-------|----------|
| runtime/context | 10 | 6 context types, create/factory, store put/get, list-by-type, hierarchy children, chain resolution, delete, non-context reject, thread safety |
| runtime/audit | 8 | record/seal, prev-hash chaining, tamper detection, reorder detection, query by actor/context/status, root hash, metadata |
| runtime/artifact | 11 | checksum compute, bytes accept, invalid version reject, non-str/bytes reject, put/get, bad-checksum reject, duplicate-id reject, SemVer sort, latest, verify-all, delete |
| runtime/permission | 8 | grant/check, wildcard resource, specific-resource deny, revoke, unknown subject, list-for, scope values, matches |
| runtime/policy | 8 | deny without permission, allow via permission+rule, deny overrides allow, insufficient when no rule, deny-all/allow-all helpers, applied-rules trace, deterministic no-LLM |

## Total
- TASK-001 tests: 39
- TASK-002 tests: 43
- TASK-003 tests: 78
- TASK-004 tests: 45
- **Total suite: 205 tests, 0 failures**

## Architecture gate
- `python aios/governance/cli/gate_check.py --task TASK-004` — lifecycle
  artifacts present; no architecture violations in `implementation/` (empty by
  convention; production code uses relative imports, no upward layer imports).
