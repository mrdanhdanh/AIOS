---
name: subagent-driven-development
description: "Use when executing implementation plans with independent tasks in the current session."
license: MIT
metadata:
  author: aios-integration
  version: "1.0.0"
---

# Subagent-Driven Development (AIOS-adapted)

Execute plan by dispatching a fresh implementer subagent per task, a task review
(spec compliance + code quality) after each, and a broad whole-branch review at
the end.

## Core Principle
Fresh subagent per task + task review + broad final review = high quality, fast
iteration. Subagents never inherit your session context; you construct exactly
what they need.

## Continuous Execution
Do not pause to check in between tasks. Execute all tasks from the plan without
stopping. The only reasons to stop are: an irreversible/destructive operation; a
security-sensitive action; a side effect outside the worktree (merge, push,
publish); or a plan so broken every path is a guess.

## Rulings, not stalls
A running plan does not wait on a human. Conflicts, ambiguities, plan defects -
decide them. Record every decision in the ledger as
`Ruling: <what> - <why> - <cost if wrong>` and keep going.

## AIOS Mapping
- AIOS equivalent: `Orchestrator` dispatches `spec_writer`/`critic`/`reviewer`
  agents; each task gets its own `aios/progress/tasks/TASK-xxx/` lifecycle.
- The ledger == AIOS `AuditTrail` (runtime kernel) + `LOG.md`.
- Final broad review == AIOS `reviewer` agent producing `review.md`.
