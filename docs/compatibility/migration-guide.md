# Migration Guide 1.0 → 1.1 (T085)

Migrating a system from AIOS 1.0 to 1.1 is **safe, reversible, and evidenced**
(see [ADR-Compatibility](../adr/ADR-Compatibility.md)).

## Steps

1. **Detect** — confirm the system is at `1.0.0`.
2. **Plan** — enumerate ordered, reversible steps (each has `up`/`down`/`verify`).
3. **Dry-run** — simulate without mutating state (AC-020-05).
4. **Apply** — run each step; if `verify` fails, abort without applying (fail-closed).
5. **Rollback** — run each step's `down` in reverse to return to 1.0.

## Usage

```python
from aios.migration import MigrationRunner, MigrationPlan, MigrationStep

def up(d): d["feature"] = True
def down(d): d.pop("feature", None)
def verify(d): return True

plan = MigrationPlan(steps=[MigrationStep("s1", up, down, verify, evidence_ref="e1")])
runner = MigrationRunner()
result = runner.apply(plan, state)  # fail-closed: verify FAIL -> not applied
```

State is migrated durably (T066) with **no data loss**; the caller's original
state is never mutated. Every step records provenance (T001 Rule 5).
