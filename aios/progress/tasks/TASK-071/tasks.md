# TASK-071 — Breakdown

- [x] Step 1 — Add `aios/devkit/cli_version.py` with `CliVersionPolicy` + breaking-change rule.
- [x] Step 2 — Extend `aios/devkit/errors.py` with `format_actionable` / `explain` / `CliVersionBumpRequired`.
- [x] Step 3 — Extend `aios/devkit/scaffold.py` with `scaffold_artifact` / `verify_conformance` / `render` (T063 + T064 conformance, deterministic).
- [x] Step 4 — Extend `aios/devkit/cli.py` (`DevKitCLI.scaffold` / `verify`).
- [x] Step 5 — Extend `aios/cli/workflow_cli.py` with `version` + `dx scaffold|verify|policy` stable subcommands.
- [x] Step 6 — Export new public API from `aios/devkit/__init__.py` (peer/downward only, no `agents/`).
- [x] Step 7 — Write `docs/dx/getting-started.md` + `docs/dx/reference.md` (valid links).
- [x] Step 8 — Add tests in `aios/devkit/tests/` + `aios/cli/tests/`; run `pytest aios/devkit aios/cli -q` → PASS.
- [x] Step 9 — Create task artifacts (spec/critique×2/tasks/review/test/evaluation/regression + implementation pointer).
