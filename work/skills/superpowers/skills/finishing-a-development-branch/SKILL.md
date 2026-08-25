---
name: finishing-a-development-branch
description: "Use when implementation is complete and you are ready to verify, present options, and close the branch."
license: MIT
metadata:
  author: aios-integration
  version: "1.0.0"
---

# Finishing a Development Branch (AIOS-adapted)

## Process
1. Run the FULL verification gate (`verification-before-completion`): tests,
   linter, build, evidence.
2. Present options to your partner (merge / squash / keep / discard).
3. On choice, execute it. For merge/push, this is a side effect outside the
   worktree -> STOP and ask first.
4. Auto-commit source when the task reaches DONE (AIOS Rule 8 / Quy tắc 8).

## AIOS Mapping
- AIOS Rule 8 (Auto-COMMIT): a scheduled TASK reaching DONE (Unified Gate PASS)
  MUST commit source in the same session with message `TASK-xxx: <title> - DONE`
  plus PLAN.md/LOG.md/STATS.md updates. Never leave a dirty working tree.
- DONE only via `UnifiedTaskGate` (all 7 gates AND).
