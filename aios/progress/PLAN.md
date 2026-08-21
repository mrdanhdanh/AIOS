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
| TASK-025 | M5 | Model Router | TASK-024 | DONE |
| TASK-026 | M5 | Planning Engine | TASK-025 | DONE |
| TASK-027 | M5 | Execution Graph | TASK-026 | DONE |
| TASK-028 | M5 | Parallel Scheduler | TASK-027 | DONE |
| TASK-029 | M6 | Harness Kernel | TASK-028 | DONE |
| TASK-030 | M6 | Execution Verification | TASK-029 | DONE |
| TASK-031 | M6 | Test Harness + Scenario | TASK-030 | DONE |
| TASK-032 | M6 | Evaluation Harness | TASK-031 | DONE |
| TASK-033 | M6 | Benchmark + Regression | TASK-032 | DONE |
| TASK-034 | M6 | Doctor + Readiness | TASK-033 | DONE |
| TASK-035 | M7 | Identity + RBAC | — | DONE |
| TASK-036 | M7 | Multi-Tenancy | — | DONE |
| TASK-037 | M7 | Distributed Runtime | — | DONE |
| TASK-038 | M7 | Distributed Scheduler | — | DONE |
| TASK-039 | M7 | Quota + Cost | — | DONE |
| TASK-040 | M7 | Credential Isolation | — | DONE |
| TASK-041 | M7 | HA + Audit + Recovery | — | DONE |
| TASK-042 | M7 | Enterprise Operations | — | DONE |

## Next action

TASK-042 `DONE` (1798 tests, 42 new for M7 infrastructure tasks, AC-035..042 PASS). M7 COMPLETE. Next: TASK-043 `READY` (Public SDK).
