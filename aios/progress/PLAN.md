# AIOS Progress Plan

Ordered task index and status. Status values: `PLANNED | SPECIFIED | ... | DONE | BLOCKED | DEPRECATED`.

| Task | Milestone | Title | Dependencies | Status |
|------|-----------|-------|--------------|--------|
| TASK-001 | M0 | Task Governance System | — | DONE |
| TASK-002 | M1 | Monorepo + aios Scaffold | TASK-001 | DONE |
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
| TASK-014 | M2 | Tool + Capability Layer | TASK-010,TASK-013 | DONE |
| TASK-015 | M2 | Plugin / Skill Execution | TASK-014 | DONE |
| TASK-016 | M2 | Architecture Hardening | TASK-010,TASK-011,TASK-012,TASK-013,TASK-014,TASK-015 | DONE |
| TASK-017 | M3 | FastAPI REST + WebSocket | TASK-016 | DONE |

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
| TASK-035 | M7 | Identity + RBAC | TASK-034 | DONE |
| TASK-036 | M7 | Multi-Tenancy | TASK-035 | DONE |
| TASK-037 | M7 | Distributed Runtime | TASK-036 | DONE |
| TASK-038 | M7 | Distributed Scheduler | TASK-037 | DONE |
| TASK-039 | M7 | Quota + Cost | TASK-038 | DONE |
| TASK-040 | M7 | Credential Isolation | TASK-039 | DONE |
| TASK-041 | M7 | HA + Audit + Recovery | TASK-040 | DONE |
| TASK-042 | M7 | Enterprise Operations | TASK-041 | DONE |
| TASK-043 | M8 | Public SDK | TASK-042 | DONE |
| TASK-044 | M8 | Plugin Runtime | TASK-043 | DONE |
| TASK-045 | M8 | Extension Contracts | TASK-044 | DONE |
| TASK-046 | M8 | Ecosystem Registry | TASK-045 | DONE |
| TASK-047 | M8 | Developer Kit | TASK-046 | DONE |
| TASK-048 | M8 | Ecosystem Hub | TASK-047 | DONE |
| TASK-049 | M8 | Certification | TASK-048 | DONE |
| TASK-050 | M9 | Autonomous Goal Engine | TASK-049 | DONE |
| TASK-051 | M9 | Autonomous Planner | TASK-050 | DONE |
| TASK-052 | M9 | World Model | TASK-051 | DONE |
| TASK-053 | M9 | Autonomous Loop | TASK-051 | DONE |
| TASK-054 | M9 | Autonomy Governor | TASK-053 | DONE |
| TASK-055 | M9 | Autonomous Recovery | TASK-054 | DONE |
| TASK-056 | M9 | Goal Durability | TASK-055 | DONE |
| TASK-057 | M9 | Autonomous Memory | TASK-056 | DONE |
| TASK-058 | M9 | Autonomous Experimentation | TASK-057 | DONE |
| TASK-059 | M9 | Multi-Agent Autonomy | TASK-058 | DONE |
| TASK-060 | M9 | Autonomous Evaluation | TASK-059 | DONE |
| TASK-061 | M9 | Advanced Stuck Detection | TASK-060 | DONE |
| TASK-062 | M9 | Autonomous Scheduler | TASK-054 | DONE |
| TASK-063 | M10 | AIOS Architecture 1.0 | TASK-062 | DONE |
| TASK-064 | M10 | Public Contract Freeze | TASK-063 | DONE |
| TASK-065 | M10 | Runtime Production Hardening | TASK-064 | DONE |
| TASK-066 | M10 | Durable Execution 1.0 | TASK-065 | DONE |
| TASK-067 | M10 | Autonomy Safety 1.0 | TASK-066 | DONE |
| TASK-068 | M10 | Kill Switch | TASK-067 | DONE |
| TASK-069 | M10 | Reliability Engineering | TASK-068 | DONE |
| TASK-070 | M10 | AIOS Security Baseline | TASK-069 | DONE |
| TASK-071 | M10 | AIOS 1.0 Developer Experience | TASK-070 | DONE |
| TASK-072 | M10 | AIOS Dashboard 1.0 | TASK-071 | DONE |
| TASK-073 | M10 | AIOS 1.0 Certification Suite | TASK-072 | DONE |
| TASK-074 | M10 | Upgrade & Migration 1.0 | TASK-073 | DONE |
| TASK-075 | M10 | Performance & Cost + Model Independence | TASK-074 | DONE |
| TASK-076 | M11 | Reserved / Not Specified in Source | TASK-075 | DONE |
| TASK-077 | M11 | Reserved / Not Specified in Source | TASK-076 | DONE |
| TASK-078 | M11 | Verification Integrity / Fail-Closed Gate | TASK-077 | DONE |
| TASK-079 | M11 | RenderReplay / Deterministic Harness | TASK-078 | DONE |
| TASK-080 | M11 | Visual Evidence + Visual Regression + UI State Contract | TASK-079 | DONE |
| TASK-081 | M11 | Asset Pipeline + Asset Capability Registry + Routing | TASK-080 | DONE |
| TASK-082 | M11 | Creative Domain + Vendor Integrity + Reference Asset | TASK-081 | DONE |
| TASK-083 | M11 | SkillDistiller + Static Deploy | TASK-082 | DONE |
| TASK-084 | M12 | Version + Compatibility Baseline | TASK-083 | DONE |
| TASK-085 | M12 | Migration 1.0 → 1.1 | TASK-084 | DONE |
| TASK-086 | M12 | Backward Compatibility | TASK-085 | DONE |
| TASK-087 | M12 | Compatibility Conformance | TASK-086 | DONE |
| TASK-088 | M12 | Docs & ADR — Compatibility | TASK-087 | DONE |

## Next action

TASK-088 `DONE` (2350 tests, M12 full: T084-T088 implemented, AC-084..088 PASS). M12 COMPLETE. ALL TASKS 001-088 DONE. Next milestone: M13 (T089-T093, Behavioral/Harness).

## Known implementation gaps (audit 2026-08-22) — CLOSED 2026-08-22

All gaps listed below were **implemented** in the session of 2026-08-22, bringing
each `aios/<package>/` implementation to meet its `docs/detailtask/` acceptance
criteria. Each task's new modules are covered by dedicated tests (see per-task
`tests/` files). Full suite: **1962 passed**.

- **T021** Observability → added `observability/health_api.py` + `dashboard.py` (fail-closed UNKNOWN≠PASS).
- **T023** Memory Coordinator → `filters`/`ranking_policy` on `MemoryQuery`, `provenance`/`checksum`/`scope` on `MemoryCandidate`, `filter.py` + retrieval observability.
- **T024** Context Optimizer → `ExtractiveCompressor`+`LLMCompressor`, priority enum aligned, non-ASCII bug fixed.
- **T025** Model Router → `FallbackResolver` fallback chain + extended `ModelRequirement`/`ModelCandidate`.
- **T028** Parallel Scheduler → `DispatchDecision` enum + `ANY_SUCCESS`/`ALL_COMPLETED` join policies.
- **T029** Harness Kernel → `HarnessRegistry` (AC-029-02) + `HarnessContext`/`HarnessEvent`/`HarnessArtifact`/`HarnessReport`.
- **T030** Execution Verification → `ReplayEngine` + expanded `EvidencePackage`.
- **T031** Test Harness → `test_harness.py` (`FakeRuntime`/`FakeTool`/`GoldenScenario`/`TestHarness`/`run_harness_test`).
- **T032** Evaluation Harness → `evaluators.py` (Evaluator base + Deterministic/Semantic/LLM/Human/Composite + trajectory eval).
- **T033** Benchmark → `GateEvaluator` (PASS/WARNING/FAIL/INCONCLUSIVE) + named primitives.
- **T034** Doctor + Readiness → `readiness.py` (13 domain doctors + `ReadinessEngine` fail-closed).
- **T035** Identity + RBAC → `abac.py` + `delegation.py` (ABAC engine, delegation w/ attenuation).
- **T036** Multi-Tenancy → `Organization`/`Project`/`Workspace`/`TenantContext` + `resolve_scope`/`assert_same_tenant`/`filter_by_tenant`.
- **T041** HA + Audit + Recovery → `health.py`/`lease.py`/`recovery.py`/`audit.py` (hash-chained audit, single-active lease).
- **T042** Enterprise Operations → `metrics.py`/`health.py` + tenant-scoped operations.
- **T043** Public SDK → error model + `SDKVersion` compat + `MockAIOSClient` + `discovery.py`.
- **T044** Plugin Runtime → `manifest.py`/`resolver.py` + validate-before-load/rollback/snapshots.
- **T045** Extension Contracts → `ExtensionContext` + `compatibility.py`/`evidence.py` + boundary check.
- **T046** Ecosystem Registry → `TrustState` + search/resolve_version/is_compatible/set_trust/checksum.
- **T047** Developer Kit → `manifest.py`/`packaging.py`/`cli.py` (`create`/`validate`/`test`/`simulate`/`package`/`inspect`).
- **T048** Ecosystem Hub → search/is_compatible/install via PluginRuntime + checksum/provenance.
- **T049** Certification → `pipeline.py` + profiles/checks/revocation reasons/expiry.
- **T050** Autonomous Goal Engine → `state_machine.py`/`policy.py` + objectives/progress/policy boundary/evidence.

## M10 implementation (2026-08-22)

M10 (Architecture 1.0) froze the 1.0 baseline and added production hardening,
safety, security, reliability and certification controls. New packages:
`aios/contracts` (T064), `aios/durable` (T066), `aios/autonomy_safety` (T067),
`aios/kill_switch` (T068), `aios/reliability` (T069), `aios/cost_meter` (T075);
extended: `aios/governance/architecture` (T063 ADR + baseline), `aios/runtime`
(T065 hardening), `aios/security` (T070), `aios/devkit`+`aios/cli` (T071),
`aios/dashboard` (T072), `aios/certification` (T073 release certifier),
`aios/upgrade` (T074 migration engine), `aios/model_router` (T075 routing).
Full suite: **2272 passed** (was 1962; +310 M10 tests). All 13 M10 tasks PASS
the unified gate (lifecycle artifacts + architecture guard + full CI suite).

### Minor governance-artifact inconsistencies (still open, non-blocking)
- Task-folder `implementation/` dirs are empty for T015, T016, T029, T041, T044, T045, T049, T050 (real code lives in `aios/<package>/`).
- Regression artifact casing inconsistent: `REGRESSION.md` (uppercase) for T011/012/013/014/016/017 vs canonical `regression.md` (lowercase) elsewhere.
