# TASK-063 — Test

## How to run
```
python -m pytest aios/governance/architecture -q
```

## What is covered
- `test_baseline.py` (new, T063 matrix):
  - agent→subprocess → ARCH-001 FAIL
  - agent→provider → ARCH-002 FAIL
  - agent→filesystem → ARCH-003 FAIL
  - tool→runtime (skip-layer) → ARCH-004 FAIL
  - correct downward import → PASS
  - parse error → `ArchitectureError` (fail-closed BLOCK)
  - determinism: same source + version → identical result
  - `ARCHITECTURE_VERSION == "1.0"`
  - `frozen_layer_contract()` matches `LAYER_ORDER` (real frozen order)
  - `frozen_arch_rules()` covers ARCH-001..004
  - returned contract is a copy (no mutation of source of truth)
  - gate fail-closed on violation
- Existing `test_architecture.py`, `test_layer_rules.py`, etc. continue to pass.

## Result
124 passed.
