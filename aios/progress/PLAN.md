# AIOS Progress Plan

Ordered task index and status. Status values: `PLANNED | SPECIFIED | ... | DONE | BLOCKED | DEPRECATED`.

| Task | Milestone | Title | Dependencies | Status |
|------|-----------|-------|--------------|--------|
| TASK-001 | M0 | Task Governance System | — | DONE |
| TASK-002 | M1 | Monorepo + aios_core Scaffold | TASK-001 | DONE |
| TASK-003 | M1 | Kernel Foundations | TASK-002 | DONE |
| TASK-004 | M1 | Runtime Services I | TASK-003 | DONE |
| TASK-005 | M1 | Runtime Services II | TASK-004 | DONE |
| TASK-006 | M1 | Model Contract + Provider Registry | TASK-004,TASK-005 | DONE |
| TASK-007 | M1 | Memory + Knowledge | TASK-003 | DONE |
| TASK-008 | M1 | Workflow Definition + Compiler | TASK-003 | READY |
| TASK-009 | M1 | Capability Foundation | TASK-003 | READY |
| TASK-011 | M1 | M1 Remediation / Architecture Hardening | TASK-005,TASK-009 | PLANNED |

> TASK-010 is intentionally sequenced after TASK-011 in this index to keep the
> M1 hardening gate coherent; see the master spec for canonical ordering.

## Next action

TASK-007 is `DONE` (326 tests green, Unified Gate PASS). Next: TASK-008 and TASK-009 remain `READY` (dependencies TASK-003 DONE).
