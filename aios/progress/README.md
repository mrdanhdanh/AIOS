# AIOS Progress — How tasks are tracked

This file is the **operational companion** to `docs/PLAN.md` and `docs/AGENTS.md`.
A new session can continue after reading those three documents, with no chat
memory required.

## 1. Task folder standard

Every task lives under `aios/progress/tasks/<TASK-xxx>/` and contains:

```
spec.md          # Objective / Scope / Deliverables / Acceptance / Dependencies
critique-1.md    # first critique
critique-2.md    # second critique
tasks.md         # breakdown into actionable subtasks
review.md        # review before implementation
implementation/  # source, tests, docs produced for the task
test.md          # how the task is verified
evaluation.md    # evaluation against acceptance criteria
```

Use `aios/progress/tasks/_TEMPLATE/` as the starting skeleton.

## 2. Lifecycle (Rule 6 — Task State Machine)

```
PLANNED -> SPECIFIED -> CRITIQUED_1 -> CRITIQUED_2 -> BROKEN_DOWN
-> REVIEWED -> IMPLEMENTING -> TESTING -> EVALUATING
-> REGRESSION -> READY_TO_CLOSE -> DONE
```

Each transition requires its mandatory artifact (enforced by
`aios/governance/lifecycle`). `DEPRECATED` and `BLOCKED` are terminal
governance statuses.

## 3. Closing a task (Unified Gate)

A task may reach `DONE` only when the Unified Task Gate passes:

```
Registry AND Dependency AND Architecture AND Lifecycle
AND Evidence AND Test/Evaluate AND Regression
```

## 4. Progress index

- `PLAN.md` — ordered task list with status.
- `LOG.md` — append-only event log.
- `STATS.md` — aggregate counts.

## 5. CLI

- `python aios/governance/cli/parse_spec.py` — build a registry from the master
  spec and validate Rule 1 / Rule 2.
- `python aios/governance/cli/gate_check.py --task TASK-001` — run the unified
  gate for a task folder.
