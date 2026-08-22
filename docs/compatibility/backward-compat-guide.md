# Backward Compatibility Guide (T086)

AIOS 1.x keeps serving consumers written for 1.0 without breaking
(see [ADR-Compatibility](../adr/ADR-Compatibility.md)).

## Surfaces

The compat guarantee locks three behavioral surfaces: **API**, **SCHEMA**,
**EVENT**.

## Rule

A breaking change against a 1.0 consumer is **BLOCKED** — it must go through a
MAJOR bump with a deprecation window (T084). A non-breaking change on a
compatible version is allowed.

## Usage

```python
from aios.backward_compat import BackwardCompatChecker, CompatCheck, CompatSurface

chk = BackwardCompatChecker()
res = chk.check(CompatCheck(surface=CompatSurface.API, provider_version="1.1.0"))
assert res.compatible and not res.blocked

breaking = chk.check(CompatCheck(
    surface=CompatSurface.SCHEMA, provider_version="1.1.0", breaking=True))
assert breaking.blocked  # fail-closed
```

The compat test suite (`CompatTestSuite`) must PASS before a DONE is allowed.
Every check carries an `evidence_ref` (T001 Rule 5).
