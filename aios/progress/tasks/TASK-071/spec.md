# TASK-071 — AIOS 1.0 Developer Experience

## Objective
Bring Developer Experience (DX) to production quality: a stable versioned CLI,
architecture/contract-conforming scaffolding, actionable error messages, and
getting-started + reference docs for building capability/agent/tool/workflow
artifacts on AIOS 1.0. TASK-071 is DX tooling built on `aios/cli` + `aios/devkit`.

## Scope
**In scope**
- Stable, versioned `aiagent` CLI surface (version command + `dx` subcommands).
- Scaffold templates generating capability/agent/tool/workflow skeletons that
  CONFORM to Architecture 1.0 (T063) + Contract 1.0 (T064).
- Actionable error helper (cause + fix hint).
- Docs: `docs/dx/getting-started.md`, `docs/dx/reference.md`.
- Integration with `aios/governance/architecture` (T063 guard) and
  `aios/extension_contracts` (T064) via public imports (peer/downward only;
  `agents/` never imported).

**Out of scope**
- New runtime features, new contracts, dashboard (T072).
- Any parallel DX system (forbidden — use `aios/cli` + `aios/devkit`).

## Deliverables
- `aios/devkit/cli_version.py` — `CliVersionPolicy` + breaking-change rule.
- `aios/devkit/scaffold.py` — `scaffold_artifact` / `verify_conformance` / `render`.
- `aios/devkit/errors.py` — `format_actionable` / `explain` / `CliVersionBumpRequired`.
- `aios/devkit/cli.py` — `DevKitCLI.scaffold` / `verify`.
- `aios/cli/workflow_cli.py` — `version` + `dx scaffold|verify|policy` commands.
- `docs/dx/getting-started.md`, `docs/dx/reference.md`.
- Tests under `aios/devkit/tests/` + `aios/cli/tests/`.

## Acceptance Criteria
- AC1: CLI commands stable + versioned (`aiagent version`, `dx` group).
- AC2: Scaffold generates artifacts conforming to T063 + T064 (guard PASS).
- AC3: Error messages actionable (cause + fix hint).
- AC4: Docs getting-started + reference ready, valid links.
- AC5: Scaffold deterministic (same template + version → same artifact).
- AC6: Integrates with CLI + Devkit + Governance gates.
- AC7: No invariant violations; prior milestone tests unaffected.

## Dependencies
- TASK-063 Architecture 1.0 (guard).
- TASK-064 Contract Freeze (`aios.extension_contracts`).
- TASK-047 DevKit base (extended here).

## Governance references
- Rule 3 (Architecture) via `aios/governance/architecture/guard`.
- Rule 1..7 satisfied via `aios/governance/*`.
