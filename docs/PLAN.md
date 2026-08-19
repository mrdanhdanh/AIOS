# AIOS — Project Plan (M0)

> **Runtime-First · Plugin-First · Offline-First · Harness-Verified · Coding-Plane**
>
> This document is the **entry point** for any new session. Together with
> `AGENTS.md` and `aios/progress/README.md` it is sufficient to continue work
> without any chat memory.

## 1. Vision

AIOS is an AI Operating System whose control substrate is the **Runtime**.
Workers/Agents never bypass Runtime, Capability, Permission or Policy. The LLM
is **not** the default control plane — a deterministic path runs first.

## 2. Milestones (high level)

| Milestone | Theme |
|-----------|-------|
| M0 | Task Governance System (this task) |
| M1 | Monorepo + runtime foundations |
| M2 | Orchestration + workers + tools |
| M3 | API + dashboard + extension |
| M4 | Upgrade / observability / orchestrator v2 |
| M5–M26 | Memory, harness, enterprise, autonomy, certification, … |

See `AIOS_Master_Task_Specification_M0-M26.md` for the full task index.

## 3. M0 — Task Governance System (TASK-001)

TASK-001 turns the 7 general rules into a self-verifying control plane
implemented as automated gates. Every later task is enforced through it.

| Rule | Component | Module |
|------|-----------|--------|
| 1 | Task Registry | `aios/governance/task_registry` |
| 2 | Dependency Graph | `aios/governance/dependency` |
| 3 | Architecture Guard | `aios/governance/architecture` |
| 4 | Deterministic Control Path | `aios/governance/deterministic` |
| 5 | Evidence Store | `aios/governance/evidence` |
| 6 | Task State Machine | `aios/governance/lifecycle` |
| 7 | Regression Gate | `aios/governance/regression` |

All seven converge in `aios/governance/gates` (Unified Task Gate).

### Unified Gate

```
Registry AND Dependency AND Architecture AND Lifecycle
AND Evidence AND Test/Evaluate AND Regression  =>  DONE
else  =>  BLOCKED
```

## 4. How to continue in a new session

1. Read `docs/PLAN.md` (this file).
2. Read `docs/AGENTS.md` (agent responsibilities + boundaries).
3. Read `aios/progress/README.md` (task folder layout + lifecycle).
4. Run `python -m pytest aios -q` to see current gate status.
5. Pick the next READY task from `aios/progress/PLAN.md`.

## 5. Repo layout

```
aios/
  core/  runtime/  harness/        # namespace placeholders (M0)
  governance/                     # TASK-001 implementation + tests
  agents/                         # orchestrator / spec-writer / critic / reviewer
  progress/                       # PLAN.md LOG.md STATS.md tasks/<TASK-xxx>/
docs/
  PLAN.md  AGENTS.md  AIOS_Master_Task_Specification_M0-M26.md
```

## 6. Definition of Done (per task)

```
PLAN -> SPEC -> CRITIQUE x2 -> BREAKDOWN -> REVIEW
-> IMPLEMENT -> TEST -> EVALUATE -> REGRESSION -> PROGRESS/LOG -> COMMIT
```
