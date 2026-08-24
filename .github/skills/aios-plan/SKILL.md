---
name: aios-plan
description: "AIOS Plan Generator — Use when the user wants to turn a natural-language task into a runnable AIOS plan.yaml (WorkflowDefinition with real shell/git commands) that can be executed via `aiagent execute plan.yaml` (TASK-222). Pairs with the AIOS Planner agent."
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

## After generating
1. Write the file (e.g. `d:\AIOS\plan.yaml`).
2. Tell the user to enable real execution, then run:
   ```bash
   # configs/default.yaml: real_execution.enabled: true   (or)
   $env:AIOS_REAL_EXECUTION_ENABLED=1
   aiagent execute d:\AIOS\plan.yaml
   ```
3. To dry-run (validate only, 0 execution): `aiagent execute d:\AIOS\plan.yaml --simulate`.

## Pairing
- Agent version: `.github/agents/aios-planner.agent.md` (chat picker).
- Execution engine: TASK-222 (`aios/runtime/process.py` + `aiagent execute`).
