# TASK-046 Implementation — Ecosystem Registry

Implementation lives in `aios/ecosystem_registry/` (M8 Ecosystem — Registry).

```
aios/ecosystem_registry/
  contracts.py  # RegistryEntry, TrustState, VersionInfo
  registry.py   # EcosystemRegistry (search/resolve_version/is_compatible/set_trust/checksum)
  __init__.py   # re-exports
  tests/
    test_registry.py
```

Discovery registry for extensions. `TrustState` + search/resolve_version/is_compatible/set_trust/checksum.

See `../spec.md`, `../test.md`, `../evaluation.md`, `../regression.md` for acceptance, verification and regression evidence. Full suite: `python -m pytest aios -q` (2519 PASS current).
