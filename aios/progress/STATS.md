# AIOS Progress Stats

| Metric | Value |
|--------|-------|
| Total tasks (master spec) | 182 |
| Tasks DONE | 16 |
| Tasks READY | 1 |
| Tasks PLANNED | 165 |
| Governance modules | 7 (+ unified gate) |
| Automated gate tests | 1257 |
| Architecture rules (ARCH-A..H + ARCH-001..004) | 17 |
| Lifecycle states | 12 |

## Per-module test counts (TASK-001)

| Module | Tests |
|--------|-------|
| task_registry | 6 |
| dependency | 5 |
| lifecycle | 4 |
| evidence | 3 |
| architecture | 6 |
| deterministic | 4 |
| regression | 3 |
| gates (unified) | 4 |
| agents | 4 |
| **Subtotal** | **39** |

## Per-module test counts (TASK-002)

| Module | Tests |
|--------|-------|
| core/config | 14 |
| core/logging | 8 |
| core/metadata | 8 |
| core/healthcheck | 8 |
| core/smoke | 5 |
| **Subtotal** | **43** |

## Per-module test counts (TASK-003)

| Module | Tests |
|--------|-------|
| core/version | 14 |
| core/contracts | 10 |
| core/container | 12 |
| core/events | 10 |
| core/planner | 18 |
| core/smoke (updated) | 5 |
| **Subtotal** | **78** |

## Per-module test counts (TASK-004)

| Module | Tests |
|--------|-------|
| runtime/context | 10 |
| runtime/audit | 8 |
| runtime/artifact | 11 |
| runtime/permission | 8 |
| runtime/policy | 8 |
| **Subtotal** | **45** |

## Per-module test counts (TASK-005)

| Module | Tests |
|--------|-------|
| runtime/execution | 8 |
| runtime/scheduler | 7 |
| runtime/state | 7 |
| runtime/resource | 7 |
| runtime/kernel | 5 |
| **Subtotal** | **34** |

## Per-module test counts (TASK-006)

| Module | Tests |
|--------|-------|
| runtime/providers/contract | 5 |
| runtime/providers/adapters | 10 |
| runtime/providers/registry | 12 |
| **Subtotal** | **27** |

## Per-module test counts (TASK-007)

| Module | Tests |
|--------|-------|
| runtime/memory | 27 |
| runtime/knowledge | 33 |
| **Subtotal** | **60** |

## Per-module test counts (TASK-009)

| Module | Tests |
|--------|-------|
| capability/capability | 34 |
| capability/prompt | 27 |
| capability/catalog | 24 |
| capability/graph | 38 |
| capability/architecture | 5 |
| capability/kernel_wiring | 5 |
| harness delta (existing suites re-collected) | 11 |
| **Subtotal** | **144** |

## Per-module test counts (TASK-008)

| Module | Tests |
|--------|-------|
| runtime/workflow (definition/validation/compiler/simulation/CLI/contract) | 39 |
| runtime/workflow/architecture | 5 |
| **Subtotal** | **44** |

## Per-module test counts (TASK-011 — M1 Remediation)

| Module | Tests |
|--------|-------|
| governance/architecture hardening | 30 |
| **Subtotal** | **30** |

## Per-module test counts (TASK-010 — Decision Pipeline)

| Module | Tests |
|--------|-------|
| orchestrator/normalizer | 12 |
| orchestrator/rule_engine | 5 |
| orchestrator/workflow_matcher | 8 |
| orchestrator/execution_plan | 9 |
| orchestrator/planner | 6 |
| orchestrator/decision_pipeline | 13 |
| orchestrator/architecture | 4 |
| **Subtotal** | **57** |

## Per-module test counts (TASK-012 — Operational Orchestration)

| Module | Tests |
|--------|-------|
| orchestrator/goal_manager | 19 |
| orchestrator/task_queue | 24 |
| orchestrator/permission_broker | 12 |
| orchestrator/failure_recovery | 18 |
| orchestrator/orchestration_integration | 16 |
| **Subtotal** | **89** |

## Per-module test counts (TASK-013 — Worker Plane)

| Module | Tests |
|--------|-------|
| worker/contract | 27 |
| worker/lifecycle | 22 |
| worker/registry | 20 |
| worker/router | 18 |
| worker/execution | 22 |
| worker/workers | 28 |
| worker/architecture | 10 |
| worker/integration | 14 |
| **Subtotal** | **161** |

## Per-module test counts (TASK-014 — Tool + Capability Layer)

| Module | Tests |
|--------|-------|
| tool/contracts | 32 |
| tool/registry | 38 |
| tool/adapters | 42 |
| tool/router | 38 |
| tool/policy_integration | 10 |
| tool/architecture | 8 |
| runtime/capability_router | 7 |
| **Subtotal** | **163** |

## Per-module test counts (TASK-015 — Plugin / Skill Execution)

| Module | Tests |
|--------|-------|
| skill/contracts | 12 |
| skill/registry | 14 |
| skill/resolver | 14 |
| skill/manager | 38 |
| skill/sandbox | 22 |
| skill/integration | 18 |
| skill/persistence | 16 |
| skill/rollback | 18 |
| skill/architecture | 15 |
| **Subtotal** | **167** |

## Per-module test counts (TASK-016 — Architecture Hardening)

| Module | Tests |
|--------|-------|
| governance/architecture (scanner/graph/rules/gate/report/violations) | 44 |
| governance/architecture/test_import_boundaries | 12 |
| governance/architecture/test_layer_rules | 11 |
| governance/architecture/test_invariants | 13 |
| governance/architecture/test_cycles | 8 |
| governance/architecture/test_policy_bypass | 7 |
| governance/architecture/test_capability_boundary | 7 |
| governance/architecture/test_workflow_engine_independence | 5 |
| governance/architecture/test_plugin_isolation | 5 |
| **Subtotal** | **112** |

## Grand total

| **Total** | **1257** |
