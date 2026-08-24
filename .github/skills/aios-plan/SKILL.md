---
name: aios-plan
description: "AIOS Plan Generator — Use when the user wants to turn a natural-language task into a runnable AIOS plan.yaml (WorkflowDefinition with real shell/git commands) saved under work/YYYYMMDD-slug/, then confirm before executing via `aiagent execute` (TASK-222/224). Pairs with the AIOS Planner agent."
---

# /aios-plan — Generate a runnable AIOS plan

Convert a plain-language request into a `plan.yaml` that AIOS can execute for real
(no LLM inside AIOS, no external API — suitable for weak/offline machines).

## When to use
- User says: "lập plan cho AIOS", "tạo plan.yaml để chạy", "dùng AIOS làm X", or invokes
  `/aios-plan <yêu cầu>`.

## How to produce the plan
Emit a YAML file matching `aios/runtime/workflow/definition.py` `WorkflowDefinition`.
Each node is ONE real command (run via `subprocess` by TASK-222):

```yaml
workflow:
  name: <human or kebab name>
  version: 0.1.0
  permissions: [process.execute]
  nodes:
    - id: step-1
      type: task
      command: echo "starting"
    - id: step-2
      type: task
      command: git status
```

Rules:
- `permissions: [process.execute]` is REQUIRED (runtime policy pre-check).
- One `command` per node; real shell/git only; no placeholders.
- Never emit destructive commands (`rm -rf /`, `format`, `mkfs`, `shutdown`, `reboot`).
- Markdown fallback: a `- [ ] <command>` list is also accepted by `aiagent execute plan.md`
  (TASK-222 `from_markdown`).

## Directory convention (WORK DIR)
Save the plan under `work/YYYYMMDD-short-slug/` at the repo root, e.g.
`work/20260824-webno1/`. **Group files by function into subfolders** so the task
folder never fills up with loose `.py`/`.yaml` files when a job is re-run many times:

```
d:\AIOS\work\20260824-webno1\
  plans\            # ALL plan/workflow yaml files (plan.yaml, plan-*.yaml)
    plan.yaml
  scripts\          # ALL generated source files (.py, .ps1, .js, ...)
    generate.py
    serve.py
  site\             # static output / build artifacts (if any)
  <other-output>\   # any other functional output folder
  README.md         # optional, with commands updated to scripts/ paths
```

Rules:
- Every `plan*.yaml` MUST live in `plans/` (never loose in the task root).
- Every generated source file (`.py`, `.ps1`, `.js`, …) MUST live in `scripts/`.
- Keep output artifacts (e.g. `site/`) in their own functional folder.
- When writing a plan, reference scripts with their `scripts/` path
  (e.g. `python scripts/generate.py`), and update `README.md` accordingly.
- This layout is MANDATORY for every new job — do not leave loose files in the
  task root.

## Confirm before executing
After writing the plan, ASK the user: "Bạn có muốn thực hiện plan này không? (yes/no)".
Only when they reply yes, run (real execution must be enabled):

```bash
$env:AIOS_REAL_EXECUTION_ENABLED=1
aiagent execute d:\AIOS\work\20260824-webno1\plans\plan.yaml --work-dir d:\AIOS\work\20260824-webno1 --yes
```

- `--work-dir <dir>` tells AIOS to create/use that folder and confine execution to it
  (sandbox `allowed_cwd`), so generated files stay inside the job folder.
- `--yes` skips any interactive prompt (used when the user already approved).
- To dry-run (validate only, 0 execution): `aiagent execute <dir>/plan.yaml --simulate`.

## Pairing
- Agent version: `.github/agents/aios-planner.agent.md` (chat picker).
- Execution engine: TASK-222 (`aios/runtime/process.py` + `aiagent execute`) + TASK-224
  (work-dir + confirm flow).
