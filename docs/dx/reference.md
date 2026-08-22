# AIOS 1.0 Developer Experience — Reference

Reference for the DX tooling delivered by TASK-071. All symbols are importable
from the public `aios.devkit` package (peer/downward imports only; `agents/`
is never imported by the devkit).

## CLI surface (`aiagent`)

| Command | Purpose |
| ------- | ------- |
| `aiagent version` | Print the CLI version (`aios.devkit.cli_version.CLI_VERSION`). |
| `aiagent dx scaffold <kind> <name> [--version X] [--author A] [--out DIR]` | Generate a capability/agent/tool/workflow skeleton. |
| `aiagent dx verify <dir>` | Verify a scaffolded artifact against T063 + T064. |
| `aiagent dx policy [--baseline ...] [--current ...] [--baseline-version V]` | Enforce the breaking-change / version-bump rule. |
| `aiagent run / validate / ci` | Pre-existing stable workflow commands (unchanged). |

## `aios.devkit` public API

### Scaffolding — `aios.devkit.scaffold`

- `DevKitScaffold.scaffold_artifact(kind, name, version="1.0.0", author="")`
  → `ScaffoldArtifact`. Deterministic: identical `(kind, name, version)`
  yields byte-identical output.
- `DevKitScaffold.verify_conformance(artifact)` → `dict` with
  `passed`, `architecture`, `contract`, `boundary`.
- `DevKitScaffold.render(artifact, base_dir)` → writes files to disk.
- `KIND_LAYER` — maps `capability|agent|tool|workflow` to its AIOS layer.
- `VALID_KINDS` — tuple of supported kinds.

### CLI wrapper — `aios.devkit.cli.DevKitCLI`

- `scaffold(kind, name, version, author)` → artifact `dict`.
- `verify(artifact_dict)` → conformance `dict`.
- (inherited from T047) `create / validate / test / simulate / package / inspect`.

### Actionable errors — `aios.devkit.errors`

- `ActionableError(message, *, cause, fix_hint, context=None)` — carries cause
  + fix hint instead of a bare traceback.
- `wrap_error(exc, *, cause, fix_hint)` — wrap any exception.
- `format_actionable(error)` — render for CLI output.
- `explain(error)` — structured `dict` for tooling.
- `CliStabilityError`, `CliVersionBumpRequired` — DX safety errors.

### CLI version policy — `aios.devkit.cli_version`

- `CLI_VERSION` — current public CLI version (SemVer).
- `CliVersionPolicy(current_version=CLI_VERSION)`:
  - `assert_stable(baseline_commands, current_commands, baseline_version=None)`
    → raises `CliVersionBumpRequired` on a breaking change without a bump.
  - `deprecate(command, since_version, remove_in)` → records a deprecation
    window.
- `is_breaking_change(baseline, current)` / `require_version_bump_if_breaking(...)`.

## Governance integration

- **Architecture 1.0 (T063):** `aios.governance.architecture.guard.ArchitectureGuard`
  is invoked on every generated `.py` file (classified by its layer path).
- **Contract 1.0 (T064):** `aios.extension_contracts.validator.ExtensionValidator`
  validates the generated spec and its import boundary.

## Conformance guarantees

- Generated skeletons import only stdlib → no ARCH-001..004 violations.
- Generated spec is compatible with contract `1.0.0` → T064 valid.
- Scaffolding is deterministic → same inputs, same artifact.
- No parallel DX system: only `aios.cli` + `aios.devkit` are used.
