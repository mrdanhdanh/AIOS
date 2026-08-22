# TASK-071 — Implementation

This folder is a **pointer** only. Real source lives under the repository
packages (per the "implementation/ only README pointer" rule):

- `aios/devkit/cli_version.py` — `CliVersionPolicy`, `CLI_VERSION`, breaking-change rule.
- `aios/devkit/errors.py` — `ActionableError`, `format_actionable`, `explain`, `CliVersionBumpRequired`.
- `aios/devkit/scaffold.py` — `DevKitScaffold.scaffold_artifact` / `verify_conformance` / `render`.
- `aios/devkit/cli.py` — `DevKitCLI.scaffold` / `verify`.
- `aios/devkit/__init__.py` — public exports (peer/downward only).
- `aios/cli/workflow_cli.py` — `version` + `dx scaffold|verify|policy` commands.
- `docs/dx/getting-started.md`, `docs/dx/reference.md` — DX documentation.
- Tests: `aios/devkit/tests/test_devkit.py`, `aios/cli/tests/test_dx.py`.
