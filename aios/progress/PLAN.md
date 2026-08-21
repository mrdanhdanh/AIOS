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
| TASK-008 | M1 | Workflow Definition + Compiler | TASK-003 | DONE |
| TASK-009 | M1 | Capability Foundation | TASK-003 | DONE |
| TASK-011 | M1 | M1 Remediation / Architecture Hardening | TASK-005,TASK-009 | DONE |
| TASK-010 | M2 | Decision Pipeline | TASK-011 | DONE |

> TASK-010 is intentionally sequenced after TASK-011 in this index to keep the
> M1 hardening gate coherent; see the master spec for canonical ordering.

| TASK-012 | M2 | Operational Orchestration | TASK-010 | DONE |
| TASK-013 | M2 | Worker Plane | TASK-010,TASK-012 | DONE |
| TASK-014 | M2 | Tool + Capability Layer | TASK-010,TASK-012,TASK-013 | DONE |
| TASK-015 | M2 | Plugin / Skill Execution | TASK-014 | DONE |
| TASK-016 | M2 | Architecture Hardening | TASK-010,TASK-011,TASK-012,TASK-013,TASK-014,TASK-015 | DONE |
| TASK-017 | M3 | FastAPI REST + WebSocket | TASK-010,TASK-011,TASK-012,TASK-013,TASK-014,TASK-015,TASK-016 | DONE |

| TASK-018 | M3 | Dashboard SPA | TASK-017 | DONE |
| TASK-019 | M3 | VS Code Extension | TASK-017 | DONE |
| TASK-020 | M4 | Upgrade Pipeline | TASK-019 | DONE |
| TASK-021 | M4 | Observability | TASK-020 | DONE |
| TASK-022 | M4 | Orchestrator v2 | TASK-021 | DONE |
| TASK-023 | M5 | Memory Coordinator | TASK-022 | DONE |
| TASK-024 | M5 | Context Optimizer | TASK-023 | DONE |

## Next action

TASK-024 `DONE` (1670 tests, 21 context optimizer + 1649 inherited, AC-024-01..17 PASS). Next: TASK-025 `READY` (Model Router).
