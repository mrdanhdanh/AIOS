# TASK-045 Implementation — Extension Contracts

Implementation lives in `aios/extension_contracts/` (M8 Ecosystem — Extension Contracts).

```
aios/extension_contracts/
  contracts.py     # ExtensionContract, ExtensionContext
  compatibility.py # Compatibility checker (version/contract)
  evidence.py      # Extension evidence (provenance)
  validator.py     # Boundary validator (Core protection)
  __init__.py      # re-exports
  tests/
    test_contracts.py
    test_compatibility.py
    test_validator.py
```

Public extension contracts protect Core. Boundary check prevents Core access.

See `../spec.md`, `../test.md`, `../evaluation.md`, `../regression.md` for acceptance, verification and regression evidence. Full suite: `python -m pytest aios -q` (2519 PASS current).
