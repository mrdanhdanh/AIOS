# TASK-013 — Worker Plane

## Objective
Xây Worker Plane làm lớp thực thi nghiệp vụ phía trên Orchestrator, cung cấp bốn worker (General, Coder, Doctor, System Doctor) tuân thủ cùng contract, lifecycle, capability access, result/evidence. Worker nhận nhiệm vụ đã orchestration quyết định, sử dụng Capability được cấp và trả về Result + Evidence, không bypass Runtime/Capability/Permission/Policy.

## Scope
- **Worker Contract** (`aios/worker/contract.py`): `WorkerContract` (worker_id, worker_type, version, capabilities, input_schema, output_schema, lifecycle, execution_context, policy_context, evidence_contract), `WorkerRequest` (task_id, goal_id, objective, constraints/allowed_capabilities, context, policy_context), `WorkerContext` (run_id, task_id, worker_id, capability_scope, permissions), `WorkerResult` (status SUCCEEDED/FAILED/BLOCKED/CANCELLED/PARTIAL, output, artifacts, evidence, metrics, execution), `WorkerEvidence` + provenance chain Evidence→Run→Artifact→Task→Requirement, `WorkerError`.
- **Worker Lifecycle** (`aios/worker/lifecycle.py`): `WorkerStatus` REGISTERED→READY→ASSIGNED→RUNNING→COMPLETING→COMPLETED, failure RUNNING→FAILED→RECOVERING→READY/FAILED, terminal COMPLETED/FAILED/CANCELLED, `WorkerHealth` REGISTERED/READY/BUSY/DEGRADED/UNAVAILABLE, `WorkerLifecycle` state machine với valid transitions, thread-safe RLock, fail-closed, không trộn với Task lifecycle.
- **Worker Registry** (`aios/worker/registry.py`): `WorkerRegistry` register/get/list/remove, health tracking, thread-safe, duplicate reject, unknown reject.
- **Worker Router** (`aios/worker/router.py`): `WorkerRouter` route task → worker dựa trên task_type/required_capabilities/worker health/policy/availability, không dựa chỉ tên, fallback chỉ khi policy cho phép, deterministic.
- **Worker Execution** (`aios/worker/execution.py`): `BaseWorker` abstract, capability-only access (chỉ qua CapabilityRegistry, không import Tool/Runtime/Provider/filesystem/subprocess), permission boundary (không tự cấp permission, phải qua Policy), execution_context isolation, structured result, evidence creation, failure propagation.
- **Concrete Workers** (`aios/worker/workers.py`): `GeneralWorker` (research/summarize/transform/inspect/coordinate), `CoderWorker` (inspect/edit/run tests/analyze/refactor, không subprocess/open/requests/docker trực tiếp), `DoctorWorker` (diagnose task failure, inspect logs/artifacts, recommend recovery, không tự remediation), `SystemDoctorWorker` (runtime/service/dependency health, architecture violations, readiness, chỉ đề xuất remediation).
- **Architecture Guard** (`aios/governance/architecture/guard.py`): thêm layer `worker` vào `LAYER_ORDER` và `LAYER_KEYWORDS`, `ALLOWED_IMPORT_LAYERS` cho worker (chỉ capability/unknown), mở rộng `AGENT_FORBIDDEN` cho worker (subprocess/os/provider/filesystem).
- **Out of scope**: Tool + Capability Router chi tiết (TASK-014), Plugin/Skill Execution (TASK-015), Architecture Hardening toàn diện (TASK-016), API/UI (M3).

## Deliverables
- `aios/worker/__init__.py` — package doc + re-exports.
- `aios/worker/contract.py` — WorkerContract, WorkerRequest, WorkerContext, WorkerResult, WorkerEvidence, WorkerError, WorkerType, WorkerResultStatus.
- `aios/worker/lifecycle.py` — WorkerStatus, WorkerHealth, WorkerLifecycle, WorkerLifecycleError.
- `aios/worker/registry.py` — WorkerRegistry, WorkerRegistryError.
- `aios/worker/router.py` — WorkerRouter, WorkerRouterError, RoutingDecision.
- `aios/worker/execution.py` — BaseWorker, WorkerExecutionError, CapabilityAccessError, PermissionBoundaryError.
- `aios/worker/workers.py` — GeneralWorker, CoderWorker, DoctorWorker, SystemDoctorWorker.
- `aios/governance/architecture/guard.py` — updated for worker layer.
- Tests: `aios/worker/tests/test_contract.py`, `test_lifecycle.py`, `test_registry.py`, `test_router.py`, `test_execution.py`, `test_workers.py`, `test_architecture.py`, `test_integration.py`.
- Governance artifacts: `aios/progress/tasks/TASK-013/{spec,critique-1,critique-2,tasks,review,test,evaluation,REGRESSION}.md`.

## Acceptance Criteria
1. **AC-013-01 — Worker Contract**: bốn worker cùng tuân thủ một contract chung (worker_id, worker_type, version, capabilities, input_schema, output_schema, lifecycle, execution_context, policy_context, evidence_contract).
2. **AC-013-02 — Capability-only access**: Worker không gọi Tool trực tiếp (chỉ qua Capability API).
3. **AC-013-03 — Runtime boundary**: Worker không bypass Runtime (không import runtime internals).
4. **AC-013-04 — Permission boundary**: Worker không tự cấp permission (phải qua Policy/Permission Request → ALLOW/DENY).
5. **AC-013-05 — Lifecycle**: Worker lifecycle được state machine kiểm soát (REGISTERED→READY→ASSIGNED→RUNNING→COMPLETING→COMPLETED, failure path, terminal).
6. **AC-013-06 — Result**: mọi execution đều trả structured result (status, output, artifacts, evidence, metrics, execution).
7. **AC-013-07 — Evidence**: kết quả quan trọng có evidence/provenance (Evidence→Run→Artifact→Task→Requirement, UNKNOWN không nâng thành PASS).
8. **AC-013-08 — Routing**: task được route đến worker phù hợp dựa trên contract/capability (không chỉ tên).
9. **AC-013-09 — Failure**: Worker failure được trả về Orchestrator/Failure Recovery, không tự tạo control plane.
10. **AC-013-10 — Architecture**: AST/import architecture tests chứng minh không có Worker→Tool, Worker→subprocess, Worker→Provider, Worker→filesystem adapter (guard PASS).
11. **AC-013-11 — Regression**: `python -m pytest aios -q` xanh, M1 + TASK-010 + TASK-012 PASS (690+ tests).

## Dependencies
- TASK-010 Decision Pipeline (DONE), TASK-012 Operational Orchestration (DONE), M1 Runtime (TASK-003..011 DONE) — CapabilityRegistry, PolicyEngine, PermissionBroker, EvidenceStore, ExecutionPlan.

## Governance references
- Rule 3 Architecture Guard (Agent→Orchestrator→Worker→Runtime→Capability→Tool, ARCH-001..004), Rule 4 Deterministic-first, Rule 5 Evidence (provenance chain), Rule 7 Regression.
