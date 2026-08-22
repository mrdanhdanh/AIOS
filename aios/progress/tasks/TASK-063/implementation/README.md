# TASK-063 — Implementation

TASK-063 is **documentation + guard codification** (no new runtime feature).
The real code delivered lives in the governance package, not here.

## Real modules
- `aios/governance/architecture/baseline.py`
  - `ARCHITECTURE_VERSION = "1.0"`
  - `frozen_layer_contract()` — returns a **copy** of `LAYER_ORDER` from
    `guard.py` (single source of truth; callers cannot mutate it).
  - `frozen_arch_rules()`, `is_frozen_layer()`, `classify()`, `scan()` —
    re-exports of `guard.py` constants/functions.
- `aios/governance/architecture/guard.py`
  - Implements ARCH-001..004 fail-closed + deterministic (pure AST scan).
  - No behavioral change required for T063; verified by tests.
- `aios/governance/architecture/__init__.py`
  - Exports the baseline symbols for downstream consumers (CI, gates, docs).

## Docs
- `docs/adr/ADR-ARCH-1.0.md` — frozen 1.0 baseline ADR.

## Tests
- `aios/governance/architecture/tests/test_baseline.py` — full T063 §7 matrix.

Run: `python -m pytest aios/governance/architecture -q`
