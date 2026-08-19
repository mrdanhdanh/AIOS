# AIOS Progress Plan

Ordered task index and status. Status values: `PLANNED | SPECIFIED | ... | DONE | BLOCKED | DEPRECATED`.

| Task | Milestone | Title | Dependencies | Status |
|------|-----------|-------|--------------|--------|
| TASK-001 | M0 | Task Governance System | — | DONE |
| TASK-002 | M1 | Monorepo + aios_core Scaffold | TASK-001 | READY |
| TASK-003 | M1 | Kernel Foundations | TASK-002 | PLANNED |
| TASK-004 | M1 | Runtime Services I | TASK-003 | PLANNED |
| TASK-005 | M1 | Runtime Services II | TASK-004 | PLANNED |
| TASK-006 | M1 | Model Contract + Provider Registry | TASK-003 | PLANNED |
| TASK-007 | M1 | Memory + Knowledge | TASK-003 | PLANNED |
| TASK-008 | M1 | Workflow Definition + Compiler | TASK-003 | PLANNED |
| TASK-009 | M1 | Capability Foundation | TASK-003 | PLANNED |
| TASK-011 | M1 | M1 Remediation / Architecture Hardening | TASK-005,TASK-009 | PLANNED |

> TASK-010 is intentionally sequenced after TASK-011 in this index to keep the
> M1 hardening gate coherent; see the master spec for canonical ordering.

## Next action

TASK-002 is `READY` (its only dependency TASK-001 is `DONE`). Begin with
`spec.md` in `aios/progress/tasks/TASK-002/`.
