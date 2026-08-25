---
name: using-git-worktrees
description: "Use when starting implementation work that should be isolated from the main working tree."
license: MIT
metadata:
  author: aios-integration
  version: "1.0.0"
---

# Using Git Worktrees (AIOS-adapted)

## Process
1. Create an isolated workspace for the task (never implement on main without
   explicit consent).
2. Keep the worktree scoped to one plan/task.
3. Run verifications inside the worktree before any merge/push.

## AIOS Mapping
- AIOS convention: every job lives under `work/YYYYMMDD-slug/` (plans/, scripts/,
  logs/, generated source). This is AIOS's worktree-equivalent isolation.
- `aiagent execute --work-dir <dir>` runs plans in isolation.
