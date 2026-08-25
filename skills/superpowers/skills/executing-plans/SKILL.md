---
name: executing-plans
description: "Use when you have a written implementation plan to execute in a separate session with review checkpoints."
license: MIT
metadata:
  author: aios-integration
  version: "1.0.0"
---

# Executing Plans (AIOS-adapted)

Load plan, review critically, execute all tasks, report when complete.

## The Process
### Step 1: Load and Review Plan
1. Ensure an isolated workspace (`using-git-worktrees`).
2. Read plan; review critically; raise concerns before starting.
3. Create todos for plan items; proceed.

### Step 2: Execute Tasks
For each task: mark in_progress -> follow each step exactly -> run verifications
as specified -> mark completed.

### Step 3: Complete Development
Announce `finishing-a-development-branch`; follow it to verify tests, present
options, execute choice.

## When to Stop and Ask
Hit a blocker (missing dep, test fails, unclear instruction), plan has critical
gaps, or you do not understand an instruction. Ask rather than guess.

## AIOS Mapping
- AIOS equivalent: `aiagent execute <plan.yaml> --work-dir <dir> --yes` after
  `AIOS_REAL_EXECUTION_ENABLED=1`.
- Review checkpoints == AIOS `REVIEWED` + `UnifiedTaskGate`.
- Never implement on main without explicit consent (AIOS working-tree hygiene).
