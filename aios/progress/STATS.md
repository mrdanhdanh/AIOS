# AIOS Progress Stats

| Metric | Value |
|--------|-------|
| Total tasks (master spec) | 219 |
| Tasks DONE | 134 |
| Tasks READY | 0 |
| Tasks PLANNED | 85 |
| Tasks BLOCKED | 0 |
| Governance modules | 7 (+ unified gate) |
| Automated gate tests | 2659 passed (2026-08-23) |
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

## M10 (TASK-063..075) — net new tests

M10 added **310** net-new automated tests (full suite 1962 → 2272). New packages:
`contracts`, `durable`, `autonomy_safety`, `kill_switch`, `reliability`, `cost_meter`;
extended: `governance/architecture`, `runtime`, `security`, `devkit`+`cli`,
`dashboard`, `certification`, `upgrade`, `model_router`.

## Per-module test counts (TASK-076..083, M11)

| Module | Tests |
|--------|-------|
| verification_integrity | 8 |
| replay | 5 |
| visual_evidence | 6 |
| asset_pipeline | 7 |
| creative_domain | 7 |
| skill_distiller | 6 |
| **Subtotal** | **39** |

> TASK-076/TASK-077 are reserved (no implementation/tests). M11 added **40** net-new
> automated tests (full suite 2272 → 2312). New packages: `verification_integrity`,
> `replay`, `visual_evidence`, `asset_pipeline`, `creative_domain`, `skill_distiller`.

## Per-module test counts (TASK-084..088, M12)

| Module | Tests |
|--------|-------|
| versioning | 9 |
| migration | 8 |
| backward_compat | 7 |
| conformance | 7 |
| compat_docs | 7 |
| **Subtotal** | **38** |

> M12 added **38** net-new automated tests (full suite 2312 → 2350). New packages:
> `versioning`, `migration`, `backward_compat`, `conformance`, `compat_docs`.
> Plus `docs/adr/ADR-Compatibility.md` + 4 compatibility guides. T084-T088 all DONE.

## Per-module test counts (TASK-089..093, M13)

| Module | Tests |
|--------|-------|
| behavioral | 9 |
| harness_coverage | 7 |
| meta_harness | 7 |
| readiness_trust | 6 |
| behavioral_docs | 6 |
| **Subtotal** | **35** |

> M13 added **35** net-new automated tests (full suite 2350 → 2385). New packages:
> `behavioral`, `harness_coverage`, `meta_harness`, `readiness_trust`, `behavioral_docs`.
> Plus `docs/behavioral_spec.md` + `docs/adr/ADR-0008.md`. T089-T093 all DONE.

## Per-module test counts (TASK-094..098, M14)

| Module | Tests |
|--------|-------|
| remediation_detect | 9 |
| remediation_candidate | 7 |
| remediation_simulation | 7 |
| remediation_apply | 6 |
| remediation_integrity | 6 |
| **Subtotal** | **35** |

> M14 added **35** net-new automated tests (full suite 2385 → 2420). New packages:
> `remediation_detect`, `remediation_candidate`, `remediation_simulation`,
> `remediation_apply`, `remediation_integrity`. T094-T098 all DONE (Remediation chain).

## Per-module test counts (TASK-099..103, M15)

| Module | Tests |
|--------|-------|
| autonomous_harness_loop | 6 |
| failure_corpus | 6 |
| continuous_certification | 6 |
| trust_budget | 6 |
| autonomy_constitution | 6 |
| **Subtotal** | **30** |

> M15 added **30** net-new automated tests (full suite 2420 → 2450). New packages:
> `autonomous_harness_loop`, `failure_corpus`, `continuous_certification`,
> `trust_budget`, `autonomy_constitution`. T099-T103 all DONE (Autonomous Harness).

## Per-module test counts (TASK-104..108, M16)

| Module | Tests |
|--------|-------|
| independent_harness/foundation (T104) | 6 |
| independent_harness/oracle (T105) | 6 |
| independent_harness/behavioral_bridge (T106) | 6 |
| independent_harness/permission_sandbox_bridge (T107) | 6 |
| independent_harness/console (T108) | 5 |
| **Subtotal** | **29** |

> M16 added **29** net-new automated tests (full suite 2450 → 2479). New package:
> `independent_harness` (foundation/oracle/behavioral_bridge/permission_sandbox_bridge/console)
> + `aios/api/routers/independent_harness.py` + `IndependentHarnessView` (Dashboard View 11).
> T104-T108 all DONE (Independent Harness Integration). AIOS retains policy authority.

## Per-module test counts (TASK-109..116, M17)

| Module | Tests |
|--------|-------|
| model_runtime/contracts (T109) | 6 |
| model_runtime/provider_registry (T110) | 6 |
| model_runtime/model_registry (T111) | 6 |
| model_runtime/orchestration (T112) | 4 |
| model_runtime/security (T113) | 6 |
| model_runtime/resilience (T114) | 6 |
| model_runtime/usage (T115) | 5 |
| model_runtime/conformance (T116) | 6 |
| **Subtotal** | **45** |

> M17 added **45** net-new automated tests (full suite 2479 → 2519). New package:
> `aios/model_runtime` (contracts/provider_registry/model_registry/orchestration/security/resilience/usage/conformance)
> integrating T001 (Evidence), T025 (Health), T035 (Identity/RBAC), T040 (Credential),
> T049 (Certification), T078 (Integrity), T039 (Quota). T109-T116 all DONE (Model Runtime).
> Vendor-neutral, deterministic-first, fail-closed; no LLM in resolver/orchestration.

## Per-module test counts (TASK-117..124, M18)

| Module | Tests |
|--------|-------|
| context/scanner (T117) | 6 |
| context/symbol_index (T118) | 6 |
| context/dependency_graph (T119) | 6 |
| context/hybrid_index (T120) | 6 |
| context/retriever (T121) | 6 |
| context/builder (T122) | 6 |
| context/verification (T123) | 6 |
| context/conformance (T124) | 6 |
| **Subtotal** | **48** |

> M18 added **48** net-new automated tests (full suite → 2579). New package:
> `aios/context` (scanner/symbol_index/dependency_graph/hybrid_index/retriever/builder/verification/conformance)
> integrating T001 (Evidence), T078 (Integrity), T040/T113 (Security), T024 (Context Optimizer).
> T117-T124 all DONE (Context Pipeline). Deterministic-first, fail-closed, no LLM in any stage.

## Per-module test counts (TASK-125, M19)

| Module | Tests |
|--------|-------|
| coder/contract (CoderAgentContract) | 4 |
| coder/contract (CoderAgentStateMachine) | 6 |
| coder/contract (architecture/layer) | 2 |
| **Subtotal** | **12** |

> M19 opened with **12** net-new automated tests (full suite → 2591). New package:
> `aios/coder` (contract) integrating T001 (Evidence/Rule 5/6), T013 (Worker), T113 (Policy), ARCH (Guard).
> T125 DONE (Coder Agent Contract + State Machine). Deterministic-first, fail-closed, provenance on every transition.

## Per-module test counts (TASK-126, M19)

| Module | Tests |
|--------|-------|
| coder/planner (CodingPlanner) | 4 |
| coder/planner (PlanVerifier) | 4 |
| coder/planner (architecture/provenance) | 1 |
| **Subtotal** | **9** |

> T126 DONE (Coding Planner + PlanVerifier). Deterministic-first (rule trước LLM, llm_call_count=0), fail-closed verify (T078), provenance (T001 Rule 5).

## Per-module test counts (TASK-127, M19)

| Module | Tests |
|--------|-------|
| coder/generation (CodeGenerationRuntime) | 4 |
| coder/generation (fail-closed/deterministic) | 2 |
| coder/generation (architecture/capability) | 1 |
| **Subtotal** | **7** |

> T127 DONE (Code Generation Runtime). Capability dispatch (ARCH-004), artifact hash (T078), provenance (T001 Rule 5), deterministic + fail-closed.

## Per-module test counts (TASK-128, M19)

| Module | Tests |
|--------|-------|
| coder/patch (diff/apply) | 4 |
| coder/patch (fail-closed/rollback) | 3 |
| coder/patch (architecture/provenance) | 1 |
| **Subtotal** | **8** |

> T128 DONE (Patch Engine). Backup-before-apply (T020), rollback-to-certified (T020/T066), fail-closed, deterministic diff, provenance (T001 Rule 5).

## Per-module test counts (TASK-129, M19)

| Module | Tests |
|--------|-------|
| coder/review (CodeReviewAgent) | 5 |
| coder/review (fail-closed/deterministic) | 2 |
| coder/review (architecture/provenance) | 1 |
| **Subtotal** | **8** |

> T129 DONE (Code Review Agent). I/O-free, capability-injected (T125), fail-closed verdict (T078), no God Object (T022), provenance (T001 Rule 5), deterministic.

## Per-module test counts (TASK-130, M19)

| Module | Tests |
|--------|-------|
| coder/artifact (CodingArtifact) | 4 |
| coder/artifact (fail-closed/integrity) | 3 |
| coder/artifact (architecture/immutable) | 1 |
| **Subtotal** | **8** |

> T130 DONE (Coding Artifact + CodingEvidence). Standardized 3-kind artifact (T078 hash), provenance chain (T001 Rule 5), fail-closed integrity gate, immutable id (T001 Rule 1), deterministic. **M19 COMPLETE** (T125-T130, 52 new tests).

## Per-module test counts (TASK-131, M19)

| Module | Tests |
|--------|-------|
| coder/conformance (CoderConformanceHarness) | 6 |
| coder/conformance (fail-closed/UNKNOWN) | 2 |
| coder/conformance (architecture/provenance) | 1 |
| **Subtotal** | **9** |

> T131 DONE (Coder Conformance Harness + Security). Fail-closed invariants (T078), UNKNOWN never promoted, security boundary (T113), provenance (T001 Rule 5).

## Per-module test counts (TASK-132, M19)

| Module | Tests |
|--------|-------|
| coder/autonomy (AutonomyPermissionBroker) | 6 |
| coder/autonomy (fail-closed/policy) | 2 |
| coder/autonomy (architecture/provenance) | 1 |
| **Subtotal** | **9** |

> T132 DONE (Autonomy Level + Permission Integration). 3-level mapping, fail-closed permission (T113), provenance (T001 Rule 5).

## Per-module test counts (TASK-133, M19)

| Module | Tests |
|--------|-------|
| coder/prompt (PromptRegistry) | 4 |
| coder/prompt (PromptBuilder) | 4 |
| coder/prompt (architecture/provenance) | 1 |
| **Subtotal** | **9** |

> T133 DONE (Prompt Architecture + PromptBuilder + Versioning). Immutable versioning (T001 Rule 1), fail-closed build (T078), provenance (T001 Rule 5), deterministic.

## Grand total

| **Total** | **1253** |

## Per-module test counts (TASK-219)

| Module | Tests |
|--------|-------|
| skill/github_bridge/parser | 3 |
| skill/github_bridge/adapter | 2 |
| skill/github_bridge/converter | 3 |
| skill/github_bridge/architecture | 1 |
| skill/github_bridge/real_skill | 3 |
| skill/github_bridge/persisted | 1 |
| **Subtotal** | **13** |
