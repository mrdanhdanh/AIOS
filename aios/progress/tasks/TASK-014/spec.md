# TASK-014 — Tool + Capability Layer

## Objective
Xây dựng lớp Tool + Capability làm cầu nối chính thức giữa Worker Plane và các công cụ thực thi bên dưới, chuẩn hóa Tool bằng contract, cho phép Tool tự khai báo capability, discovery động Capability→Tool[], router chọn Tool theo health/priority/policy, enforce Policy/Permission pre-check trước execution, và đảm bảo Worker không bypass Capability để gọi Tool trực tiếp. Hệ thống hoạt động offline với mock/local Tool.

## Scope
- **Tool Contract** (`aios/tool/contracts.py`): Tool metadata (id/name/version/type/description/capabilities/permissions/resources/health/priority/enabled), ToolType (python/docker/rest/mcp/shell/git), ToolHealth (UNKNOWN/HEALTHY/DEGRADED/UNHEALTHY/DISABLED), ToolResult, CapabilityRequest/Resolution, version/compatibility via `aios.core.contracts` + `aios.core.version`.
- **Tool Registry** (`aios/tool/registry.py`): register/unregister, lookup by id/capability, enable/disable, health/priority metadata, version/compatibility check, thread-safe RLock, dynamic discovery Capability→Tool[].
- **Capability Registry** (existing `aios/capability/capability.py`): giữ nguyên, mở rộng health để tương thích 5-state, không hard-code Agent→Tool.
- **Capability Router** (`aios/runtime/capability_router.py`): resolve CapabilityRequest → CapabilityResolution, filter health (HEALTHY/DEGRADED eligible, UNHEALTHY/DISABLED/UNKNOWN reject), priority selection, Policy pre-check (ALLOW/DENY/ASK), fail-closed UNRESOLVED, evidence metadata.
- **Tool Adapters** (`aios/tool/adapters.py`): 6 adapters Python/Docker/REST/MCP/Shell/Git, mỗi adapter khai báo capabilities, offline mock, không bypass Policy, chuẩn hóa ToolResult.
- **Runtime Wiring** (`aios/runtime/kernel.py`): wire ToolRegistry + CapabilityRouter vào Container, health snapshot.
- **Out of scope**: Sandbox Pool đầy đủ (TASK-015), Plugin/Skill lifecycle (TASK-015), Worker Plane chi tiết (TASK-013), multi-tenant (M7).

## Deliverables
- `aios/tool/__init__.py` — re-exports.
- `aios/tool/contracts.py` — ToolContract, ToolHealth, ToolType, ToolResult, CapabilityRequest, CapabilityResolution, ResolutionStatus, ResolutionReason, ToolError.
- `aios/tool/registry.py` — ToolRegistry.
- `aios/tool/adapters.py` — PythonTool, DockerTool, RestTool, McpTool, ShellTool, GitTool + BaseToolAdapter.
- `aios/runtime/capability_router.py` — CapabilityRouter.
- `aios/runtime/kernel.py` — updated wiring.
- `aios/capability/capability.py` — health 5-state compat (backward compat healthy/unhealthy).
- Tests: `aios/tool/tests/test_contracts.py`, `test_registry.py`, `test_adapters.py`, `test_router.py`, `test_policy_integration.py`, `test_architecture.py` + `aios/runtime/tests/test_capability_router.py`.
- Governance artifacts: `aios/progress/tasks/TASK-014/{spec,critique-1,critique-2,tasks,review,test,evaluation,REGRESSION}.md`.

## Acceptance Criteria
1. **AC-014-01 — Tool Contract**: mọi Tool đăng ký phải conform Tool Contract và có metadata/version hợp lệ.
2. **AC-014-02 — Capability Declaration**: Tool có thể khai báo một hoặc nhiều Capability.
3. **AC-014-03 — Dynamic Discovery**: Registry có thể xây mapping Capability→Tool[] mà không cần hard-code Agent→Tool.
4. **AC-014-04 — Multi-Tool Capability**: một Capability phải map tới nhiều Tool implementation.
5. **AC-014-05 — Health-aware Routing**: Router không chọn Tool UNHEALTHY hoặc DISABLED (UNKNOWN cũng reject).
6. **AC-014-06 — Priority-aware Routing**: khi nhiều Tool đều eligible, Router sử dụng priority để lựa chọn.
7. **AC-014-07 — Policy-aware Routing**: Tool không được execution nếu Policy/Permission không cho phép (DENY/ASK).
8. **AC-014-08 — Fail-Closed**: không resolve khi capability không tồn tại, Tool không hợp lệ, health không đủ, policy deny, permission deny → UNRESOLVED.
9. **AC-014-09 — Worker Isolation**: Worker/Agent không import hoặc invoke Tool implementation trực tiếp (ARCH-001..004).
10. **AC-014-10 — Offline**: Router + Registry + adapters có thể test hoàn toàn bằng mock/local Tool, không cần Internet.
11. **AC-014-11 — Evidence**: Tool resolution và execution phải tạo metadata/evidence reference đủ để truy vết.
12. **AC-014-12 — Regression**: toàn bộ regression của M0/M1 + TASK-010/012 phải PASS trước khi DONE.

## Dependencies
- TASK-003 Kernel Foundations (DONE), TASK-004/005 Runtime Services (DONE), TASK-009 Capability Foundation (DONE), TASK-010 Decision Pipeline (DONE), TASK-012 Operational Orchestration (DONE) — Policy/Permission, CapabilityRegistry, RuntimeKernel.

## Governance references
- Rule 3 Architecture Guard (Agent→Orchestrator→Runtime→Capability→Tool, Worker không bypass Capability), Rule 4 Deterministic-first, Rule 5 Evidence, Rule 7 Regression.
