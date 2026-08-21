# TASK-015 — Plugin / Skill Execution

## Objective
Hoàn thiện lớp Plugin/Skill Execution của AIOS trong M2, biến Skill thành component có lifecycle đầy đủ, dependency resolution, trạng thái persistent và khả năng chạy trong Sandbox Pool. Skill là extension không thuộc Core, không bypass Runtime/Capability/Permission/Policy, lifecycle quản lý deterministic, dependency resolve trước enable, install/upgrade/remove không làm hỏng certified state, rollback khôi phục version đã xác nhận, sandbox tái sử dụng nhưng reset state giữa các execution, offline-first và persist qua restart.

## Scope
- **Skill Contract** (`aios/skill/contracts.py`): Skill metadata/manifest (id, name, version, description, author, dependencies, required_capabilities, permissions, resources, runtime, entrypoint, checksum, status), SkillStatus, SkillDependency, SkillPersistentState, validation via `aios.core.version.SemVer` + `aios.core.contracts`, checksum/integrity, fail-closed UNKNOWN.
- **Skill Registry** (`aios/skill/registry.py`): register/get/list/remove, status tracking, thread-safe RLock, duplicate/unknown reject, capability declaration index.
- **Dependency Resolver** (`aios/skill/resolver.py`): resolve direct + transitive dependencies, version constraint (>=, ==, ~=, <, >), conflict detection, cycle detection (DFS), topological order, fail-closed on cycle/conflict/missing.
- **Skill Manager** (`aios/skill/manager.py`): lifecycle state machine (RESOLVE→VALIDATE→INSTALL→ENABLE→READY→DISABLE→UNLOAD→RELOAD→UPGRADE→ROLLBACK→REMOVE), validate manifest schema/checksum/capability/permission/resource/entrypoint/policy, install (validate→install target→register→persist), enable (validate→resolve→policy→permission→prepare runtime→register capabilities→ENABLED), disable (drain→unregister→DISABLED), unload/reload (idempotent, health check), upgrade (backup certified→validate new→install→health check→certify), rollback (restore version/manifest/dependencies/runtime/capabilities/config/artifacts), remove (policy + dependency check, no orphan registry), persistent state, evidence/audit.
- **Sandbox Pool** (`aios/skill/sandbox.py`): SandboxContract, SandboxStatus (CREATED→INITIALIZING→READY→ACQUIRED→RUNNING→RESETTING→READY, FAILED→DESTROY), Sandbox, SandboxPool (acquire/release, warm-start, health check, reset state, idle eviction, resource limits, timeout, isolation boundary), reset clears filesystem/process/env/artifacts/network state, unhealthy never returns to READY.
- **Integration** (`aios/skill/manager.py` + `aios/runtime/kernel.py`): CapabilityRegistry/Router integration (skill declares capabilities, router selects tool), PolicyService/PermissionService pre-check (ALLOW/DENY/ASK, BLOCKED on deny), StateStore/ArtifactStore/EventBus/AuditTrail integration, evidence provenance Skill→Version→Transition→Run→Artifact→Result.
- **Runtime Wiring** (`aios/runtime/kernel.py`): wire SkillRegistry + SkillManager + SandboxPool into Container, health snapshot.
- **Architecture Guard** (`aios/governance/architecture/guard.py`): extend LAYER_ORDER/LAYER_KEYWORDS/ALLOWED_IMPORT_LAYERS for skill layer, forbid skill bypass (subprocess/os/provider/filesystem/runtime internals).
- **Out of scope**: UI/API (M3), multi-tenant (M7), full container isolation (M6 harness), LLM-dependent lifecycle (offline-first).

## Deliverables
- `aios/skill/__init__.py` — re-exports.
- `aios/skill/contracts.py` — SkillContract, SkillDependency, SkillStatus, SkillPersistentState, SkillTransition, validation, checksum, version.
- `aios/skill/registry.py` — SkillRegistry.
- `aios/skill/resolver.py` — SkillDependencyResolver, ResolverError, DependencyGraph.
- `aios/skill/manager.py` — SkillManager, SkillLifecycle, lifecycle transitions, install/enable/disable/unload/reload/upgrade/rollback/remove, persistence, evidence.
- `aios/skill/sandbox.py` — Sandbox, SandboxPool, SandboxStatus, SandboxError, lifecycle, acquire/release/reset/health/eviction.
- `aios/runtime/kernel.py` — updated wiring for skill services.
- `aios/governance/architecture/guard.py` — updated for skill layer.
- Tests: `aios/skill/tests/test_contracts.py`, `test_registry.py`, `test_resolver.py`, `test_manager.py`, `test_sandbox.py`, `test_integration.py`, `test_architecture.py`, `test_persistence.py`, `test_rollback.py`.
- Governance artifacts: `aios/progress/tasks/TASK-015/{spec,critique-1,critique-2,tasks,review,test,evaluation,regression}.md`.

## Acceptance Criteria
1. **AC-015-01 — Lifecycle**: mọi transition hợp lệ thực hiện deterministic, transition không hợp lệ bị reject.
2. **AC-015-02 — Dependency**: dependency resolve trước Enable, conflict/cycle → FAIL.
3. **AC-015-03 — Persistence**: state survive restart và phản ánh đúng trước restart.
4. **AC-015-04 — Isolation**: plugin không import/truy cập trực tiếp Core/Runtime implementation (architecture test FAIL nếu vi phạm).
5. **AC-015-05 — Capability Boundary**: skill chỉ dùng capability contract, không hard-code Tool implementation.
6. **AC-015-06 — Policy Boundary**: skill không execution khi Policy/Permission deny (BLOCKED).
7. **AC-015-07 — Sandbox**: sandbox acquire trước execution, release/reset sau, unhealthy không tái sử dụng.
8. **AC-015-08 — Isolation Between Runs**: execution A không để lại state ảnh hưởng execution B.
9. **AC-015-09 — Upgrade Safety**: upgrade failure không làm mất certified version hiện tại.
10. **AC-015-10 — Rollback**: rollback failure của version mới phải phục hồi certified version trước đó.
11. **AC-015-11 — Offline-first**: lifecycle management cơ bản chạy không cần LLM/network.
12. **AC-015-12 — Evidence**: transition quan trọng có state/evidence/audit provenance Skill→Version→Transition→Run→Artifact→Result.
13. **AC-015-13 — Regression**: toàn bộ test của dependency closure PASS trước khi DONE.

## Dependencies
- TASK-014 Tool + Capability Layer (DONE) — CapabilityRegistry/Router, ToolRegistry, Policy/Permission.
- TASK-013 Worker Plane (DONE), TASK-010 Decision Pipeline (DONE), TASK-012 Operational Orchestration (DONE) — Runtime services.
- M1 Runtime (TASK-003..011 DONE) — StateStore, ArtifactStore, EventBus, AuditTrail, ResourcePool.

## Governance references
- Rule 3 Architecture Guard (Agent→Orchestrator→Worker→Runtime→Skill→Capability→Tool, no bypass), Rule 4 Deterministic-first, Rule 5 Evidence (provenance), Rule 7 Regression.
