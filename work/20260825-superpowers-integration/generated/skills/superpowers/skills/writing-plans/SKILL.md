---
name: writing-plans
description: "Use when you have a spec or requirements for a multi-step task, before touching code."
license: MIT
metadata:
  author: aios-integration
  version: "1.0.0"
---

# Writing Plans (AIOS-adapted)

Write comprehensive implementation plans assuming the engineer has zero context
for our codebase and questionable taste. Document everything: files to touch,
code, testing, docs, how to test. Bite-sized tasks. DRY. YAGNI. TDD. Frequent
commits.

## Plan Document Header (every plan MUST start with this)
```markdown
# [Feature] Implementation Plan
**Goal:** [one sentence]
**Architecture:** [2-3 sentences]
**Tech Stack:** [key tech]
**Spec:** [path to spec this plan implements]
## Global Constraints
[verbatim project-wide requirements]
```

## Task Right-Sizing
A task is the smallest unit carrying its own test cycle + reviewer gate. Each
task ends with an independently testable deliverable.

## Bite-Sized Granularity (each step one action, 2-5 min)
- "Write the failing test" / "Run it to make sure it fails" /
  "Implement minimal code" / "Run tests, make sure they pass" / "Commit".

## AIOS Mapping
- AIOS equivalent: `aios-plan` skill + `plan.yaml` (WorkflowDefinition) under
  `work/YYYYMMDD-slug/`. One node = one real command.
- Bite-sized steps map to AIOS task breakdown (`tasks.md`).
- Save plans to `docs/superpowers/plans/YYYY-MM-DD-<feature>.md`.
