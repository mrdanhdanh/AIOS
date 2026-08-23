# TASK-047 Implementation — Developer Kit

Implementation lives in `aios/devkit/` (M8 Ecosystem — Developer Kit).

```
aios/devkit/
  contracts.py   # DevKit contracts
  manifest.py    # Manifest generation/validation
  packaging.py   # Package building
  scaffold.py    # Project scaffolding
  cli.py         # CLI (create/validate/test/simulate/package/inspect)
  cli_version.py # CLI version
  errors.py      # Error model
  __init__.py    # re-exports
  tests/
    test_devkit.py
    test_cli.py
    test_packaging.py
```

CLI/tooling to create, dev, test extensions.

See `../spec.md`, `../test.md`, `../evaluation.md`, `../regression.md` for acceptance, verification and regression evidence. Full suite: `python -m pytest aios -q` (2519 PASS current).
