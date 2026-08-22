# TASK-071 — Test

## How to run
```
python -m pytest aios/devkit aios/cli -q
```

## What is covered
- **Unit** — `scaffold_artifact` for capability/agent/tool/workflow; deterministic output; unknown-kind error.
- **Contract** — generated spec validated by `aios.extension_contracts.validator` (T064).
- **Architecture** — generated `.py` files scanned by `aios.governance.architecture.guard` (T063, no ARCH-001..004).
- **Integration** — `DevKitCLI.scaffold` + `verify`; `aiagent version` / `dx scaffold` / `dx verify` / `dx policy` end-to-end via `main()`.
- **Regression** — prior `aios/devkit` (T047) tests still pass; no edits to other packages.

## Result
27 passed.
