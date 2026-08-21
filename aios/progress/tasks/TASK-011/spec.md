# TASK-011 — M1 Remediation / Architecture Hardening

## Objective
Đóng M1 bằng remediation hardening: rà soát toàn bộ contracts, dependency graph và runtime wiring của M1 (TASK-002..009), siết chặt architecture invariants (Agent→Tool, Workflow→Engine, Policy→Execution), vá những gap phát hiện qua critique/integration/architecture/policy/dependency tests, và cung cấp architecture test suite + regression evidence để M1 gate chuyển PASS trước khi mở M2. Không thêm feature mới ngoài patch set và tests cần thiết.

## Scope
- **Contract hardening** (`aios/core/contracts.py`, `aios/runtime/workflow/contracts.py`, `aios/capability/contracts.py`, `aios/core/metadata.py`, `aios/core/version.py`): mỗi contract có version/semver, schema rõ, không leak implementation, có compatibility check và test.
- **Dependency hardening** (`aios/governance/architecture/guard.py` + `aios/governance/dependency/graph.py`): kiểm tra layering `Agent → Orchestrator → Runtime → Capability → Tool`, phát hiện circular/upward/skip imports, cấm `Agent → Tool` trực tiếp, cấm `Workflow Definition → Engine` (langgraph/jinja2).
- **Policy hardening** (`aios/runtime/policy.py` + `permission.py` + `execution.py`): đảm bảo luồng `Request → Requirements → PolicyService → ALLOW/DENY → Execution` không thể bypass; tool/executor không vòng qua policy.
- **Runtime wiring** (`aios/runtime/kernel.py` + `aios/core/container.py`): verify DI compose toàn bộ M1 services (EventBus, ContextStore, AuditTrail, ArtifactStore, PermissionBroker, PolicyEngine, Scheduler, StateStore, ResourcePool, MemoryStore, KnowledgeIndex, CapabilityRegistry, PromptRegistry, SystemCatalog, KnowledgeGraph, Executor) với Singleton/Scoped/Transient, lifecycle, mock injection.
- **Architecture invariants** (4 ARCH rules + AC-011-02..05): `ARCH-001` no subprocess/os in agent, `ARCH-002` no provider in agent, `ARCH-003` no filesystem in agent, `ARCH-004` layering.
- **Regression** (closure TASK-002..009): chạy lại toàn bộ suite, evidence per gate.
- **Out of scope**: Decision Pipeline/Planner LLM/Goal Manager/Worker Plane/Tool ecosystem/Skill execution/Desktop UI/multi-agent orchestration (để M2).

## Deliverables
- `aios/governance/architecture/guard.py` — patched: `LAYER_KEYWORDS` mở rộng (`core`,`governance`,`harness`,`kernel`,`progress`), `ALLOWED_IMPORT_LAYERS` siết (`agent: ["orchestrator","unknown"]`, `capability: ["unknown"]`), giữ backward compat.
- `aios/governance/architecture/tests/test_m1_hardening.py` — ≥15 tests covering AC-011-02..05 (invariants, policy pre-check, workflow isolation, agent boundary) + CLI/workflow/compiler isolation + regression markers.
- `aios/runtime/kernel.py` — health() bao phủ tất cả singletons (capabilities/prompts/catalog/graph + TASK-004/005/007).
- Governance artifacts: `aios/progress/tasks/TASK-011/{spec,critique-1,critique-2,tasks,review,test,evaluation,REGRESSION}.md` + `aios/progress/{PLAN,LOG,STATS}.md` updates.
- Evidence: `python -m pytest aios -q` ≥514 PASS, offline (no LLM), fail-closed.

## Acceptance Criteria
1. **AC-011-01 — Full M1 Regression**: toàn bộ suite của closure M1 PASS (`python -m pytest aios -q` ≥514).
2. **AC-011-02 — Architecture**: không tồn tại violation của 4 invariants (ARCH-001..004) — guard scan PASS.
3. **AC-011-03 — Policy**: Execution không bypass PolicyService — pre-check `DENY` thì `execution_count==0`, evidence recorded.
4. **AC-011-04 — Agent Boundary**: không có Worker/Agent import trực tiếp Tool/provider/filesystem/subprocess — architecture tests phát hiện.
5. **AC-011-05 — Workflow Boundary**: WorkflowDefinition không import/phụ thuộc trực tiếp execution engine (langgraph/jinja2) — compiler isolation.
6. **AC-011-06 — Contract**: mọi contract có version/schema/compatibility check PASS.
7. **AC-011-07 — Runtime Composition**: RuntimeKernel compose & resolve mọi M1 services qua DI (Container), health() đầy đủ.
8. **AC-011-08 — Offline**: core suite chạy không cần external LLM (`llm_calls==0`).
9. **AC-011-09 — Evidence**: mỗi gate result có evidence/provenance (events/artifacts).
10. **AC-011-10 — Fail Closed**: architecture/policy/regression failure → `BLOCKED`, không silent PASS.

## Dependencies
- TASK-002..009 (DONE) — đặc biệt TASK-005 (RuntimeKernel), TASK-009 (Capability), TASK-008 (Workflow+Compiler+Simulation). TASK-011 là M1 closing gate, phải PASS trước TASK-010 (M2).

## Governance references
- Rule 1..7 via `aios/governance/*`. Deterministic-first: guard/pipeline thuần Python AST, không LLM. Evidence via `AuditTrail`/`EventBus`/artifacts.
