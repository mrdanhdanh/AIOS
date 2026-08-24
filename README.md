# AIOS — Agent-First Operating System

Runtime-First · Plugin-First · Offline-First · Harness-Verified · Coding-Plane

AIOS is a deterministic, governance-enforced agent runtime. This README documents
the **standard job workflow** every task must follow so that no part of the system
is bypassed, and every execution leaves a durable, auditable trail.

## Quick start

```bash
pip install -e ".[dev]"            # Python >=3.11, pyyaml only runtime dep
python -m pytest aios -q           # all gates must stay green
```

## Architecture (layering is enforced)

```
Agent -> Orchestrator -> Runtime -> Capability -> Tool
```

Imports only go **downward** (enforced by `aios/governance/architecture/guard.py`).
Violations **block** the task (fail-closed).

## The standard AIOS job

Every job lives under `work/YYYYMMDD-short-slug/` and is driven through the real
governance pipeline + 7 gates. **A plain `aiagent execute` plan only runs shell
steps — it does NOT run the pipeline or gates by default.** To guarantee every
part of AIOS is exercised, use the dedicated command:

```bash
# Run the FULL pipeline (spec -> critique x2 -> breakdown -> review -> orchestrate)
# AND the 7 governance gates for a TASK, writing a durable log.
aiagent task TASK-xxx --job-dir work/<job>/logs
# or equivalently:
python work/<job>/scripts/run_task.py TASK-xxx --job-dir work/<job>/logs
```

The `orchestrate` step uses the **real** `Orchestrator` (wired to `TaskLifecycle` +
`UnifiedTaskGate`), so when a task has all mandatory artifacts and the unified gate
passes, the step reports `OK` and the task is closed to `DONE` for real (not a dry-run
skip). A task missing artifacts reports `SKIPPED` with the reason in the log.

### 7 governance gates (fail-closed)

`lifecycle · architecture · registry · dependency · evidence · test_evaluate · regression`
plus CI. Run standalone with:

```bash
python aios/governance/cli/gate_check.py --task TASK-xxx
```

### Durable execution log

`EvidenceStore` is in-memory only, so the **file on disk is the proof** a plan was
processed by AIOS. Every `aiagent execute` writes:

```
work/<job>/logs/execution-<exec_id>.json   # machine-readable
work/<job>/logs/execution-<exec_id>.log    # human-readable
```

`aiagent task` additionally writes `logs/task-TASK-xxx-<timestamp>.json`.

**How to verify a plan actually ran through AIOS:** open the log file — it must
contain an `execution_id` and per-step `COMPLETED`/`FAILED` lines. If `aiagent
execute` returned a shell error, AIOS did NOT process it.

## Job folder layout (MANDATORY)

Group files by function so the task folder never fills with loose files:

```
work/20260824-webno1/
  plans/      # ALL plan/workflow yaml (plan.yaml, plan-*.yaml)
  scripts/    # ALL generated source (.py, .ps1, .js, ...)
  site/       # static output / build artifacts (if any)
  logs/       # durable execution logs (auto-written)
  README.md   # optional, with commands updated to scripts/ paths
```

Rules:
- Every `plan*.yaml` MUST live in `plans/`.
- Every generated source file MUST live in `scripts/`.
- Keep output artifacts in their own functional folder.

## Writing a plan (AIOS Planner / `/aios-plan`)

Each node is ONE real command run via `subprocess` (a **non-Pure-PowerShell shell**,
so PowerShell-only syntax FAILS inside `command:`).

**FORBIDDEN in `command:`:** PowerShell cmdlets (`Get-Content`, `Set-Content`,
`Out-Null`, `Move-Item`, `Remove-Item`), flags (`-Force`, `-replace`), `mkdir a, b`,
and relying on `;`/`&&` as separators.

**REQUIRED patterns:**
- **Always use absolute paths** — `aiagent execute` runs from `--work-dir`, so
  repo-relative paths (`aios/...`, `scripts/...`) will NOT resolve.
- One real command per node; file edits via `python -c "..."` or `scripts/edit.py`.
- Keep `git commit`/`git push` **out of the plan** (the AIOS shell mishandles
  `git -C d:\...`); do them manually after the plan's work nodes complete.
- Confirm with the user before executing; run with:
  ```bash
  $env:AIOS_REAL_EXECUTION_ENABLED=1
  aiagent execute work/<job>/plans/plan.yaml --work-dir work/<job> --yes
  ```

## End-to-end example (meta-demo)

See `work/20260824-nihongo-n5/plans/plan-meta-demo.yaml` — it runs the full
pipeline + gates for `TASK-222` and verifies the durable log was written. This is
the reference template for any new governed job.

## Governance references

- `docs/PLAN.md`, `docs/AGENTS.md`, `docs/AIOS_Master_Task_Specification_M0-M26.md`
- `aios/governance/gates/unified.py`, `aios/governance/cli/gate_check.py`
- Skills: `aios-plan`, `aios-governance` · Agents: `aios-planner`, `aios-coordinator`
