# AIOS — Master Task Specification

## Runtime-First · Plugin-First · Offline-First · Harness-Verified · Coding-Plane

> **Trạng thái tài liệu (2026-08-25):** ROADMAP + RECORD THỰC TẾ. Tính đến nay **238/238 task DONE** (TASK-001 → TASK-238), **0 task PLANNED**, full suite **3255+ tests xanh**, 0 BLOCKED. Roadmap M0–M26 + M27 (control-plane extension) + M28 (self-evolution) + M29–M35 (Operational Integration & Autonomous Coding OS) CLOSED. Toàn bộ AIOS 2.x hoàn thành. Mỗi task dưới đây mang dòng `> **Trạng thái thực tế:**` ghi nhận module đã build, số test (DONE).
>
> **Nguồn:** nội dung master plan được cung cấp trong file `Plan-AI-Operating-System-—-Runtime-First,-Plugin-First,-Offline-First,-Milestone.txt`.
>
> **Biên soạn:** chuẩn hóa toàn bộ task thành một format thống nhất `Objective → Scope → Deliverables → Acceptance → Dependencies`. Với các task mà nguồn chỉ nêu tên/ý định mà chưa có AC chi tiết, phần mô tả là **structured expansion** để biến roadmap thành task specification; không coi đó là lịch sử implementation.

## 1. Quy tắc chung

1. TASK ID là immutable; không tái sử dụng.
2. Dependency quyết định thứ tự thực thi; milestone quyết định product boundary.
3. Runtime là control substrate; Worker/Agent không bypass Runtime, Capability, Permission hoặc Policy.
4. LLM không được trở thành control plane mặc định; deterministic path đi trước.
5. Evidence phải có provenance; UNKNOWN không được nâng thành PASS.
6. Task chỉ được đóng khi có spec, critique ×2, breakdown, review, implementation, test, evaluation và cập nhật progress/log theo workflow của master plan.
7. Mọi task phải regression các dependency trước đó.
8. **Auto-COMMIT sau DONE (scheduled TASK):** mọi TASK đã lên lịch trong file này (`AIOS_Master_Task_Specification_M0-M26.md`) khi đạt `DONE` (Unified Task Gate `PASS`) phải `COMMIT` source ngay trong cùng phiên — không để working tree bẩn sang task sau; commit message chuẩn `TASK-xxx: <title> — DONE` kèm cập nhật `aios/progress/PLAN.md`, `LOG.md`, `STATS.md` và evidence liên quan.

## 2. Task Folder Standard

```text
aios/progress/tasks/TASK-xxx/
├── spec.md
├── critique-1.md
├── critique-2.md
├── tasks.md
├── review.md
├── implementation/
├── test.md
└── evaluation.md
```

## 3. Definition of Done

```text
PLAN → SPEC → CRITIQUE×2 → BREAKDOWN → REVIEW
→ IMPLEMENT → TEST → EVALUATE → REGRESSION → PROGRESS/LOG → COMMIT
```

> **Quy tắc 8 — Auto-COMMIT:** `COMMIT` là bước bắt buộc và phải thực hiện **ngay** sau khi TASK đã lên lịch trong file này đạt `DONE` (Unified Gate `PASS`). Không được trì hoãn commit sang task sau; `PROGRESS/LOG` (`PLAN.md`/`LOG.md`/`STATS.md`) phải được cập nhật trước khi commit.

---

# M0

## TASK-001 — Task Governance System (Project Governance Foundation)

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/governance/` (task_registry, dependency, lifecycle, evidence, architecture, deterministic, regression, gates, cli); **39 automated tests**; implementation khớp spec, fail-closed PASS (Unified Gate AND 7 rules).

**Mục tiêu**  
Biến 7 Quy tắc chung từ "nguyên tắc trên giấy" thành một hệ thống kiểm soát task có thể tự kiểm chứng (self-verifying **Task Governance System**) trước khi có runtime. Đây là control plane cho toàn bộ AIOS development system; từ TASK-002 trở đi, developer/agent không cần "nhớ" 7 quy tắc — hệ thống tự ép tuân thủ.

**Phạm vi**  
Xây 7 thành phần governance, mỗi thành phần có **automated test** (không chỉ quy ước bằng lời):

- **Task Registry** (Rule 1): registry duy nhất; ID `unique / immutable / never-reused / never-deleted`; gate `create_task()` từ chối ID đã tồn tại. Task sai → `status = DEPRECATED`, không xóa rồi tái sử dụng ID.
- **Dependency Graph** (Rule 2): mỗi task khai báo `dependencies`; task chỉ `READY` khi tất cả dependency `PASS`; phát hiện `cyclic_dependency → BLOCK`.
- **Architecture Guard** (Rule 3): AST/import scanner enforce `Agent → Orchestrator → Runtime → Capability → Tool`. Quy tắc `ARCH-001..004` (vd: Agent không import `subprocess`/provider/filesystem adapter trực tiếp). Vi phạm → `ARCHITECTURE GATE = FAIL → TASK BLOCKED`.
- **Deterministic Control Path** (Rule 4): execution contract `Request → Normalizer → Rule Engine → Workflow Matcher → Capability Resolver → Policy → Execution Plan`; LLM chỉ fallback khi deterministic `INSUFFICIENT` và output phải qua validator.
- **Evidence Store** (Rule 5): mỗi evidence có `evidence_id, task_id, run_id, producer, type, source, created_at, content_hash, parent_artifact, environment, status`; provenance chain `Evidence → Run → Artifact → Task → Requirement`.
- **Task State Machine** (Rule 6): `PLANNED → SPECIFIED → CRITIQUED_1 → CRITIQUED_2 → BROKEN_DOWN → REVIEWED → IMPLEMENTING → TESTING → EVALUATING → REGRESSION → READY_TO_CLOSE → DONE`; mỗi transition có điều kiện artifact bắt buộc. Thiếu một → `DONE = REJECTED`.
- **Regression Gate** (Rule 7): mỗi task chạy test của **dependency closure** trước khi PASS; failure trong closure → `TASK BLOCKED`.

**Unified Task Gate** hội tụ 7 quy tắc: `Registry ∧ Dependency ∧ Architecture ∧ Lifecycle ∧ Evidence ∧ Test/Evaluate ∧ Regression → PASS → DONE`, else `BLOCKED`.

Cấu trúc:
```text
aios/
├── core/  runtime/  harness/  governance/
│                              ├── task_registry/
│                              ├── dependency/
│                              ├── lifecycle/
│                              ├── evidence/
│                              ├── gates/
│                              ├── regression/
│                              └── architecture/
aios/progress/
├── PLAN.md  LOG.md  STATS.md  tasks/TASK-xxx/
```

Thứ tự triển khai: **Phase A** — TASK-001 tạo Registry/Schema/State Machine/Dependency Graph/Evidence Schema/Gate Engine/Regression Runner/Architecture Rules. **Phase B** — chứng minh bằng TASK-002 đi trọn `PLAN→SPEC→CRITIQUE×2→BREAKDOWN→REVIEW→IMPLEMENT→TEST→EVALUATE→REGRESSION→DONE`. **Phase C** — TASK-003..

**Deliverables**
- `aios/governance/` package: 7 modules + automated pytest tests cho từng gate.
- `aios/progress/` với `PLAN.md / LOG.md / STATS.md` + task folders (`_TEMPLATE/` và `TASK-001/` thực thi trọn vòng đời).
- `docs/PLAN.md`, `AGENTS.md`, `aios/agents/` (orchestrator / spec-writer / critic / reviewer).
- CLI: `parse_spec.py` (sinh registry từ master spec, validate Rule 1/2) và `gate_check.py` (chạy unified gate).

**Acceptance Criteria**
- Registry: tạo task với ID đã tồn tại → `REJECT` (automated test PASS).
- Dependency: task chạy khi dependency chưa PASS → `BLOCK`; `cyclic_dependency → BLOCK` (test PASS).
- Architecture: agent import `subprocess`/provider trực tiếp → `ARCHITECTURE GATE FAIL` (test PASS).
- Deterministic: rule quyết định được → `LLM call count = 0`; rule không đủ → LLM được gọi và output qua validator (test PASS).
- Evidence: mỗi `PASS` truy được provenance chain đầy đủ (test PASS).
- State Machine: thiếu một artifact bắt buộc → `DONE` bị `REJECT` (test PASS).
- Regression: failure trong dependency closure → task `BLOCKED` (test PASS).
- Một phiên mới đọc repo (`docs/PLAN.md` + `AGENTS.md` + `aios/progress/README.md`) tiếp tục được mà không cần chat memory.

**Dependency / Gate**
- Milestone M0, không dependency. Là nền tảng cho mọi task sau (TASK-002 trở đi bắt buộc chạy qua hệ thống này).

---

# M1

## TASK-002 — Monorepo + aios_core Scaffold

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/core/` (config, logging, metadata, healthcheck, smoke); **43 automated tests**; layout + CI/test bootstrap xanh.

**Mục tiêu**  
Tạo skeleton Python/monorepo ổn định cho Runtime.

**Phạm vi**
- Package layout, config, logging, metadata, healthcheck, test layout.

**Deliverables**
- Repository skeleton + CI/test bootstrap.

**Acceptance Criteria**
- Import/package/test bootstrap chạy sạch; layout phù hợp quy ước M1.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-003 — Kernel Foundations

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/core/` (version, contracts, container, events, planner); **78 automated tests**; DI lifetimes + event bus + contract compat hoạt động.

**Mục tiêu**  
Xây semantic versioning, contracts, DI và event bus.

**Phạm vi**
- Contract version/schema compatibility; DI singleton/scoped/transient; event bus; execution-plan primitives.

**Deliverables**
- Core contracts + container + event primitives.

**Acceptance Criteria**
- Service có thể inject mock; contract compatibility được kiểm tra; event publish/subscribe hoạt động.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-004 — Runtime Services I

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/runtime/` (context, audit, artifact, permission, policy); **45 automated tests**; Policy pre-check trước Execution, artifact có integrity.

**Mục tiêu**  
Xây Context, Event/Audit, Artifact, Permission và Policy services.

**Phạm vi**
- 6 context types; audit; artifact checksum/version; permission scopes; policy pre-check.

**Deliverables**
- Các service độc lập + interfaces + tests.

**Acceptance Criteria**
- Không service nào bypass contract; Policy quyết định trước Execution; artifact có metadata/integrity.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-005 — Runtime Services II

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/runtime/` (execution, scheduler, state, resource, kernel); **34 automated tests**; RuntimeKernel wires 9 services, retry/cancel/timeout + snapshot/resume.

**Mục tiêu**  
Hoàn thiện Execution, Scheduler, State, Resource và RuntimeKernel.

**Phạm vi**
- Retry/cancel/timeout; checkpoint; queue kỹ thuật; resource grant/queue/reject; kernel composition.

**Deliverables**
- RuntimeKernel + service wiring.

**Acceptance Criteria**
- Workflow có thể execute/snapshot/resume; resource và policy được enforce.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-006 — Model Contract + Provider Registry

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/runtime/providers/` (contract, adapters, registry); **27 automated tests**; Mock/OpenAI/Ollama adapters, offline-first selection, provider thay thế qua contract.

**Mục tiêu**  
Chuẩn hóa model/provider mà không khóa AIOS vào một vendor.

**Phạm vi**
- Mock/OpenAI/Ollama adapters; model metadata; capabilities; usage/cost/error.

**Deliverables**
- Provider registry + adapters + deterministic selection primitives.

**Acceptance Criteria**
- Provider có thể thay thế qua contract; mock chạy offline.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-007 — Memory + Knowledge

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/runtime/` (memory, knowledge); **60 automated tests** (27 memory + 33 knowledge); isolation + provenance (content_hash) + deterministic ranking + thread-safe.

**Mục tiêu**  
Xây conversation/session/knowledge/artifact memory và knowledge pipeline.

**Phạm vi**
- Memory lifecycle, retrieval, local docs/PDF/code sources, metadata.

**Deliverables**
- Memory services + index/retrieval pipeline.

**Acceptance Criteria**
- Memory isolation và provenance được giữ; retrieval có nguồn evidence.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-008 — Workflow Definition + Compiler

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/runtime/workflow/` (definition, compiler, langgraph, mock); **44 automated tests** (39 + 5 arch); YAML→compile→simulate không cần LLM, engine-independent.

**Mục tiêu**  
Đưa workflow thành declarative contract độc lập engine.

**Phạm vi**
- YAML definition, compiler interface, LangGraph compiler, Mock compiler, simulation.

**Deliverables**
- Workflow schema + compiler adapters + CLI simulation.

**Acceptance Criteria**
- Cùng workflow có thể compile sang engine khác; simulation không cần LLM.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-009 — Capability Foundation

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/capability/` (capability, prompt, catalog, graph); **94 automated tests**; dynamic discovery, prompt version/render, catalog index, in-memory graph v1, provenance retained.

**Mục tiêu**  
Tạo Capability Registry, Prompt Registry, System Catalog và Knowledge Graph v1.

**Phạm vi**
- Dynamic capability discovery; prompt metadata/version; catalog; graph node/edge metadata.

**Deliverables**
- Registry/catalog/graph APIs.

**Acceptance Criteria**
- Agent chỉ thấy capability; graph v1 chạy in-memory/manual theo amendment của nguồn.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-011 — M1 Remediation / Architecture Hardening

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/governance/architecture/` (m1_hardening + guard); **30+ architecture tests**; M1 gate PASS, invariants cốt lõi (ARCH-001..004, policy pre-check, agent boundary, workflow isolation, offline) enforced.

**Mục tiêu**  
Đóng các gap còn lại của nền Runtime trước khi mở rộng Orchestrator.

**Phạm vi**
- Contract, policy, dependency, wiring, tests và review findings.

**Deliverables**
- Remediation patch set + regression report.

**Acceptance Criteria**
- M1 gate PASS; architecture invariants cốt lõi không vi phạm.

**Dependency / Gate**
- Theo dependency của milestone.

---

# M2

## TASK-010 — Decision Pipeline

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/orchestrator/` (normalizer, rule_engine, workflow_matcher, execution_plan, planner, decision_pipeline); **57 automated tests**; deterministic routing không LLM, planner chỉ fallback khi INSUFFICIENT + NO_MATCH.

**Mục tiêu**  
Triển khai Normalizer → Rule Engine → Workflow Matcher → Planner LLM.

**Phạm vi**
- Deterministic routing trước; planner chỉ fallback khi rule/workflow không đủ.

**Deliverables**
- Pipeline + execution-plan artifact.

**Acceptance Criteria**
- Request deterministic được xử lý không cần LLM; planner output được validate.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-012 — Operational Orchestration

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/orchestrator/` (goal_manager, task_queue, permission_broker, failure_recovery); **89 automated tests**; goal resume/persist, dependency-blocked queue (no cron), permission broker (DENY wins), bounded retry/recovery.

**Mục tiêu**  
Xây Goal Manager, Task Queue, Permission Broker và Failure Recovery.

**Phạm vi**
- Goal dài hạn; logical task queue; permission request/decision; retry/recovery.

**Deliverables**
- Orchestration services + persisted state.

**Acceptance Criteria**
- Goal có thể resume; task queue không bị nhầm với Scheduler kỹ thuật.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-013 — Worker Plane

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/worker/` (contract, lifecycle, registry, router, execution, workers); **161 automated tests**; 4 worker types (General/Coder/Doctor/SystemDoctor), capability-only access, no runtime/orchestrator import, evidence provenance.

**Mục tiêu**  
Tạo General, Coder, Doctor và System Doctor workers.

**Phạm vi**
- Agent contract, lifecycle, capability access, result/evidence.

**Deliverables**
- Worker agents + routing contracts.

**Acceptance Criteria**
- Worker không truy cập Runtime/Tool trực tiếp; chỉ qua Capability + Runtime.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-014 — Tool + Capability Layer

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/tool/` (contracts, registry, adapters, router) + `aios/runtime/capability_router`; **181 automated tests**; 6 tool types (python/docker/rest/mcp/shell/git), dynamic discovery, health-aware + policy-gated routing, fail-closed.

**Mục tiêu**  
Chuẩn hóa Python/Docker/REST/MCP/Shell/Git qua capability.

**Phạm vi**
- Tool contracts, health, capability declaration, router, policy pre-check.

**Deliverables**
- Tool registry + capability router + adapters.

**Acceptance Criteria**
- Một capability có thể map nhiều tool; router chọn tool theo health/priority/policy.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-015 — Plugin / Skill Execution

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/skill/` (contracts, registry, resolver, manager, sandbox, persistence, rollback); **167 automated tests**; full lifecycle (install/enable/disable/upgrade/rollback/remove), dependency resolution, sandbox pool, rollback khôi phục certified state.

**Mục tiêu**  
Hoàn thiện skill lifecycle và sandbox pool.

**Phạm vi**
- Resolve/Validate/Install/Enable/Disable/Unload/Reload/Upgrade/Rollback/Remove; dependency resolution.

**Deliverables**
- Skill manager + sandbox pool + persistent state.

**Acceptance Criteria**
- Plugin không chạm Core; rollback khôi phục certified state.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-016 — Architecture Hardening

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/governance/architecture/` (scanner, graph, rules, gate, report, violations); **112 automated tests**; ARCH-A..H + INV-001..010 enforced via AST, fail-closed CI gate.

**Mục tiêu**  
Enforce invariants và dependency boundaries bằng AST/architecture tests.

**Phạm vi**
- INV-001..010, layer checks, import rules, capability/policy bypass detection.

**Deliverables**
- Architecture test suite + CI gate.

**Acceptance Criteria**
- Vi phạm architecture làm gate FAIL.

**Dependency / Gate**
- Theo dependency của milestone.

---

# M3

## TASK-017 — FastAPI REST + WebSocket

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/api/` (schemas, errors, auth, events, contracts, websocket, app, routers, openapi, versioning); **60 automated tests**; REST + WebSocket, auth boundary, OpenAPI stable, event whitelist.

**Mục tiêu**  
Mở Runtime/Orchestrator qua API ổn định.

**Phạm vi**
- REST resources, WebSocket events, auth boundary, error model.

**Deliverables**
- API service + OpenAPI + integration tests.

**Acceptance Criteria**
- CLI/UI và API dùng cùng contracts; event stream không bypass policy.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-018 — Dashboard SPA

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/dashboard/` (client, health, views, server, mock); **123 automated tests**; 10 views, actions đi qua API boundary, offline mock backend, UNKNOWN≠healthy.

**Mục tiêu**  
Xây operational UI thống nhất.

**Phạm vi**
- Chat, workflow, timeline, tools, memory, artifacts, skills, models, prompts, health.

**Deliverables**
- Dashboard SPA + API client.

**Acceptance Criteria**
- UI phản ánh state thật; action đi qua API/runtime.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-019 — VS Code Extension

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/extension/` (contracts, workspace, api_client, config, mock); **74 automated tests**; 9 commands map to API, pure client không chứa business logic, no Runtime/Tool import.

**Mục tiêu**  
Đưa AIOS vào coding workspace.

**Phạm vi**
- Chat, workflow run, task/progress, artifacts, diagnostics.

**Deliverables**
- Extension + backend integration.

**Acceptance Criteria**
- Extension không chứa business logic riêng; dùng AIOS APIs.

**Dependency / Gate**
- Theo dependency của milestone.

---

# M4

## TASK-020 — Upgrade Pipeline

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/upgrade/` (manifest, compatibility, backup, migration, dryrun, validation, rollback); **43 automated tests**; dry-run deterministic, auto-rollback khôi phục exact state, evidence trong kết quả.

**Mục tiêu**  
Xây upgrade/migration an toàn.

**Phạm vi**
- Resolve → Backup → Migrate → Validate → Rollback; dry-run.

**Deliverables**
- Migration engine + manifests + rollback.

**Acceptance Criteria**
- Migration fail không làm mất certified state; dry-run deterministic.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-021 — Observability + Architecture Health

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/observability/` (metrics, audit, prompt history, profiler, doctor, architecture health); **43 automated tests**; phát hiện contract/layer/dependency/capability/permission violations, fail-closed.

**Mục tiêu**  
Quan sát runtime và kiến trúc.

**Phạm vi**
- Metrics, audit, prompt history, profiler, doctor, architecture health.

**Deliverables**
- Telemetry/evaluation/doctor surfaces.

**Acceptance Criteria**
- Có thể phát hiện contract/layer/dependency/capability/permission violations.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-022 — Orchestrator v2

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/orchestrator/` v2 (supervisor, evaluator, advisor, reporter); **30 automated tests**; execution supervisor + evaluation collector, improvement chỉ đề xuất không bypass policy.

**Mục tiêu**  
Nâng Orchestrator thành control plane có evaluation và improvement.

**Phạm vi**
- Execution Supervisor, Evaluation Collector, Improvement Advisor, Goal reporting.

**Deliverables**
- Orchestrator v2 + reports.

**Acceptance Criteria**
- Orchestrator vẫn không trở thành God Object; improvement chỉ đề xuất, không bypass policy.

**Dependency / Gate**
- Theo dependency của milestone.

---

# M5

## TASK-023 — Memory Coordinator

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/memory_coordinator/`; **19 automated tests**; MemoryQuery (filters/ranking_policy), MemoryCandidate (provenance/checksum/scope), retrieval observability, tích hợp Runtime/Harness.

**Mục tiêu**  
Điều phối 4 loại memory và isolation.

**Phạm vi**
- Triển khai đúng contract và invariant của milestone; tích hợp với Runtime/Harness hiện có, không tạo control plane song song.

**Deliverables**
- Implementation + tests + docs/ADR khi cần.

**Acceptance Criteria**
- AC của task PASS; regression của các milestone trước PASS; không vi phạm invariant.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-024 — Context Optimizer

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/context_optimizer/` (ExtractiveCompressor, LLMCompressor, optimizer); **21 automated tests**; priority enum aligned, non-ASCII bug fixed, tích hợp Runtime/Harness.

**Mục tiêu**  
Tối ưu context theo relevance, budget và lifecycle.

**Phạm vi**
- Triển khai đúng contract và invariant của milestone; tích hợp với Runtime/Harness hiện có, không tạo control plane song song.

**Deliverables**
- Implementation + tests + docs/ADR khi cần.

**Acceptance Criteria**
- AC của task PASS; regression của các milestone trước PASS; không vi phạm invariant.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-025 — Model Router

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/model_router/` (FallbackResolver, ModelRequirement, ModelCandidate); **11 automated tests**; fallback chain, policy/capability/cost/health selection, tích hợp Runtime/Harness.

**Mục tiêu**  
Chọn model theo policy, capability, cost và health.

**Phạm vi**
- Triển khai đúng contract và invariant của milestone; tích hợp với Runtime/Harness hiện có, không tạo control plane song song.

**Deliverables**
- Implementation + tests + docs/ADR khi cần.

**Acceptance Criteria**
- AC của task PASS; regression của các milestone trước PASS; không vi phạm invariant.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-026 — Planning Engine

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/planning_engine/` (contracts/compiler); thuộc 36 tests mới của M5; tạo/validate execution plan đa bước, tích hợp Runtime/Harness.

**Mục tiêu**  
Tạo/validate execution plan đa bước.

**Phạm vi**
- Triển khai đúng contract và invariant của milestone; tích hợp với Runtime/Harness hiện có, không tạo control plane song song.

**Deliverables**
- Implementation + tests + docs/ADR khi cần.

**Acceptance Criteria**
- AC của task PASS; regression của các milestone trước PASS; không vi phạm invariant.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-027 — Execution Graph

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/execution_graph/` (compiler/contracts); **15 automated tests**; biên dịch plan thành DAG acyclic, tích hợp Runtime/Harness.

**Mục tiêu**  
Biên dịch plan thành DAG acyclic.

**Phạm vi**
- Triển khai đúng contract và invariant của milestone; tích hợp với Runtime/Harness hiện có, không tạo control plane song song.

**Deliverables**
- Implementation + tests + docs/ADR khi cần.

**Acceptance Criteria**
- AC của task PASS; regression của các milestone trước PASS; không vi phạm invariant.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-028 — Parallel Scheduler

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/parallel_scheduler/` (contracts, scheduler); **11 automated tests**; DispatchDecision enum + ANY_SUCCESS/ALL_COMPLETED join policies, chạy DAG song song trong resource/policy boundaries.

**Mục tiêu**  
Chạy DAG song song trong resource/policy boundaries.

**Phạm vi**
- Triển khai đúng contract và invariant của milestone; tích hợp với Runtime/Harness hiện có, không tạo control plane song song.

**Deliverables**
- Implementation + tests + docs/ADR khi cần.

**Acceptance Criteria**
- AC của task PASS; regression của các milestone trước PASS; không vi phạm invariant.

**Dependency / Gate**
- Theo dependency của milestone.

---

# M6

## TASK-029 — Harness Kernel + Contract + Registry + Run

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/harness/` (kernel: HarnessRegistry, HarnessContext/Event/Artifact/Report); **11 automated tests**; RunStatus lifecycle CREATED→…→COMPLETED, kernel create/execute/register_step, no Runtime import.

**Mục tiêu**  
Tạo kernel cho harness độc lập với Runtime.

**Phạm vi**
- Triển khai đúng contract và invariant của milestone; tích hợp với Runtime/Harness hiện có, không tạo control plane song song.

**Deliverables**
- Implementation + tests + docs/ADR khi cần.

**Acceptance Criteria**
- AC của task PASS; regression của các milestone trước PASS; không vi phạm invariant.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-030 — Execution Verification + Evidence + Replay

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/harness/` (verification: ReplayEngine, EvidencePackage); **6 automated tests**; fail-closed (no_checks→INCONCLUSIVE), mọi verify tạo EvidencePackage có provenance.

**Mục tiêu**  
Xác minh execution và tạo evidence có thể replay.

**Phạm vi**
- Triển khai đúng contract và invariant của milestone; tích hợp với Runtime/Harness hiện có, không tạo control plane song song.

**Deliverables**
- Implementation + tests + docs/ADR khi cần.

**Acceptance Criteria**
- AC của task PASS; regression của các milestone trước PASS; không vi phạm invariant.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-031 — Test Harness + Scenario + Simulation

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/harness/` (test_harness: FakeRuntime/FakeTool/GoldenScenario/TestHarness/run_harness_test); **5 automated tests**; deterministic scenario + simulation không side-effect.

**Mục tiêu**  
Chạy scenario deterministic và simulation.

**Phạm vi**
- Triển khai đúng contract và invariant của milestone; tích hợp với Runtime/Harness hiện có, không tạo control plane song song.

**Deliverables**
- Implementation + tests + docs/ADR khi cần.

**Acceptance Criteria**
- AC của task PASS; regression của các milestone trước PASS; không vi phạm invariant.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-032 — Evaluation Harness + Metrics

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/harness/` (evaluation: Evaluator base + Deterministic/Semantic/LLM/Human/Composite + trajectory eval); **4 automated tests**; exact match PASS, empty INCONCLUSIVE, custom WARNING.

**Mục tiêu**  
Đánh giá output/trajectory bằng evaluator suite.

**Phạm vi**
- Triển khai đúng contract và invariant của milestone; tích hợp với Runtime/Harness hiện có, không tạo control plane song song.

**Deliverables**
- Implementation + tests + docs/ADR khi cần.

**Acceptance Criteria**
- AC của task PASS; regression của các milestone trước PASS; không vi phạm invariant.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-033 — Benchmark + Regression Gate

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/harness/` (benchmark: GateEvaluator PASS/WARNING/FAIL/INCONCLUSIVE + named primitives); **6 automated tests**; BaselineManager + RegressionDetector + ReleaseGate.

**Mục tiêu**  
So sánh phiên bản theo quality/cost/latency/token/failure/policy.

**Phạm vi**
- Triển khai đúng contract và invariant của milestone; tích hợp với Runtime/Harness hiện có, không tạo control plane song song.

**Deliverables**
- Implementation + tests + docs/ADR khi cần.

**Acceptance Criteria**
- AC của task PASS; regression của các milestone trước PASS; không vi phạm invariant.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-034 — Doctor + Readiness

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/harness/` (doctor: readiness.py 13 domain doctors + ReadinessEngine); **7 automated tests**; readiness fail-closed (một fail → not ready).

**Mục tiêu**  
Chẩn đoán và tính readiness fail-closed.

**Phạm vi**
- Triển khai đúng contract và invariant của milestone; tích hợp với Runtime/Harness hiện có, không tạo control plane song song.

**Deliverables**
- Implementation + tests + docs/ADR khi cần.

**Acceptance Criteria**
- AC của task PASS; regression của các milestone trước PASS; không vi phạm invariant.

**Dependency / Gate**
- Theo dependency của milestone.

---

# M7

## TASK-035 — Identity + Principal + RBAC/ABAC

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/identity/` (Principal, Role, Policy, IdentityService, RBAC/ABAC); **12 automated tests**; fail-closed (thiếu info → DENY).

**Mục tiêu**  
Thiết lập identity và authorization.

**Phạm vi**
- Triển khai đúng contract và invariant của milestone; tích hợp với Runtime/Harness hiện có, không tạo control plane song song.

**Deliverables**
- Implementation + tests + docs/ADR khi cần.

**Acceptance Criteria**
- AC của task PASS; regression của các milestone trước PASS; không vi phạm invariant.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-036 — Multi-Tenancy + Tenant Boundary

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/tenancy/` (Tenant, TenantManager, boundary); **10 automated tests**; cross-tenant isolation, fail-closed trên missing tenant.

**Mục tiêu**  
Cô lập tenant xuyên runtime/data.

**Phạm vi**
- Triển khai đúng contract và invariant của milestone; tích hợp với Runtime/Harness hiện có, không tạo control plane song song.

**Deliverables**
- Implementation + tests + docs/ADR khi cần.

**Acceptance Criteria**
- AC của task PASS; regression của các milestone trước PASS; không vi phạm invariant.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-037 — Distributed Runtime + Runtime Node

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/distributed/` (RuntimeNode, NodeManager); **5 automated tests**; health model, tenant/policy-aware selection, no Orchestrator→internal.

**Mục tiêu**  
Đưa Runtime lên nhiều node.

**Phạm vi**
- Triển khai đúng contract và invariant của milestone; tích hợp với Runtime/Harness hiện có, không tạo control plane song song.

**Deliverables**
- Implementation + tests + docs/ADR khi cần.

**Acceptance Criteria**
- AC của task PASS; regression của các milestone trước PASS; không vi phạm invariant.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-038 — Distributed Scheduler + Lease + Failover

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/distributed_scheduler/` (DistributedScheduler, Lease); **5 automated tests**; lease lifecycle HELD→RELEASED/EXPIRED, duplicate acquire rejected (INV-026).

**Mục tiêu**  
Điều phối execution phân tán an toàn.

**Phạm vi**
- Triển khai đúng contract và invariant của milestone; tích hợp với Runtime/Harness hiện có, không tạo control plane song song.

**Deliverables**
- Implementation + tests + docs/ADR khi cần.

**Acceptance Criteria**
- AC của task PASS; regression của các milestone trước PASS; không vi phạm invariant.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-039 — Quota + Cost + Resource Governance

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/quota/` (Quota, Cost, Budget); **5 automated tests**; exceeded→DENY, UNKNOWN→DENY fail-closed.

**Mục tiêu**  
Giới hạn tài nguyên và chi phí theo tenant.

**Phạm vi**
- Triển khai đúng contract và invariant của milestone; tích hợp với Runtime/Harness hiện có, không tạo control plane song song.

**Deliverables**
- Implementation + tests + docs/ADR khi cần.

**Acceptance Criteria**
- AC của task PASS; regression của các milestone trước PASS; không vi phạm invariant.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-040 — Credential + Network + Sandbox Isolation

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/security/` (Credential, NetworkPolicy, SandboxConfig, IsolationManager); **27 automated tests**; default-deny, invalid credential→DENY, no Agent bypass.

**Mục tiêu**  
Cô lập secrets/network/sandbox.

**Phạm vi**
- Triển khai đúng contract và invariant của milestone; tích hợp với Runtime/Harness hiện có, không tạo control plane song song.

**Deliverables**
- Implementation + tests + docs/ADR khi cần.

**Acceptance Criteria**
- AC của task PASS; regression của các milestone trước PASS; không vi phạm invariant.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-041 — HA + Audit + Recovery

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/ha/` (HAConfig, HAManager, lease, recovery); **10 automated tests**; failover, single-active lease, hash-chained audit.

**Mục tiêu**  
Đảm bảo high availability, audit và recovery.

**Phạm vi**
- Triển khai đúng contract và invariant của milestone; tích hợp với Runtime/Harness hiện có, không tạo control plane song song.

**Deliverables**
- Implementation + tests + docs/ADR khi cần.

**Acceptance Criteria**
- AC của task PASS; regression của các milestone trước PASS; không vi phạm invariant.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-042 — Enterprise Operations + Dashboard

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/operations/` (Operation, OperationsManager, health, metrics); **9 automated tests**; tenant-scoped, no parallel control plane.

**Mục tiêu**  
Cung cấp vận hành enterprise.

**Phạm vi**
- Triển khai đúng contract và invariant của milestone; tích hợp với Runtime/Harness hiện có, không tạo control plane song song.

**Deliverables**
- Implementation + tests + docs/ADR khi cần.

**Acceptance Criteria**
- AC của task PASS; regression của các milestone trước PASS; không vi phạm invariant.

**Dependency / Gate**
- Theo dependency của milestone.

---

# M8

## TASK-043 — Public AIOS SDK

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/sdk/` (error model, SDKVersion compat, MockAIOSClient, discovery); **9 automated tests**; stable public API.

**Mục tiêu**  
Mở API ổn định cho developer.

**Phạm vi**
- Triển khai đúng contract và invariant của milestone; tích hợp với Runtime/Harness hiện có, không tạo control plane song song.

**Deliverables**
- Implementation + tests + docs/ADR khi cần.

**Acceptance Criteria**
- AC của task PASS; regression của các milestone trước PASS; không vi phạm invariant.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-044 — Plugin Runtime

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/plugin_runtime/` (manifest, resolver, validate-before-load/rollback/snapshots); **9 automated tests**; plugin lifecycle isolation.

**Mục tiêu**  
Runtime lifecycle cho plugin.

**Phạm vi**
- Triển khai đúng contract và invariant của milestone; tích hợp với Runtime/Harness hiện có, không tạo control plane song song.

**Deliverables**
- Implementation + tests + docs/ADR khi cần.

**Acceptance Criteria**
- AC của task PASS; regression của các milestone trước PASS; không vi phạm invariant.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-045 — Extension Contracts

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/extension_contracts/` (ExtensionContext, compatibility, evidence, boundary); **10 automated tests**; bảo vệ Core qua public contracts.

**Mục tiêu**  
Bảo vệ Core bằng public extension contracts.

**Phạm vi**
- Triển khai đúng contract và invariant của milestone; tích hợp với Runtime/Harness hiện có, không tạo control plane song song.

**Deliverables**
- Implementation + tests + docs/ADR khi cần.

**Acceptance Criteria**
- AC của task PASS; regression của các milestone trước PASS; không vi phạm invariant.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-046 — Ecosystem Registry

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/ecosystem_registry/` (TrustState, search/resolve_version/is_compatible/set_trust/checksum); **9 automated tests**; discovery cho extension.

**Mục tiêu**  
Registry discovery cho extension.

**Phạm vi**
- Triển khai đúng contract và invariant của milestone; tích hợp với Runtime/Harness hiện có, không tạo control plane song song.

**Deliverables**
- Implementation + tests + docs/ADR khi cần.

**Acceptance Criteria**
- AC của task PASS; regression của các milestone trước PASS; không vi phạm invariant.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-047 — Developer Kit

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/devkit/` (manifest, packaging, cli: create/validate/test/simulate/package/inspect); **20 automated tests**; tooling dev/test extension.

**Mục tiêu**  
CLI/tooling tạo, dev, test extension.

**Phạm vi**
- Triển khai đúng contract và invariant của milestone; tích hợp với Runtime/Harness hiện có, không tạo control plane song song.

**Deliverables**
- Implementation + tests + docs/ADR khi cần.

**Acceptance Criteria**
- AC của task PASS; regression của các milestone trước PASS; không vi phạm invariant.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-048 — Ecosystem Hub

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/ecosystem_hub/` (search/is_compatible/install qua PluginRuntime + checksum/provenance); **10 automated tests**; phân phối extension.

**Mục tiêu**  
Phân phối extension.

**Phạm vi**
- Triển khai đúng contract và invariant của milestone; tích hợp với Runtime/Harness hiện có, không tạo control plane song song.

**Deliverables**
- Implementation + tests + docs/ADR khi cần.

**Acceptance Criteria**
- AC của task PASS; regression của các milestone trước PASS; không vi phạm invariant.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-049 — Certification

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/certification/` (pipeline, profiles, checks, revocation, expiry); **17 automated tests**; trust cho ecosystem.

**Mục tiêu**  
Certification và trust cho ecosystem.

**Phạm vi**
- Triển khai đúng contract và invariant của milestone; tích hợp với Runtime/Harness hiện có, không tạo control plane song song.

**Deliverables**
- Implementation + tests + docs/ADR khi cần.

**Acceptance Criteria**
- AC của task PASS; regression của các milestone trước PASS; không vi phạm invariant.

**Dependency / Gate**
- Theo dependency của milestone.

---

# M9

## TASK-050 — Autonomous Goal Engine

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/autonomous_goal/` (engine, state_machine, policy, objectives/progress/boundary/evidence); **12 automated tests**; goal dài hạn tự chủ.

**Mục tiêu**  
Quản lý goal dài hạn tự chủ.

**Phạm vi**
- Triển khai đúng contract và invariant của milestone; tích hợp với Runtime/Harness hiện có, không tạo control plane song song.

**Deliverables**
- Implementation + tests + docs/ADR khi cần.

**Acceptance Criteria**
- AC của task PASS; regression của các milestone trước PASS; không vi phạm invariant.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-051 — Autonomous Planner

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/autonomous_planner/` (planner, validation, contracts); **10 automated tests**; lập kế hoạch động.

**Mục tiêu**  
Lập kế hoạch động.

**Phạm vi**
- Triển khai đúng contract và invariant của milestone; tích hợp với Runtime/Harness hiện có, không tạo control plane song song.

**Deliverables**
- Implementation + tests + docs/ADR khi cần.

**Acceptance Criteria**
- AC của task PASS; regression của các milestone trước PASS; không vi phạm invariant.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-052 — World Model

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/world_model/`; **8 automated tests**; tách world state khỏi memory.

**Mục tiêu**  
Tách world state khỏi memory.

**Phạm vi**
- Triển khai đúng contract và invariant của milestone; tích hợp với Runtime/Harness hiện có, không tạo control plane song song.

**Deliverables**
- Implementation + tests + docs/ADR khi cần.

**Acceptance Criteria**
- AC của task PASS; regression của các milestone trước PASS; không vi phạm invariant.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-053 — Autonomous Loop

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/autonomous_loop/` (loop, contracts); **6 automated tests**; plan→act→observe→learn.

**Mục tiêu**  
Đóng vòng plan→act→observe→learn.

**Phạm vi**
- Triển khai đúng contract và invariant của milestone; tích hợp với Runtime/Harness hiện có, không tạo control plane song song.

**Deliverables**
- Implementation + tests + docs/ADR khi cần.

**Acceptance Criteria**
- AC của task PASS; regression của các milestone trước PASS; không vi phạm invariant.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-054 — Autonomy Governor

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/autonomy_governor/` (governor, contracts); **11 automated tests**; giới hạn quyền tự chủ.

**Mục tiêu**  
Giới hạn quyền tự chủ.

**Phạm vi**
- Triển khai đúng contract và invariant của milestone; tích hợp với Runtime/Harness hiện có, không tạo control plane song song.

**Deliverables**
- Implementation + tests + docs/ADR khi cần.

**Acceptance Criteria**
- AC của task PASS; regression của các milestone trước PASS; không vi phạm invariant.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-055 — Autonomous Recovery

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/autonomous_recovery/` (recovery, circuit, contracts); **8 automated tests**; circuit breaker + recovery.

**Mục tiêu**  
Circuit breaker và recovery.

**Phạm vi**
- Triển khai đúng contract và invariant của milestone; tích hợp với Runtime/Harness hiện có, không tạo control plane song song.

**Deliverables**
- Implementation + tests + docs/ADR khi cần.

**Acceptance Criteria**
- AC của task PASS; regression của các milestone trước PASS; không vi phạm invariant.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-056 — Long-Horizon Execution

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/goal_durability/`; **9 automated tests**; checkpoint/resume goal dài.

**Mục tiêu**  
Checkpoint/resume cho goal dài.

**Phạm vi**
- Triển khai đúng contract và invariant của milestone; tích hợp với Runtime/Harness hiện có, không tạo control plane song song.

**Deliverables**
- Implementation + tests + docs/ADR khi cần.

**Acceptance Criteria**
- AC của task PASS; regression của các milestone trước PASS; không vi phạm invariant.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-057 — Autonomous Memory

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/autonomous_memory/` (controller, retention, contracts); **8 automated tests**; failure/goal memory có kiểm soát.

**Mục tiêu**  
Lưu failure/goal memory có kiểm soát.

**Phạm vi**
- Triển khai đúng contract và invariant của milestone; tích hợp với Runtime/Harness hiện có, không tạo control plane song song.

**Deliverables**
- Implementation + tests + docs/ADR khi cần.

**Acceptance Criteria**
- AC của task PASS; regression của các milestone trước PASS; không vi phạm invariant.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-058 — Autonomous Experimentation

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/autonomous_experimentation/` (controller, contracts); **9 automated tests**; thử nghiệm cải tiến có harness.

**Mục tiêu**  
Thử nghiệm cải tiến có harness.

**Phạm vi**
- Triển khai đúng contract và invariant của milestone; tích hợp với Runtime/Harness hiện có, không tạo control plane song song.

**Deliverables**
- Implementation + tests + docs/ADR khi cần.

**Acceptance Criteria**
- AC của task PASS; regression của các milestone trước PASS; không vi phạm invariant.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-059 — Multi-Agent Autonomy

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/multi_agent_autonomy/`; **8 automated tests**; delegation giữa agent.

**Mục tiêu**  
Delegation giữa agent.

**Phạm vi**
- Triển khai đúng contract và invariant của milestone; tích hợp với Runtime/Harness hiện có, không tạo control plane song song.

**Deliverables**
- Implementation + tests + docs/ADR khi cần.

**Acceptance Criteria**
- AC của task PASS; regression của các milestone trước PASS; không vi phạm invariant.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-060 — Autonomous Evaluation

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/autonomous_evaluation/` (evaluator, contracts); **11 automated tests** (stuck_detection); phát hiện loop/oscillation/stuck.

**Mục tiêu**  
Đánh giá để quyết định bước tiếp.

**Phạm vi**
- Triển khai đúng contract và invariant của milestone; tích hợp với Runtime/Harness hiện có, không tạo control plane song song.

**Deliverables**
- Implementation + tests + docs/ADR khi cần.

**Acceptance Criteria**
- AC của task PASS; regression của các milestone trước PASS; không vi phạm invariant.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-061 — Advanced Stuck Detection

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/stuck_detection/`; **11 automated tests**; phát hiện loop/oscillation/stuck.

**Mục tiêu**  
Phát hiện loop/oscillation/stuck.

**Phạm vi**
- Triển khai đúng contract và invariant của milestone; tích hợp với Runtime/Harness hiện có, không tạo control plane song song.

**Deliverables**
- Implementation + tests + docs/ADR khi cần.

**Acceptance Criteria**
- AC của task PASS; regression của các milestone trước PASS; không vi phạm invariant.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-062 — Autonomous Scheduler

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/autonomous_scheduler/` (scheduler, contracts); **10 automated tests**; kích hoạt goal theo schedule/trigger.

**Mục tiêu**  
Kích hoạt goal theo schedule/trigger.

**Phạm vi**
- Triển khai đúng contract và invariant của milestone; tích hợp với Runtime/Harness hiện có, không tạo control plane song song.

**Deliverables**
- Implementation + tests + docs/ADR khi cần.

**Acceptance Criteria**
- AC của task PASS; regression của các milestone trước PASS; không vi phạm invariant.

**Dependency / Gate**
- Theo dependency của milestone.

---

# M10

## TASK-063 — AIOS Architecture 1.0

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/governance/architecture/` (ADR + baseline freeze); thuộc **310 net-new tests M10** (full suite 1962→2272); architecture 1.0 đóng băng.

**Mục tiêu**  
Đóng băng architecture baseline.

**Phạm vi**
- Triển khai đúng contract và invariant của milestone; tích hợp với Runtime/Harness hiện có, không tạo control plane song song.

**Deliverables**
- Implementation + tests + docs/ADR khi cần.

**Acceptance Criteria**
- AC của task PASS; regression của các milestone trước PASS; không vi phạm invariant.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-064 — Public Contract Freeze

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/contracts/` (public contract freeze 1.0); thuộc 310 net-new tests M10.

**Mục tiêu**  
Freeze public contracts 1.0.

**Phạm vi**
- Triển khai đúng contract và invariant của milestone; tích hợp với Runtime/Harness hiện có, không tạo control plane song song.

**Deliverables**
- Implementation + tests + docs/ADR khi cần.

**Acceptance Criteria**
- AC của task PASS; regression của các milestone trước PASS; không vi phạm invariant.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-065 — Runtime Production Hardening

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/runtime/` (production hardening); thuộc 310 net-new tests M10.

**Mục tiêu**  
Hardening runtime.

**Phạm vi**
- Triển khai đúng contract và invariant của milestone; tích hợp với Runtime/Harness hiện có, không tạo control plane song song.

**Deliverables**
- Implementation + tests + docs/ADR khi cần.

**Acceptance Criteria**
- AC của task PASS; regression của các milestone trước PASS; không vi phạm invariant.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-066 — Durable Execution 1.0

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/durable/` (durable state/checkpoint/recovery); thuộc 310 net-new tests M10.

**Mục tiêu**  
Durable state/checkpoint/recovery.

**Phạm vi**
- Triển khai đúng contract và invariant của milestone; tích hợp với Runtime/Harness hiện có, không tạo control plane song song.

**Deliverables**
- Implementation + tests + docs/ADR khi cần.

**Acceptance Criteria**
- AC của task PASS; regression của các milestone trước PASS; không vi phạm invariant.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-067 — Autonomy Safety 1.0

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/autonomy_safety/` (bounded autonomy, boundary, contracts); thuộc 310 net-new tests M10.

**Mục tiêu**  
Bounded autonomy.

**Phạm vi**
- Triển khai đúng contract và invariant của milestone; tích hợp với Runtime/Harness hiện có, không tạo control plane song song.

**Deliverables**
- Implementation + tests + docs/ADR khi cần.

**Acceptance Criteria**
- AC của task PASS; regression của các milestone trước PASS; không vi phạm invariant.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-068 — Kill Switch

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/kill_switch/` (emergency stop); thuộc 310 net-new tests M10.

**Mục tiêu**  
Emergency stop.

**Phạm vi**
- Triển khai đúng contract và invariant của milestone; tích hợp với Runtime/Harness hiện có, không tạo control plane song song.

**Deliverables**
- Implementation + tests + docs/ADR khi cần.

**Acceptance Criteria**
- AC của task PASS; regression của các milestone trước PASS; không vi phạm invariant.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-069 — Reliability Engineering

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/reliability/` (SLO/reliability controls); thuộc 310 net-new tests M10.

**Mục tiêu**  
SLO và reliability controls.

**Phạm vi**
- Triển khai đúng contract và invariant của milestone; tích hợp với Runtime/Harness hiện có, không tạo control plane song song.

**Deliverables**
- Implementation + tests + docs/ADR khi cần.

**Acceptance Criteria**
- AC của task PASS; regression của các milestone trước PASS; không vi phạm invariant.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-070 — AIOS Security Baseline

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/security/` (security baseline 1.0); thuộc 310 net-new tests M10.

**Mục tiêu**  
Security baseline 1.0.

**Phạm vi**
- Triển khai đúng contract và invariant của milestone; tích hợp với Runtime/Harness hiện có, không tạo control plane song song.

**Deliverables**
- Implementation + tests + docs/ADR khi cần.

**Acceptance Criteria**
- AC của task PASS; regression của các milestone trước PASS; không vi phạm invariant.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-071 — AIOS 1.0 Developer Experience

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/devkit/` + `aios/cli/` (DX 1.0); thuộc 310 net-new tests M10.

**Mục tiêu**  
DX production.

**Phạm vi**
- Triển khai đúng contract và invariant của milestone; tích hợp với Runtime/Harness hiện có, không tạo control plane song song.

**Deliverables**
- Implementation + tests + docs/ADR khi cần.

**Acceptance Criteria**
- AC của task PASS; regression của các milestone trước PASS; không vi phạm invariant.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-072 — AIOS Dashboard 1.0

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/dashboard/` (dashboard 1.0); thuộc 310 net-new tests M10.

**Mục tiêu**  
Dashboard release.

**Phạm vi**
- Triển khai đúng contract và invariant của milestone; tích hợp với Runtime/Harness hiện có, không tạo control plane song song.

**Deliverables**
- Implementation + tests + docs/ADR khi cần.

**Acceptance Criteria**
- AC của task PASS; regression của các milestone trước PASS; không vi phạm invariant.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-073 — AIOS 1.0 Certification Suite

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/certification/` (cert suite 1.0, release certifier); thuộc 310 net-new tests M10.

**Mục tiêu**  
Certification suite.

**Phạm vi**
- Triển khai đúng contract và invariant của milestone; tích hợp với Runtime/Harness hiện có, không tạo control plane song song.

**Deliverables**
- Implementation + tests + docs/ADR khi cần.

**Acceptance Criteria**
- AC của task PASS; regression của các milestone trước PASS; không vi phạm invariant.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-074 — Upgrade & Migration 1.0

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/upgrade/` (migration engine 1.0); thuộc 310 net-new tests M10.

**Mục tiêu**  
Migration 1.0.

**Phạm vi**
- Triển khai đúng contract và invariant của milestone; tích hợp với Runtime/Harness hiện có, không tạo control plane song song.

**Deliverables**
- Implementation + tests + docs/ADR khi cần.

**Acceptance Criteria**
- AC của task PASS; regression của các milestone trước PASS; không vi phạm invariant.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-075 — Performance & Cost + Model Independence

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/cost_meter/` + `aios/model_router/` (perf/cost + provider independence); thuộc 310 net-new tests M10.

**Mục tiêu**  
Hiệu năng, cost và provider independence.

**Phạm vi**
- Triển khai đúng contract và invariant của milestone; tích hợp với Runtime/Harness hiện có, không tạo control plane song song.

**Deliverables**
- Implementation + tests + docs/ADR khi cần.

**Acceptance Criteria**
- AC của task PASS; regression của các milestone trước PASS; không vi phạm invariant.

**Dependency / Gate**
- Theo dependency của milestone.

---

# M11

## TASK-076 — Reserved / Not Specified in Source

> **Trạng thái thực tế (2026-08-23):** DONE (reserved) — giữ chỗ ID lịch sử, **không có implementation/test** (theo quy tắc không tái sử dụng ID).

**Mục tiêu**  
Giữ nguyên khoảng trống ID lịch sử để không tái sử dụng task ID.

**Phạm vi**
- Không tự gán implementation mới khi nguồn không định nghĩa canonical task.

**Deliverables**
- Entry giữ chỗ trong master task index.

**Acceptance Criteria**
- ID không bị tái sử dụng; nếu cần bổ sung phải tạo Amendment/ADR hoặc task ID mới.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-077 — Reserved / Not Specified in Source

> **Trạng thái thực tế (2026-08-23):** DONE (reserved) — giữ chỗ ID lịch sử, **không có implementation/test**.

**Mục tiêu**  
Giữ nguyên khoảng trống ID lịch sử để không tái sử dụng task ID.

**Phạm vi**
- Không tự gán implementation mới khi nguồn không định nghĩa canonical task.

**Deliverables**
- Entry giữ chỗ trong master task index.

**Acceptance Criteria**
- ID không bị tái sử dụng; nếu cần bổ sung phải tạo Amendment/ADR hoặc task ID mới.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-078 — Verification Integrity / Fail-Closed Gate

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/verification_integrity/`; **8 automated tests**; fail-closed gate, trust/evidence.

**Mục tiêu**  
Hoàn thiện năng lực được định nghĩa cho milestone và mở rộng trust/evidence mà không phá Core.

**Phạm vi**
- Contracts, implementation, harness, evidence, policy boundary và documentation theo task.

**Deliverables**
- Artifact implementation + conformance tests + evidence + ADR/docs khi task yêu cầu.

**Acceptance Criteria**
- Task đạt AC; fail-closed; regression và trust gates PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-079 — RenderReplay / Deterministic Harness

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/replay/`; **5 automated tests**; render replay / deterministic harness.

**Mục tiêu**  
Hoàn thiện năng lực được định nghĩa cho milestone và mở rộng trust/evidence mà không phá Core.

**Phạm vi**
- Contracts, implementation, harness, evidence, policy boundary và documentation theo task.

**Deliverables**
- Artifact implementation + conformance tests + evidence + ADR/docs khi task yêu cầu.

**Acceptance Criteria**
- Task đạt AC; fail-closed; regression và trust gates PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-080 — Visual Evidence + Visual Regression + UI State Contract

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/visual_evidence/`; **6 automated tests**; visual regression + UI state contract.

**Mục tiêu**  
Hoàn thiện năng lực được định nghĩa cho milestone và mở rộng trust/evidence mà không phá Core.

**Phạm vi**
- Contracts, implementation, harness, evidence, policy boundary và documentation theo task.

**Deliverables**
- Artifact implementation + conformance tests + evidence + ADR/docs khi task yêu cầu.

**Acceptance Criteria**
- Task đạt AC; fail-closed; regression và trust gates PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-081 — Asset Pipeline + Asset Capability Registry + Routing

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/asset_pipeline/`; **7 automated tests**; asset pipeline + registry + routing.

**Mục tiêu**  
Hoàn thiện năng lực được định nghĩa cho milestone và mở rộng trust/evidence mà không phá Core.

**Phạm vi**
- Contracts, implementation, harness, evidence, policy boundary và documentation theo task.

**Deliverables**
- Artifact implementation + conformance tests + evidence + ADR/docs khi task yêu cầu.

**Acceptance Criteria**
- Task đạt AC; fail-closed; regression và trust gates PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-082 — Creative Domain + Vendor Integrity + Reference Asset

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/creative_domain/`; **7 automated tests**; creative domain + vendor integrity + reference asset.

**Mục tiêu**  
Hoàn thiện năng lực được định nghĩa cho milestone và mở rộng trust/evidence mà không phá Core.

**Phạm vi**
- Contracts, implementation, harness, evidence, policy boundary và documentation theo task.

**Deliverables**
- Artifact implementation + conformance tests + evidence + ADR/docs khi task yêu cầu.

**Acceptance Criteria**
- Task đạt AC; fail-closed; regression và trust gates PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-083 — SkillDistiller + Static Deploy

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/skill_distiller/`; **6 automated tests**; skill distiller + static deploy.

**Mục tiêu**  
Hoàn thiện năng lực được định nghĩa cho milestone và mở rộng trust/evidence mà không phá Core.

**Phạm vi**
- Contracts, implementation, harness, evidence, policy boundary và documentation theo task.

**Deliverables**
- Artifact implementation + conformance tests + evidence + ADR/docs khi task yêu cầu.

**Acceptance Criteria**
- Task đạt AC; fail-closed; regression và trust gates PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-219 — GitHub Skill → AIOS Skill Plugin Bridge (Amendment)

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/skill/github_bridge/` (parser, adapter, converter) + `tools/install_github_skill.py` + `skills/ui-ux-pro-max/`; **13 automated tests** (9 unit + 3 real-skill + 1 persisted); bridge GitHub Copilot/Claude skill → AIOS Skill Plugin.

**Mục tiêu**  
Xây **bridge/adapter** chuyển đổi một GitHub Copilot skill (thư mục chứa `SKILL.md` + `scripts/` + `agents/`) thành một **AIOS Skill Plugin** có thể nạp qua lifecycle chuẩn (`SkillManager.install` → `enable`). Tận dụng khung có sẵn `aios/skill` (TASK-015, M2) và `aios/plugin_runtime` (TASK-044, M8) — **không** viết lại runtime.

**Phạm vi**
- `aios/skill/github_bridge/`: `parser.py` (parse `SKILL.md` frontmatter + body, `agents/*.yaml`, `skill.json` + `.claude/skills/*/SKILL.md`), `adapter.py` (map → `SkillContract` + `PluginManifest`), `converter.py` (sinh package: `skills/<id>/manifest.json`, `prompts/instructions.md`, `SKILL.md`, `plugin_manifest.json`, `catalog/skill-<id>.json`, `package_index.json`).
- Hỗ trợ **2 layout** (tự detect): `copilot` (root `SKILL.md` → 1 skill) và `claude` (`skill.json` + `.claude/skills/<name>/SKILL.md` → N sub-skill, mỗi sub-skill 1 contract). Đã thực tế validate với `ui-ux-pro-max-skill` (7 sub-skill).
- Ánh xạ: `SKILL.md`→`SkillContract`; `scripts/*.py`→`entrypoint`; `agents/*.yaml` `tools`→`required_capabilities`; permission hints→`ALLOWED_PERMISSIONS`; runtime→`ALLOWED_RUNTIMES`.
- Tích hợp `SkillManager` (T015) + `PluginManifest` (T044) + `ArchitectureGuard` (T063).

**Deliverables**
- `aios/skill/github_bridge/{parser,adapter,converter}.py` + `__init__.py` + `tests/` (13 tests: 9 unit + 3 real-skill + 1 persisted).
- `tools/install_github_skill.py` — CLI clone/convert/install/enable persistent.
- **Skill thực tế đã lưu:** `skills/ui-ux-pro-max/` (7 sub-skill từ `nextlevelbuilder/ui-ux-pro-max-skill`, layout `claude`).
- Task artifacts + evidence + ADR/docs.

**Acceptance Criteria**
- Parse `SKILL.md` (có/không frontmatter) → structured data đúng.
- `to_skill_contract` sinh `SkillContract` hợp lệ (`validate()` PASS).
- `convert_skill_dir` sinh package đầy đủ (manifest + prompts + scripts + plugin_manifest + catalog).
- Contract sinh ra có thể `install` + `enable` qua `SkillManager` → status `ENABLED`.
- Cùng input skill + converter → cùng package (deterministic, không timestamp).
- Architecture gate quét package → không vi phạm ARCH-001..004.
- Persist: package sinh ra lưu được dưới `skills/` và reload + enable lại qua `SkillManager` (test_persisted_skills).
- Regression của TASK-047/083/046/049 PASS; không vi phạm invariants.

**Dependency / Gate**
- TASK-083 (SkillDistiller, M11) → TASK-219 (M11) → TASK-084 (M12).
- T015 (skill), T044 (plugin runtime), T063 (architecture guard), T046 (ecosystem registry), T049 (certification).

---

## TASK-220 — AIOS Coordinator Agent (Control-Plane + Chat Agent)

> **Trạng thái thực tế (2026-08-24):** DONE — `aios/agents/coordinator.py` (`CoordinatorAgent`, `CoordinationResult`, `CoordinationStep`) + export trong `aios/agents/__init__.py` + `aios/agents/tests/test_coordinator.py` (**3 tests**) + `.github/agents/aios-coordinator.agent.md` (custom VS Code chat agent). Unified Gate PASS; full suite 3141 tests (sau T220).

**Mục tiêu**  
Xây **CoordinatorAgent** — agent tầng `agents` (pure, I/O-free, capability-injected) điều phối các agent vai trò khác (`SpecWriter`, `Critic`, `Reviewer`, `Orchestrator`) qua pipeline governance: `spec → critique×2 → breakdown(tasks) → review → orchestrate/close`. Đồng thời đóng gói một **custom chat agent** (`.agent.md`) để người dùng chọn từ dropdown chat VS Code và agent tự biết bước tiếp theo.

**Phạm vi**
- `aios/agents/coordinator.py`: `CoordinatorAgent` nhận 4 sub-agent qua constructor (Protocol injection); `coordinate(task_id, spec_input)` chạy pipeline; `CoordinationResult`/`CoordinationStep` dataclass + `to_dict()`; fail-closed (review reject → không close).
- `aios/agents/__init__.py`: export `CoordinatorAgent`, `CoordinationResult`, `CoordinationStep`.
- `aios/agents/tests/test_coordinator.py`: 3 tests (happy path close, fail-closed reject, deterministic).
- `.github/agents/aios-coordinator.agent.md`: `user-invocable: true`, mô tả pipeline + next-step loop.

**Deliverables**
- `aios/agents/coordinator.py` + `__init__` export + test + chat agent + task artifacts.

**Acceptance Criteria**
- `CoordinatorAgent` nhận 4 sub-agent qua injection; không import `subprocess`/`os`/provider/filesystem (ARCH-001..004).
- Pipeline sinh đủ artifact keys: `spec.md`, `critique-1.md`, `critique-2.md`, `tasks.md`.
- Review reject → `approved=False` và `closed=False` (fail-closed).
- Cùng input → cùng `result.to_dict()` (deterministic).
- `pytest aios/agents/tests/test_coordinator.py -q` → 3 passed; architecture gate `agents` clean.
- `.github/agents/aios-coordinator.agent.md` có `description` + `tools` + `user-invocable: true`.

**Dependency / Gate**
- TASK-001 (lifecycle + gates), TASK-008 (workflow CLI), TASK-125 (coder contract pattern tham khảo).
- Milestone M27 (post-M26 control-plane extension).

---

## TASK-221 — Coordinator Chat API Endpoint

> **Trạng thái thực tế (2026-08-24):** DONE — `aios/api/routers/coordinator.py` (`POST /coordinator/run`, `GET /coordinator/{task_id}`) + `aios/api/schemas.py` (`CoordinatorRunRequest`, `CoordinatorRunResponse`, `CoordinatorStep`) + include trong `aios/api/app.py` + `aios/api/tests/test_coordinator_router.py` (**4 tests**). Unified Gate PASS; full suite 3145 tests (sau T221).

**Mục tiêu**  
Thêm endpoint REST cho phép client (chat UI / script) gửi `{task_id, objective, scope, deliverables, acceptance, dependencies}` và nhận kết quả điều phối từ `CoordinatorAgent` (TASK-220). Endpoint nằm tầng `api`, gọi xuống `agents` (downward-only, ARCH-004).

**Phạm vi**
- `aios/api/routers/coordinator.py`: 2 endpoints, in-memory store, gọi `CoordinatorAgent.coordinate()` thực tế.
- Gọi `CoordinatorAgent` với `_FakeOrchestrator` (prototype) để phản ánh kết quả coordination.
- `aios/api/schemas.py`: Pydantic v2 request/response, version `API_VERSION`.
- `aios/api/app.py`: include router (prefix `API_PREFIX`).

**Deliverables**
- Router + schema + app include + test + task artifacts.

**Acceptance Criteria**
- `POST /api/v1/coordinator/run` nhận `CoordinatorRunRequest` → trả `CoordinatorRunResponse` (task_id, approved, closed, artifacts, steps).
- Gọi `CoordinatorAgent.coordinate()` thực tế (không mock cứng).
- `GET /api/v1/coordinator/{task_id}` trả result đã lưu hoặc 404.
- Architecture gate: `api` → `agents` downward OK (ARCH-004).
- `pytest aios/api/tests/test_coordinator_router.py -q` → passed; full suite regression green.

**Dependency / Gate**
- TASK-220 (CoordinatorAgent), TASK-017 (API boundary), TASK-001 (lifecycle/gates).
- Milestone M27.

---

## TASK-222 — AIOS Real Executor + CLI `execute` (practical usage)

> **Trạng thái thực tế (2026-08-24):** DONE — `aios/runtime/process.py` (`RealToolHandler`) + `aios/runtime/workflow/definition.py` (`to_execution_plan`/`from_markdown`) + `aios/runtime/kernel.py` (`execute_plan`) + `aios/cli/workflow_cli.py` (`execute` subcommand) + `configs/default.yaml` (`real_execution.enabled`) + `aios/runtime/tests/test_process.py` (8) + `aios/cli/tests/test_execute.py` (3); **11 automated tests**; full suite 3156 passed, 3 skipped; Unified Gate PASS.

**Mục tiêu**  
Biến AIOS từ "hệ thống tự quản lý" thành "môi trường thực thi task thật" mà **không cần model/LLM và không cần API ngoài** (máy yếu). Copilot/OpenCode đóng vai "não" lập plan; AIOS làm "đôi tay + hàng rào an toàn": thực thi plan qua **real tool executor** (shell/file/git) được **Policy/Permission** kiểm soát, ghi **evidence** chuẩn provenance chain.

**Phạm vi**
- Real execution trong `aios/runtime/` (shell, git, file write) có Policy/Permission pre-check (fail-closed).
- Subcommand `execute` MỚI trong `aios/cli/workflow_cli.py` (không động `run` cũ — DX stability T071).
- Converter `WorkflowDefinition.to_execution_plan()` gán `scope`/`resource` để policy pre-check fire; `from_markdown()` parse plan Markdown (`- [ ]` lines).
- Hỗ trợ plan YAML/JSON và Markdown; flag `--simulate` chỉ validate, 0 LLM call, không exec.
- Evidence provenance chain đầy đủ (Evidence→Run→Artifact→Task→Requirement).
- Config `real_execution.enabled: false` mặc định (safe default, opt-in).

**Deliverables**
- `aios/runtime/process.py` (`RealToolHandler` + denylist + timeout-kill cross-platform) + test.
- `aios/runtime/workflow/definition.py` (`to_execution_plan`/`from_markdown`) + `aios/runtime/kernel.py` (`execute_plan`).
- `aios/cli/workflow_cli.py` (`execute` subcommand) + `configs/default.yaml` (`real_execution.enabled`).
- Task artifacts + evidence + ADR/docs.

**Acceptance Criteria**
- `aiagent execute sample.yaml` chạy plan có 1 node shell `echo` + 1 node `git status`, tạo file output.
- Step thiếu permission (broker không grant) → DENY fail-closed, không exec.
- `real_execution.enabled: false` → mọi exec bị chặn (safe default).
- Timeout giữa step → subprocess bị kill (Windows `CTRL_BREAK_EVENT` / POSIX `killpg`).
- Evidence provenance chain complete (5 registries) sau run.
- `python -m pytest aios/governance/architecture -q` → 0 violations.
- `aiagent execute sample.md --simulate` → chỉ validate, 0 LLM call, không exec.

**Dependency / Gate**
- TASK-221 (Coordinator API), TASK-008 (workflow CLI), TASK-005 (runtime kernel), TASK-001 (lifecycle/gates).
- Milestone M27 (post-M26 control-plane extension).

---

## TASK-223 — AIOS Planner Agent + Skill (request → plan.yaml)

> **Trạng thái thực tế (2026-08-24):** DONE — `.github/agents/aios-planner.agent.md` + `.github/skills/aios-plan/SKILL.md` + sample plans + `aios/cli/tests/test_planner_agent.py` (**5 automated tests**); full suite 3161 passed; Unified Gate PASS.

**Mục tiêu**  
Đóng vòng lặp thực tế: người dùng ra lệnh (bằng tiếng Việt) → một **agent/skill** tiếp nhận, phân tích, và sinh ra file `plan.yaml` chuẩn `WorkflowDefinition` (có `command` ở mỗi node) → user chạy `aiagent execute plan.yaml` (TASK-222) để AIOS tự thực thi. Không cần LLM trong AIOS, không API ngoài — "não" là Copilot/OpenCode, AIOS làm "đôi tay".

**Phạm vi**
- Agent `.github/agents/aios-planner.agent.md` — chuyên trách nhận yêu cầu, sinh `plan.yaml` (I/O-free, chỉ text).
- Skill `.github/skills/aios-plan/SKILL.md` — slash command `/aios-plan <yêu cầu>` hướng dẫn format plan + gọi `aiagent execute`.
- Template plan mẫu + test xác thực agent sinh plan hợp lệ (validate qua `WorkflowDefinition.from_file`).

**Deliverables**
- `.github/agents/aios-planner.agent.md` (custom VS Code chat agent, `user-invocable: true`).
- `.github/skills/aios-plan/SKILL.md` (slash command + plan schema + shell-agnostic rules).
- Sample plans + `aios/cli/tests/test_planner_agent.py` (5 tests).
- Task artifacts + evidence + ADR/docs.

**Acceptance Criteria**
- Agent sinh `plan.yaml` có `workflow.name/version/nodes[].command/permissions`.
- `aiagent validate plan.yaml` (TASK-008) PASS với plan do agent sinh.
- Plan có thể chạy qua `aiagent execute plan.yaml` (TASK-222).
- Skill `/aios-plan` hướng dẫn đúng format + link TASK-222.
- Test tự động: agent prompt sinh plan → `WorkflowDefinition.from_file` không raise.
- Architecture gate 0 violations (agent/skill không import runtime internals).

**Dependency / Gate**
- TASK-222 (real executor + CLI execute), TASK-008 (workflow CLI), TASK-001 (lifecycle/gates).
- Milestone M27 (post-M26 control-plane extension).

---

## TASK-224 — Planner confirm flow + `work/` directory convention

> **Trạng thái thực tế (2026-08-24):** DONE — `aios/cli/workflow_cli.py` (`--work-dir` + `--yes`) + `.github/agents/aios-planner.agent.md` + `.github/skills/aios-plan/SKILL.md` (updated) + `aios/cli/tests/test_execute_workdir.py` (**4 automated tests**); full suite 3161+ passed; Unified Gate PASS.

**Mục tiêu**  
Cải tiến luồng thực tế AIOS theo phản hồi user:
1. **Confirm trước khi thực thi**: sau khi sinh `plan.yaml`, agent/skill HỎI user có muốn chạy không. Chỉ khi user đồng ý mới gọi terminal chạy `aiagent execute`.
2. **Quy ước vị trí file**: tại repo root tạo folder `work/`. Mỗi việc = 1 subfolder `YYYYMMDD-tenngan` (vd `20260824-webno1`). `plan.yaml` + mọi source sinh ra đều nằm trong folder đó.

**Phạm vi**
- Cập nhật `.github/agents/aios-planner.agent.md` + `.github/skills/aios-plan/SKILL.md`: hỏi confirm + quy ước `work/YYYYMMDD-tenngan/`.
- `aios/cli/workflow_cli.py` `_cmd_execute`: thêm `--work-dir <dir>` (tạo folder nếu chưa có, đặt plan vào đó, chạy với `allowed_cwd` = folder đó) + `--yes` (bỏ qua confirm khi gọi từ script/agent). Khi không có `--yes` và chạy interactive → in prompt xác nhận.
- Test: work-dir tạo đúng folder, plan nằm trong, execute chạy được, `--yes` bỏ qua prompt.

**Deliverables**
- `aios/cli/workflow_cli.py` (`--work-dir` + `--yes`) + `aios/cli/tests/test_execute_workdir.py` (4 tests).
- Updated `.github/agents/aios-planner.agent.md` + `.github/skills/aios-plan/SKILL.md`.
- Task artifacts + evidence + ADR/docs.

**Acceptance Criteria**
- Agent sinh plan vào `work/YYYYMMDD-tenngan/plan.yaml`.
- Agent HỎI user "thực hiện không?" trước khi chạy.
- `aiagent execute plan.yaml --work-dir work/20260824-x` tạo folder, chạy, source trong đó.
- `--yes` bỏ qua confirm (script/agent tự gọi).
- Architecture gate 0 violations.
- Full suite không regress.

**Dependency / Gate**
- TASK-223 (planner agent + skill), TASK-222 (real executor + CLI execute), TASK-001 (lifecycle/gates).
- Milestone M27 (post-M26 control-plane extension).

---

## TASK-225 — AIOS Self-Improver Agent

> **Trạng thái thực tế (2026-08-25):** DONE — `aios/agents/self_improver.py` (`SelfImproverAgent`, pure/I/O-free, capability-injected) + `aios/agents/tests/test_self_improver.py` (**4 automated tests**); `.github/agents/aios-self-improver.agent.md`; full suite 3161+ passed; Unified Gate PASS.

**Mục tiêu**  
Bổ sung lớp **Self-Improver** cho phép AIOS phản tư vận hành của chính nó (EvidenceStore + regression log) và ĐỀ XUẤT (không tự áp dụng) task cải tiến nội bộ, đẩy qua pipeline 7-gate như mọi task. Đây là bước "nâng cấp bản thân" — AIOS biết nhận diện điểm yếu của chính nó một cách deterministic, fail-closed.

**Phạm vi**
- `aios/agents/self_improver.py`: `SelfImproverAgent` nhận `evidence_store` + `registry` (capability-injected), quét tín hiệu FAIL/UNKNOWN, tổng hợp theo producer, sinh `ImprovementProposal` (spec sẵn sàng đưa vào governance). Không import `subprocess`/`os`/provider/filesystem (ARCH-001..004).
- `aios/agents/__init__.py`: export `SelfImproverAgent`, `SelfImproverResult`, `ImprovementProposal`.
- `aios/agents/tests/test_self_improver.py`: pure / fail-closed / deterministic / propose_next.
- `.github/agents/aios-self-improver.agent.md`: chat agent chọn từ picker, tự chạy vòng phản tư.

**Deliverables**
- `aios/agents/self_improver.py` + test + chat agent + task artifacts + evidence.

**Acceptance Criteria**
- Pure: 0 vi phạm ARCH-001..004 (architecture gate PASS).
- Capability-injected: chỉ qua interface, không tự làm I/O.
- Deterministic: cùng input -> cùng proposal.
- Fail-closed: thiếu evidence -> không đề xuất (trả None), không đoán.
- Đề xuất ở dạng spec text, KHÔNG ghi thẳng vào `aios/`.
- 7-gate PASS, full suite không regress.

**Dependency / Gate**
- TASK-220 (CoordinatorAgent), TASK-001 (lifecycle/gates), TASK-005 (evidence).
- Milestone M28 (self-evolution / metacognition).

---

## TASK-226 — Deterministic Auto-Stop / RetryGuard

> **Trạng thái thực tế (2026-08-25):** DONE — `aios/runtime/retry_guard.py` (`RetryGuard`) + `aios/runtime/tests/test_retry_guard.py` (**7 automated tests**); Unified Gate PASS; full suite green. Self-Improver TASK-225 proposed this from 165 retry-loop signals.

**Mục tiêu**  
Codify the auto-stop rule (AGENTS.md §12) as deterministic, fail-closed runtime capability: detect repeated identical failures (>= threshold) and halt with root-cause report instead of looping "Try Again".

**Phạm vi**
- `aios/runtime/retry_guard.py`: `RetryGuard` (observe/should_stop/report/reset/count), threshold default 3, fail-closed on bad input.
- `aios/runtime/tests/test_retry_guard.py`: 7 tests.
- No agent-layer import (ARCH-003 compliant); agents receive it via capability injection.

**Deliverables**
- `aios/runtime/retry_guard.py` + test + task artifacts + evidence.

**Acceptance Criteria**
- Auto-stop at/after threshold; distinct signatures independent; report root cause; fail-closed on invalid input; architecture gate 0 violations; full suite no regression.

**Dependency / Gate**
- TASK-225 (Self-Improver proposal), TASK-005 (runtime services), TASK-001 (gates).
- Milestone M28 (self-evolution).

---

## TASK-227 — StubGuard: reject null-stub / SKIPPED pipeline steps

> **Trạng thái thực tế (2026-08-25):** DONE — `aios/runtime/stub_guard.py` (`StubGuard`) + `aios/runtime/tests/test_stub_guard.py` (**7 automated tests**); Unified Gate PASS; full suite green. Self-Improver TASK-225 proposed this from 44 skipped-stub signals.

**Mục tiêu**  
Codify the anti-stub rule (AGENTS.md §12 "cấm null-stub / bước SKIPPED") as deterministic, fail-closed runtime capability: validate every pipeline step status and reject SKIPPED/null-stub steps.

**Phạm vi**
- `aios/runtime/stub_guard.py`: `StubGuard` (record/is_skip/violations/is_clean/report/reset), fail-closed on empty input.
- `aios/runtime/tests/test_stub_guard.py`: 7 tests.
- No agent-layer import (ARCH-003 compliant); agents receive it via capability injection.

**Deliverables**
- `aios/runtime/stub_guard.py` + test + task artifacts + evidence.

**Acceptance Criteria**
- Detect SKIPPED/null/stub/_Null/unknown; report violations; fail-closed on bad input; architecture gate 0 violations; full suite no regression.

**Dependency / Gate**
- TASK-225 (Self-Improver proposal), TASK-005 (runtime services), TASK-001 (gates).
- Milestone M28 (self-evolution).

---
# M12

## TASK-084 — Version + Compatibility Baseline

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/versioning/`; **9 automated tests**; version + compat baseline 1.0→1.1.

**Mục tiêu**  
Hoàn thiện năng lực được định nghĩa cho milestone và mở rộng trust/evidence mà không phá Core.

**Phạm vi**
- Contracts, implementation, harness, evidence, policy boundary và documentation theo task.

**Deliverables**
- Artifact implementation + conformance tests + evidence + ADR/docs khi task yêu cầu.

**Acceptance Criteria**
- Task đạt AC; fail-closed; regression và trust gates PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-085 — Migration 1.0 → 1.1

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/migration/`; **8 automated tests**; migration 1.0→1.1.

**Mục tiêu**  
Hoàn thiện năng lực được định nghĩa cho milestone và mở rộng trust/evidence mà không phá Core.

**Phạm vi**
- Contracts, implementation, harness, evidence, policy boundary và documentation theo task.

**Deliverables**
- Artifact implementation + conformance tests + evidence + ADR/docs khi task yêu cầu.

**Acceptance Criteria**
- Task đạt AC; fail-closed; regression và trust gates PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-086 — Backward Compatibility

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/backward_compat/`; **7 automated tests**; backward compatibility.

**Mục tiêu**  
Hoàn thiện năng lực được định nghĩa cho milestone và mở rộng trust/evidence mà không phá Core.

**Phạm vi**
- Contracts, implementation, harness, evidence, policy boundary và documentation theo task.

**Deliverables**
- Artifact implementation + conformance tests + evidence + ADR/docs khi task yêu cầu.

**Acceptance Criteria**
- Task đạt AC; fail-closed; regression và trust gates PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-087 — Compatibility Conformance

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/conformance/`; **7 automated tests**; compatibility conformance.

**Mục tiêu**  
Hoàn thiện năng lực được định nghĩa cho milestone và mở rộng trust/evidence mà không phá Core.

**Phạm vi**
- Contracts, implementation, harness, evidence, policy boundary và documentation theo task.

**Deliverables**
- Artifact implementation + conformance tests + evidence + ADR/docs khi task yêu cầu.

**Acceptance Criteria**
- Task đạt AC; fail-closed; regression và trust gates PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-088 — Docs & ADR — Compatibility

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/compat_docs/` + `docs/adr/ADR-Compatibility.md`; **7 automated tests**; docs & ADR compatibility.

**Mục tiêu**  
Hoàn thiện năng lực được định nghĩa cho milestone và mở rộng trust/evidence mà không phá Core.

**Phạm vi**
- Contracts, implementation, harness, evidence, policy boundary và documentation theo task.

**Deliverables**
- Artifact implementation + conformance tests + evidence + ADR/docs khi task yêu cầu.

**Acceptance Criteria**
- Task đạt AC; fail-closed; regression và trust gates PASS.

**Dependency / Gate**
- Theo dependency của milestone.

---

# M13

## TASK-089 — Behavioral Conformance

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/behavioral/`; **9 automated tests**; behavioral conformance.

**Mục tiêu**  
Hoàn thiện năng lực được định nghĩa cho milestone và mở rộng trust/evidence mà không phá Core.

**Phạm vi**
- Contracts, implementation, harness, evidence, policy boundary và documentation theo task.

**Deliverables**
- Artifact implementation + conformance tests + evidence + ADR/docs khi task yêu cầu.

**Acceptance Criteria**
- Task đạt AC; fail-closed; regression và trust gates PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-090 — Harness Coverage + Readiness

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/harness_coverage/`; **7 automated tests**; harness coverage + readiness.

**Mục tiêu**  
Hoàn thiện năng lực được định nghĩa cho milestone và mở rộng trust/evidence mà không phá Core.

**Phạm vi**
- Contracts, implementation, harness, evidence, policy boundary và documentation theo task.

**Deliverables**
- Artifact implementation + conformance tests + evidence + ADR/docs khi task yêu cầu.

**Acceptance Criteria**
- Task đạt AC; fail-closed; regression và trust gates PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-091 — Meta-Harness / Verify-the-Verifier

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/meta_harness/`; **7 automated tests**; verify-the-verifier.

**Mục tiêu**  
Hoàn thiện năng lực được định nghĩa cho milestone và mở rộng trust/evidence mà không phá Core.

**Phạm vi**
- Contracts, implementation, harness, evidence, policy boundary và documentation theo task.

**Deliverables**
- Artifact implementation + conformance tests + evidence + ADR/docs khi task yêu cầu.

**Acceptance Criteria**
- Task đạt AC; fail-closed; regression và trust gates PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-092 — System Readiness vs Harness Trust

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/readiness_trust/`; **6 automated tests**; system readiness vs harness trust.

**Mục tiêu**  
Hoàn thiện năng lực được định nghĩa cho milestone và mở rộng trust/evidence mà không phá Core.

**Phạm vi**
- Contracts, implementation, harness, evidence, policy boundary và documentation theo task.

**Deliverables**
- Artifact implementation + conformance tests + evidence + ADR/docs khi task yêu cầu.

**Acceptance Criteria**
- Task đạt AC; fail-closed; regression và trust gates PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-093 — Behavioral Spec + ADR-0008

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/behavioral_docs/` + `docs/behavioral_spec.md` + `docs/adr/ADR-0008.md`; **6 automated tests**; behavioral spec + ADR-0008.

**Mục tiêu**  
Hoàn thiện năng lực được định nghĩa cho milestone và mở rộng trust/evidence mà không phá Core.

**Phạm vi**
- Contracts, implementation, harness, evidence, policy boundary và documentation theo task.

**Deliverables**
- Artifact implementation + conformance tests + evidence + ADR/docs khi task yêu cầu.

**Acceptance Criteria**
- Task đạt AC; fail-closed; regression và trust gates PASS.

**Dependency / Gate**
- Theo dependency của milestone.

---

# M14

## TASK-094 — Detect + Diagnose

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/remediation_detect/`; **9 automated tests**; detect + diagnose.

**Mục tiêu**  
Hoàn thiện năng lực được định nghĩa cho milestone và mở rộng trust/evidence mà không phá Core.

**Phạm vi**
- Contracts, implementation, harness, evidence, policy boundary và documentation theo task.

**Deliverables**
- Artifact implementation + conformance tests + evidence + ADR/docs khi task yêu cầu.

**Acceptance Criteria**
- Task đạt AC; fail-closed; regression và trust gates PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-095 — Candidate Generation + Risk Scoring

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/remediation_candidate/`; **7 automated tests**; candidate generation + risk scoring.

**Mục tiêu**  
Hoàn thiện năng lực được định nghĩa cho milestone và mở rộng trust/evidence mà không phá Core.

**Phạm vi**
- Contracts, implementation, harness, evidence, policy boundary và documentation theo task.

**Deliverables**
- Artifact implementation + conformance tests + evidence + ADR/docs khi task yêu cầu.

**Acceptance Criteria**
- Task đạt AC; fail-closed; regression và trust gates PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-096 — Simulation + Meta-Verification Gate

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/remediation_simulation/`; **7 automated tests**; simulation + meta-verification gate.

**Mục tiêu**  
Hoàn thiện năng lực được định nghĩa cho milestone và mở rộng trust/evidence mà không phá Core.

**Phạm vi**
- Contracts, implementation, harness, evidence, policy boundary và documentation theo task.

**Deliverables**
- Artifact implementation + conformance tests + evidence + ADR/docs khi task yêu cầu.

**Acceptance Criteria**
- Task đạt AC; fail-closed; regression và trust gates PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-097 — Permission + Human Approval + Apply + Re-test + Rollback + Certification

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/remediation_apply/`; **6 automated tests**; permission + human approval + apply + re-test + rollback + certification.

**Mục tiêu**  
Hoàn thiện năng lực được định nghĩa cho milestone và mở rộng trust/evidence mà không phá Core.

**Phạm vi**
- Contracts, implementation, harness, evidence, policy boundary và documentation theo task.

**Deliverables**
- Artifact implementation + conformance tests + evidence + ADR/docs khi task yêu cầu.

**Acceptance Criteria**
- Task đạt AC; fail-closed; regression và trust gates PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-098 — Remediation Integrity + Kill Switch

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/remediation_integrity/`; **6 automated tests**; remediation integrity + kill switch.

**Mục tiêu**  
Hoàn thiện năng lực được định nghĩa cho milestone và mở rộng trust/evidence mà không phá Core.

**Phạm vi**
- Contracts, implementation, harness, evidence, policy boundary và documentation theo task.

**Deliverables**
- Artifact implementation + conformance tests + evidence + ADR/docs khi task yêu cầu.

**Acceptance Criteria**
- Task đạt AC; fail-closed; regression và trust gates PASS.

**Dependency / Gate**
- Theo dependency của milestone.

---

# M15

## TASK-099 — Autonomous Harness Loop

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/autonomous_harness_loop/`; **6 automated tests**; autonomous harness loop.

**Mục tiêu**  
Hoàn thiện năng lực được định nghĩa cho milestone và mở rộng trust/evidence mà không phá Core.

**Phạm vi**
- Contracts, implementation, harness, evidence, policy boundary và documentation theo task.

**Deliverables**
- Artifact implementation + conformance tests + evidence + ADR/docs khi task yêu cầu.

**Acceptance Criteria**
- Task đạt AC; fail-closed; regression và trust gates PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-100 — Failure-Corpus Improvement Engine

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/failure_corpus/`; **6 automated tests**; failure-corpus improvement engine.

**Mục tiêu**  
Hoàn thiện năng lực được định nghĩa cho milestone và mở rộng trust/evidence mà không phá Core.

**Phạm vi**
- Contracts, implementation, harness, evidence, policy boundary và documentation theo task.

**Deliverables**
- Artifact implementation + conformance tests + evidence + ADR/docs khi task yêu cầu.

**Acceptance Criteria**
- Task đạt AC; fail-closed; regression và trust gates PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-101 — Continuous Certification

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/continuous_certification/`; **6 automated tests**; continuous certification.

**Mục tiêu**  
Hoàn thiện năng lực được định nghĩa cho milestone và mở rộng trust/evidence mà không phá Core.

**Phạm vi**
- Contracts, implementation, harness, evidence, policy boundary và documentation theo task.

**Deliverables**
- Artifact implementation + conformance tests + evidence + ADR/docs khi task yêu cầu.

**Acceptance Criteria**
- Task đạt AC; fail-closed; regression và trust gates PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-102 — Trust Budget + Autonomy Levels + SAFE-STOP

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/trust_budget/`; **6 automated tests**; trust budget + autonomy levels + SAFE-STOP.

**Mục tiêu**  
Hoàn thiện năng lực được định nghĩa cho milestone và mở rộng trust/evidence mà không phá Core.

**Phạm vi**
- Contracts, implementation, harness, evidence, policy boundary và documentation theo task.

**Deliverables**
- Artifact implementation + conformance tests + evidence + ADR/docs khi task yêu cầu.

**Acceptance Criteria**
- Task đạt AC; fail-closed; regression và trust gates PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-103 — Autonomy Constitution + Audit Trail

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/autonomy_constitution/`; **6 automated tests**; autonomy constitution + audit trail.

**Mục tiêu**  
Hoàn thiện năng lực được định nghĩa cho milestone và mở rộng trust/evidence mà không phá Core.

**Phạm vi**
- Contracts, implementation, harness, evidence, policy boundary và documentation theo task.

**Deliverables**
- Artifact implementation + conformance tests + evidence + ADR/docs khi task yêu cầu.

**Acceptance Criteria**
- Task đạt AC; fail-closed; regression và trust gates PASS.

**Dependency / Gate**
- Theo dependency của milestone.

---

# M16

## TASK-104 — Independent Harness Integration Foundation

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/independent_harness/` (foundation); **6 automated tests**; independent harness integration foundation.

**Mục tiêu**  
Hoàn thiện năng lực được định nghĩa cho milestone và mở rộng trust/evidence mà không phá Core.

**Phạm vi**
- Contracts, implementation, harness, evidence, policy boundary và documentation theo task.

**Deliverables**
- Artifact implementation + conformance tests + evidence + ADR/docs khi task yêu cầu.

**Acceptance Criteria**
- Task đạt AC; fail-closed; regression và trust gates PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-105 — Independent Verification Oracle

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/independent_harness/` (oracle); **6 automated tests**; independent verification oracle, AIOS giữ policy authority.

**Mục tiêu**  
Map các invariant checkable sang independent harness oracle.

**Phạm vi**
- Bridge evidence từ independent harness vào AIOS verification; không chuyển authority khỏi AIOS policy.

**Deliverables**
- Oracle adapter + evidence mapping + conformance.

**Acceptance Criteria**
- Independent result được ghi nhận; AIOS vẫn giữ authority/policy boundary.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-106 — Behavioral Conformance Bridge

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/independent_harness/` (behavioral_bridge); **6 automated tests**; behavioral conformance bridge.

**Mục tiêu**  
Hoàn thiện năng lực được định nghĩa cho milestone và mở rộng trust/evidence mà không phá Core.

**Phạm vi**
- Contracts, implementation, harness, evidence, policy boundary và documentation theo task.

**Deliverables**
- Artifact implementation + conformance tests + evidence + ADR/docs khi task yêu cầu.

**Acceptance Criteria**
- Task đạt AC; fail-closed; regression và trust gates PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-107 — Permission + Sandbox Bridge

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/independent_harness/` (permission_sandbox_bridge); **6 automated tests**; permission + sandbox bridge.

**Mục tiêu**  
Hoàn thiện năng lực được định nghĩa cho milestone và mở rộng trust/evidence mà không phá Core.

**Phạm vi**
- Contracts, implementation, harness, evidence, policy boundary và documentation theo task.

**Deliverables**
- Artifact implementation + conformance tests + evidence + ADR/docs khi task yêu cầu.

**Acceptance Criteria**
- Task đạt AC; fail-closed; regression và trust gates PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-108 — Management Console / Independent Harness Integration

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/independent_harness/` (console) + `aios/api/routers/independent_harness.py` + Dashboard View 11; **5 automated tests**; management console integration.

**Mục tiêu**  
Hoàn thiện năng lực được định nghĩa cho milestone và mở rộng trust/evidence mà không phá Core.

**Phạm vi**
- Contracts, implementation, harness, evidence, policy boundary và documentation theo task.

**Deliverables**
- Artifact implementation + conformance tests + evidence + ADR/docs khi task yêu cầu.

**Acceptance Criteria**
- Task đạt AC; fail-closed; regression và trust gates PASS.

**Dependency / Gate**
- Theo dependency của milestone.

---

# M17

## TASK-109 — Model Contracts

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/model_runtime/contracts`; **6 automated tests**; model contracts, vendor-neutral, deterministic-first.

**Mục tiêu**  
Triển khai model contracts như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Model Contracts implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-110 — Provider Registry + Lifecycle

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/model_runtime/provider_registry`; **6 automated tests**; provider registry + lifecycle.

**Mục tiêu**  
Triển khai provider registry + lifecycle như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Provider Registry + Lifecycle implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-111 — Model Registry + Deterministic Resolver

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/model_runtime/model_registry`; **6 automated tests**; model registry + deterministic resolver.

**Mục tiêu**  
Triển khai model registry + deterministic resolver như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Model Registry + Deterministic Resolver implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-112 — Inference Runtime Orchestration

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/model_runtime/orchestration`; **4 automated tests**; inference runtime orchestration, no LLM in resolver.

**Mục tiêu**  
Triển khai inference runtime orchestration như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Inference Runtime Orchestration implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-113 — Credential + Permission + Policy Integration

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/model_runtime/security`; **6 automated tests**; credential + permission + policy integration (tích hợp T035/T040/T049).

**Mục tiêu**  
Triển khai credential + permission + policy integration như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Credential + Permission + Policy Integration implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-114 — Retry / Timeout / Streaming / Cancellation

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/model_runtime/resilience`; **6 automated tests**; retry/timeout/streaming/cancellation.

**Mục tiêu**  
Triển khai retry / timeout / streaming / cancellation như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Retry / Timeout / Streaming / Cancellation implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-115 — Usage / Cost / Audit / Evidence

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/model_runtime/usage`; **5 automated tests**; usage/cost/audit/evidence.

**Mục tiêu**  
Triển khai usage / cost / audit / evidence như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Usage / Cost / Audit / Evidence implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-116 — Provider Conformance + Certification

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/model_runtime/conformance`; **6 automated tests**; provider conformance + certification.

**Mục tiêu**  
Triển khai provider conformance + certification như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Provider Conformance + Certification implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

---

# M18

## TASK-117 — Repository Scanner

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/context/scanner`; **6 automated tests**; repository scanner, deterministic-first.

**Mục tiêu**  
Triển khai repository scanner như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Repository Scanner implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-118 — Source / Symbol Index

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/context/symbol_index`; **6 automated tests**; source/symbol index.

**Mục tiêu**  
Triển khai source / symbol index như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Source / Symbol Index implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-119 — Dependency Graph

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/context/dependency_graph`; **6 automated tests**; dependency graph.

**Mục tiêu**  
Triển khai dependency graph như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Dependency Graph implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-120 — Semantic + Hybrid Index

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/context/hybrid_index`; **6 automated tests**; semantic + hybrid index.

**Mục tiêu**  
Triển khai semantic + hybrid index như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Semantic + Hybrid Index implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-121 — Context Retriever

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/context/retriever`; **6 automated tests**; context retriever.

**Mục tiêu**  
Triển khai context retriever như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Context Retriever implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-122 — Context Builder + Budget

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/context/builder`; **6 automated tests**; context builder + budget.

**Mục tiêu**  
Triển khai context builder + budget như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Context Builder + Budget implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-123 — Context Verification + Evidence

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/context/verification`; **6 automated tests**; context verification + evidence.

**Mục tiêu**  
Triển khai context verification + evidence như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Context Verification + Evidence implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-124 — Context Harness + Conformance

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/context/conformance`; **6 automated tests**; context harness + conformance.

**Mục tiêu**  
Triển khai context harness + conformance như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Context Harness + Conformance implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

---

# M19

## TASK-125 — Coder Agent Contract + State Machine

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/coder/contract` (CoderAgentContract + CoderAgentStateMachine); **12 automated tests**; deterministic-first, fail-closed, provenance mọi transition.

**Mục tiêu**  
Triển khai coder agent contract + state machine như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Coder Agent Contract + State Machine implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-126 — Coding Planner + PlanVerifier

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/coder/planner` (CodingPlanner + PlanVerifier); **9 automated tests**; rule trước LLM (llm_call_count=0), fail-closed verify.

**Mục tiêu**  
Triển khai coding planner + planverifier như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Coding Planner + PlanVerifier implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-127 — Code Generation Runtime

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/coder/generation` (CodeGenerationRuntime); **7 automated tests**; capability dispatch (ARCH-004), artifact hash, provenance, deterministic + fail-closed.

**Mục tiêu**  
Triển khai code generation runtime như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Code Generation Runtime implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-128 — Patch Engine

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/coder/patch` (diff/apply); **8 automated tests**; backup-before-apply (T020), rollback-to-certified, fail-closed, deterministic diff.

**Mục tiêu**  
Triển khai patch engine như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Patch Engine implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-129 — Code Review Agent

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/coder/review` (CodeReviewAgent); **8 automated tests**; I/O-free, capability-injected, fail-closed verdict, no God Object.

**Mục tiêu**  
Triển khai code review agent như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Code Review Agent implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-130 — Coding Artifact + CodingEvidence

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/coder/artifact` (CodingArtifact + CodingEvidence); **8 automated tests**; 3-kind artifact (T078 hash), provenance chain, fail-closed integrity, immutable id. **M19 COMPLETE** (T125-T130, 52 new tests).

**Mục tiêu**  
Triển khai coding artifact + codingevidence như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Coding Artifact + CodingEvidence implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-131 — Coder Conformance Harness + Security

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/coder/conformance` (CoderConformanceHarness); **9 automated tests**; fail-closed invariants, UNKNOWN never promoted, security boundary.

**Mục tiêu**  
Triển khai coder conformance harness + security như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Coder Conformance Harness + Security implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-132 — Autonomy Level + Permission Integration

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/coder/autonomy` (AutonomyPermissionBroker); **9 automated tests**; 3-level mapping, fail-closed permission.

**Mục tiêu**  
Triển khai autonomy level + permission integration như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Autonomy Level + Permission Integration implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-133 — Prompt Architecture + PromptBuilder + Versioning

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/coder/prompt` (PromptRegistry + PromptBuilder); **9 automated tests**; immutable versioning, fail-closed build, provenance.

**Mục tiêu**  
Triển khai prompt architecture + promptbuilder + versioning như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Prompt Architecture + PromptBuilder + Versioning implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-134 — File Safety Boundary + Scope Enforcement

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/coder/filesafety` (FileSafetyBoundary); **8 automated tests**; scope root enforcement, fail-closed escape rejection. **M19 COMPLETE** (T125-T134, 88 new tests).

**Mục tiêu**  
Triển khai file safety boundary + scope enforcement như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- File Safety Boundary + Scope Enforcement implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

---

# M20

## TASK-135 — Execution Contract

> **Trạng thái thực tế (2026-08-23):** PLANNED — chưa triển khai (thuộc 85 tasks remaining M20–M26, xem `aios/progress/PLAN.md`).

**Mục tiêu**  
Triển khai execution contract như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Execution Contract implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-136 — Sandbox Manager

> **Trạng thái thực tế (2026-08-23):** PLANNED — chưa triển khai.

**Mục tiêu**  
Triển khai sandbox manager như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Sandbox Manager implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-137 — Workspace / Snapshot Manager

> **Trạng thái thực tế (2026-08-23):** PLANNED — chưa triển khai.

**Mục tiêu**  
Triển khai workspace / snapshot manager như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Workspace / Snapshot Manager implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-138 — Resource + Network + Command Policy

> **Trạng thái thực tế (2026-08-23):** PLANNED — chưa triển khai.

**Mục tiêu**  
Triển khai resource + network + command policy như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Resource + Network + Command Policy implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-139 — Test Runner

> **Trạng thái thực tế (2026-08-23):** PLANNED — chưa triển khai.

**Mục tiêu**  
Triển khai test runner như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Test Runner implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-140 — Build / Lint Runner

> **Trạng thái thực tế (2026-08-23):** PLANNED — chưa triển khai.

**Mục tiêu**  
Triển khai build / lint runner như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Build / Lint Runner implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-141 — Output + Artifact Collector

> **Trạng thái thực tế (2026-08-23):** PLANNED — chưa triển khai.

**Mục tiêu**  
Triển khai output + artifact collector như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Output + Artifact Collector implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-142 — Verification Engine

> **Trạng thái thực tế (2026-08-23):** PLANNED — chưa triển khai.

**Mục tiêu**  
Triển khai verification engine như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Verification Engine implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-143 — Security + Replay Harness

> **Trạng thái thực tế (2026-08-23):** PLANNED — chưa triển khai.

**Mục tiêu**  
Triển khai security + replay harness như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Security + Replay Harness implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-144 — Execution Evidence + Conformance

> **Trạng thái thực tế (2026-08-23):** PLANNED — chưa triển khai.

**Mục tiêu**  
Triển khai execution evidence + conformance như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Execution Evidence + Conformance implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

---

# M21

## TASK-145 — Coding Loop State Machine

> **Trạng thái thực tế (2026-08-23):** PLANNED — chưa triển khai.

**Mục tiêu**  
Triển khai coding loop state machine như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Coding Loop State Machine implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-146 — Execution Observation

> **Trạng thái thực tế (2026-08-23):** PLANNED — chưa triển khai.

**Mục tiêu**  
Triển khai execution observation như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Execution Observation implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-147 — Failure Classification

> **Trạng thái thực tế (2026-08-23):** PLANNED — chưa triển khai.

**Mục tiêu**  
Triển khai failure classification như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Failure Classification implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-148 — Diagnostic Agent

> **Trạng thái thực tế (2026-08-23):** PLANNED — chưa triển khai.

**Mục tiêu**  
Triển khai diagnostic agent như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Diagnostic Agent implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-149 — Repair Planner

> **Trạng thái thực tế (2026-08-23):** PLANNED — chưa triển khai.

**Mục tiêu**  
Triển khai repair planner như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Repair Planner implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-150 — Progress + Regression Detection

> **Trạng thái thực tế (2026-08-23):** PLANNED — chưa triển khai.

**Mục tiêu**  
Triển khai progress + regression detection như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Progress + Regression Detection implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-151 — Verification Gate

> **Trạng thái thực tế (2026-08-23):** PLANNED — chưa triển khai.

**Mục tiêu**  
Triển khai verification gate như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Verification Gate implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-152 — Context Refresh + Patch Chain

> **Trạng thái thực tế (2026-08-23):** PLANNED — chưa triển khai.

**Mục tiêu**  
Triển khai context refresh + patch chain như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Context Refresh + Patch Chain implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-153 — Autonomous Safety Controller

> **Trạng thái thực tế (2026-08-23):** PLANNED — chưa triển khai.

**Mục tiêu**  
Triển khai autonomous safety controller như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Autonomous Safety Controller implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-154 — Autonomous Coding Harness

> **Trạng thái thực tế (2026-08-23):** PLANNED — chưa triển khai.

**Mục tiêu**  
Triển khai autonomous coding harness như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Autonomous Coding Harness implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

---

# M22

## TASK-155 — Requirement → Evidence Mapping

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/verification/requirement_evidence.py` (RequirementEvidenceMapper); **7 automated tests**; fail-closed PASS (Unified Gate AND 7 rules).

**Mục tiêu**  
Triển khai requirement → evidence mapping như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Requirement → Evidence Mapping implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-156 — Test Adequacy Analyzer + Mutation Verifier

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/verification/test_adequacy.py` (TestAdequacyAnalyzer); **7 automated tests**; fail-closed PASS (Unified Gate AND 7 rules).

**Mục tiêu**  
Triển khai test adequacy analyzer + mutation verifier như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Test Adequacy Analyzer + Mutation Verifier implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-157 — Behavioral Verifier

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/verification/behavioral.py` (BehavioralVerifier); **7 automated tests**; fail-closed PASS (Unified Gate AND 7 rules).

**Mục tiêu**  
Triển khai behavioral verifier như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Behavioral Verifier implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-158 — Contract Verifier

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/verification/contract.py` (ContractVerifier); **7 automated tests**; fail-closed PASS (Unified Gate AND 7 rules).

**Mục tiêu**  
Triển khai contract verifier như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Contract Verifier implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-159 — Regression Verifier

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/verification/regression.py` (RegressionVerifier); **7 automated tests**; fail-closed PASS (Unified Gate AND 7 rules).

**Mục tiêu**  
Triển khai regression verifier như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Regression Verifier implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-160 — Security Verifier

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/verification/security.py` (SecurityVerifier); **7 automated tests**; fail-closed PASS (Unified Gate AND 7 rules).

**Mục tiêu**  
Triển khai security verifier như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Security Verifier implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-161 — Performance Verifier

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/verification/performance.py` (PerformanceVerifier); **7 automated tests**; fail-closed PASS (Unified Gate AND 7 rules).

**Mục tiêu**  
Triển khai performance verifier như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Performance Verifier implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-162 — Replay & Flaky Detector

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/verification/replay_flaky.py` (ReplayFlakyDetector); **7 automated tests**; fail-closed PASS (Unified Gate AND 7 rules).

**Mục tiêu**  
Triển khai replay & flaky detector như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Replay & Flaky Detector implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-163 — Evidence Collector + Evidence Integrity

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/verification/evidence_collector.py` (EvidenceCollector); **7 automated tests**; fail-closed PASS (Unified Gate AND 7 rules).

**Mục tiêu**  
Triển khai evidence collector + evidence integrity như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Evidence Collector + Evidence Integrity implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-164 — Trust Evaluator + CodingCertificate + Verification Harness

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/verification/trust_certificate.py` (VerificationHarness); **7 automated tests**; fail-closed PASS (Unified Gate AND 7 rules).

**Mục tiêu**  
Triển khai trust evaluator + codingcertificate + verification harness như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Trust Evaluator + CodingCertificate + Verification Harness implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

---

# M23

## TASK-165 — Adversarial Evaluation Harness

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/adversarial/adversarial_evaluation.py` (AdversarialEvaluationHarness); **7 automated tests**; fail-closed PASS (Unified Gate AND 7 rules).

**Mục tiêu**  
Triển khai adversarial evaluation harness như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Adversarial Evaluation Harness implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-166 — Evidence Attackers

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/adversarial/evidence_attackers.py` (EvidenceAttacker); **7 automated tests**; fail-closed PASS (Unified Gate AND 7 rules).

**Mục tiêu**  
Triển khai evidence attackers như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Evidence Attackers implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-167 — Test Weakness Attackers

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/adversarial/test_weakness_attackers.py` (TestWeaknessAttacker); **7 automated tests**; fail-closed PASS (Unified Gate AND 7 rules).

**Mục tiêu**  
Triển khai test weakness attackers như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Test Weakness Attackers implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-168 — Requirement / Scope Attackers

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/adversarial/requirement_scope_attackers.py` (RequirementScopeAttacker); **7 automated tests**; fail-closed PASS (Unified Gate AND 7 rules).

**Mục tiêu**  
Triển khai requirement / scope attackers như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Requirement / Scope Attackers implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-169 — Certificate Attackers

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/adversarial/certificate_attackers.py` (CertificateAttacker); **7 automated tests**; fail-closed PASS (Unified Gate AND 7 rules).

**Mục tiêu**  
Triển khai certificate attackers như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Certificate Attackers implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-170 — Prompt Injection Tester + Untrusted Artifact Isolation

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/adversarial/prompt_injection.py` (PromptInjectionTester/UntrustedArtifactIsolation); **7 automated tests**; fail-closed PASS (Unified Gate AND 7 rules).

**Mục tiêu**  
Triển khai prompt injection tester + untrusted artifact isolation như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Prompt Injection Tester + Untrusted Artifact Isolation implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-171 — Execution Integrity Attackers

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/adversarial/execution_integrity_attackers.py` (ExecutionIntegrityAttacker); **7 automated tests**; fail-closed PASS (Unified Gate AND 7 rules).

**Mục tiêu**  
Triển khai execution integrity attackers như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Execution Integrity Attackers implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-172 — Environment / Dependency Attackers

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/adversarial/environment_dependency_attackers.py` (EnvironmentDependencyAttacker); **7 automated tests**; fail-closed PASS (Unified Gate AND 7 rules).

**Mục tiêu**  
Triển khai environment / dependency attackers như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Environment / Dependency Attackers implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-173 — Boundary Attackers

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/adversarial/boundary_attackers.py` (BoundaryAttacker); **7 automated tests**; fail-closed PASS (Unified Gate AND 7 rules).

**Mục tiêu**  
Triển khai boundary attackers như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Boundary Attackers implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-174 — Collusion Detector + Resilience Score + Attack Corpus Regression

> **Trạng thái thực tế (2026-08-23):** DONE — `aios/adversarial/collusion_detector.py` (CollusionDetector); **7 automated tests**; fail-closed PASS (Unified Gate AND 7 rules).

**Mục tiêu**  
Triển khai collusion detector + resilience score + attack corpus regression như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Collusion Detector + Resilience Score + Attack Corpus Regression implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

---

# M24

## TASK-175 — Quality Gate + Gate States

> **Trạng thái thực tế (2026-08-23):** DONE — đã triển khai (2026-08-23).

**Mục tiêu**  
Triển khai quality gate + gate states như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Quality Gate + Gate States implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-176 — Risk Model + Classification

> **Trạng thái thực tế (2026-08-23):** DONE — đã triển khai (2026-08-23).

**Mục tiêu**  
Triển khai risk model + classification như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Risk Model + Classification implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-177 — Policy Engine + Profiles + Precedence

> **Trạng thái thực tế (2026-08-23):** DONE — đã triển khai (2026-08-23).

**Mục tiêu**  
Triển khai policy engine + profiles + precedence như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Policy Engine + Profiles + Precedence implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-178 — Exception Management

> **Trạng thái thực tế (2026-08-23):** DONE — đã triển khai (2026-08-23).

**Mục tiêu**  
Triển khai exception management như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Exception Management implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-179 — Quality Debt Tracking

> **Trạng thái thực tế (2026-08-23):** DONE — đã triển khai (2026-08-23).

**Mục tiêu**  
Triển khai quality debt tracking như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Quality Debt Tracking implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-180 — Release Gate + Decision Explainability

> **Trạng thái thực tế (2026-08-23):** DONE — đã triển khai (2026-08-23).

**Mục tiêu**  
Triển khai release gate + decision explainability như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Release Gate + Decision Explainability implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-181 — Governance Ledger + Provenance Graph

> **Trạng thái thực tế (2026-08-23):** DONE — đã triển khai (2026-08-23).

**Mục tiêu**  
Triển khai governance ledger + provenance graph như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Governance Ledger + Provenance Graph implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-182 — Trust Lifecycle + Invalidation + Selective Reverification

> **Trạng thái thực tế (2026-08-23):** DONE — đã triển khai (2026-08-23).

**Mục tiêu**  
Triển khai trust lifecycle + invalidation + selective reverification như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Trust Lifecycle + Invalidation + Selective Reverification implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-183 — Approval Workflow + Rollback Recommendation

> **Trạng thái thực tế (2026-08-23):** DONE — đã triển khai (2026-08-23).

**Mục tiêu**  
Triển khai approval workflow + rollback recommendation như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Approval Workflow + Rollback Recommendation implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-184 — Quality Dashboard + Governance Harness

> **Trạng thái thực tế (2026-08-23):** DONE — đã triển khai (2026-08-23).

**Mục tiêu**  
Triển khai quality dashboard + governance harness như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Quality Dashboard + Governance Harness implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

---

# M25

## TASK-185 — Coding Evaluation Contract

> **Trạng thái thực tế (2026-08-23):** DONE — đã triển khai (2026-08-23).

**Mục tiêu**  
Triển khai coding evaluation contract như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Coding Evaluation Contract implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-186 — Evaluation Engine

> **Trạng thái thực tế (2026-08-23):** DONE — đã triển khai (2026-08-23).

**Mục tiêu**  
Triển khai evaluation engine như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Evaluation Engine implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-187 — Quality Dimensions

> **Trạng thái thực tế (2026-08-23):** DONE — đã triển khai (2026-08-23).

**Mục tiêu**  
Triển khai quality dimensions như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Quality Dimensions implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-188 — Benchmark Registry

> **Trạng thái thực tế (2026-08-23):** DONE — đã triển khai (2026-08-23).

**Mục tiêu**  
Triển khai benchmark registry như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Benchmark Registry implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-189 — Baseline Manager

> **Trạng thái thực tế (2026-08-23):** DONE — đã triển khai (2026-08-23).

**Mục tiêu**  
Triển khai baseline manager như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Baseline Manager implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-190 — Regression Detector

> **Trạng thái thực tế (2026-08-23):** DONE — đã triển khai (2026-08-23).

**Mục tiêu**  
Triển khai regression detector như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Regression Detector implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-191 — Agent Behavior Evaluator

> **Trạng thái thực tế (2026-08-23):** DONE — đã triển khai (2026-08-23).

**Mục tiêu**  
Triển khai agent behavior evaluator như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Agent Behavior Evaluator implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-192 — Efficiency Evaluator

> **Trạng thái thực tế (2026-08-23):** DONE — đã triển khai (2026-08-23).

**Mục tiêu**  
Triển khai efficiency evaluator như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Efficiency Evaluator implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-193 — Failure Attribution

> **Trạng thái thực tế (2026-08-23):** DONE — đã triển khai (2026-08-23).

**Mục tiêu**  
Triển khai failure attribution như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Failure Attribution implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-194 — Evaluation Store

> **Trạng thái thực tế (2026-08-23):** DONE — đã triển khai (2026-08-23).

**Mục tiêu**  
Triển khai evaluation store như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Evaluation Store implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-195 — Model / Agent Benchmark

> **Trạng thái thực tế (2026-08-23):** DONE — đã triển khai (2026-08-23).

**Mục tiêu**  
Triển khai model / agent benchmark như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Model / Agent Benchmark implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-196 — Continuous Evaluation

> **Trạng thái thực tế (2026-08-23):** DONE — đã triển khai (2026-08-23).

**Mục tiêu**  
Triển khai continuous evaluation như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Continuous Evaluation implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

---

# M26

## TASK-197 — Unified Coding Contract

> **Trạng thái thực tế (2026-08-23):** PLANNED — chưa triển khai.

**Mục tiêu**  
Triển khai unified coding contract như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Unified Coding Contract implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-198 — Coding State Machine

> **Trạng thái thực tế (2026-08-23):** PLANNED — chưa triển khai.

**Mục tiêu**  
Triển khai coding state machine như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Coding State Machine implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-199 — Coding Policy Engine

> **Trạng thái thực tế (2026-08-23):** PLANNED — chưa triển khai.

**Mục tiêu**  
Triển khai coding policy engine như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Coding Policy Engine implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-200 — Risk Engine

> **Trạng thái thực tế (2026-08-23):** PLANNED — chưa triển khai.

**Mục tiêu**  
Triển khai risk engine như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Risk Engine implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-201 — Approval Gate

> **Trạng thái thực tế (2026-08-23):** PLANNED — chưa triển khai.

**Mục tiêu**  
Triển khai approval gate như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Approval Gate implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-202 — Autonomous Guardrails

> **Trạng thái thực tế (2026-08-23):** PLANNED — chưa triển khai.

**Mục tiêu**  
Triển khai autonomous guardrails như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Autonomous Guardrails implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-203 — Safe Stop / Resume

> **Trạng thái thực tế (2026-08-23):** PLANNED — chưa triển khai.

**Mục tiêu**  
Triển khai safe stop / resume như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Safe Stop / Resume implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-204 — Recovery Orchestrator

> **Trạng thái thực tế (2026-08-23):** PLANNED — chưa triển khai.

**Mục tiêu**  
Triển khai recovery orchestrator như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Recovery Orchestrator implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-205 — Artifact Lineage

> **Trạng thái thực tế (2026-08-23):** PLANNED — chưa triển khai.

**Mục tiêu**  
Triển khai artifact lineage như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Artifact Lineage implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-206 — Coding Session

> **Trạng thái thực tế (2026-08-23):** PLANNED — chưa triển khai.

**Mục tiêu**  
Triển khai coding session như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Coding Session implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-207 — Session Fork

> **Trạng thái thực tế (2026-08-23):** PLANNED — chưa triển khai.

**Mục tiêu**  
Triển khai session fork như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Session Fork implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-208 — Multi-Agent Coding

> **Trạng thái thực tế (2026-08-23):** PLANNED — chưa triển khai.

**Mục tiêu**  
Triển khai multi-agent coding như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Multi-Agent Coding implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-209 — Parallel Coding

> **Trạng thái thực tế (2026-08-23):** PLANNED — chưa triển khai.

**Mục tiêu**  
Triển khai parallel coding như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Parallel Coding implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-210 — Change Impact Analysis

> **Trạng thái thực tế (2026-08-23):** PLANNED — chưa triển khai.

**Mục tiêu**  
Triển khai change impact analysis như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Change Impact Analysis implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-211 — Repository Knowledge Graph Integration

> **Trạng thái thực tế (2026-08-23):** PLANNED — chưa triển khai.

**Mục tiêu**  
Triển khai repository knowledge graph integration như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Repository Knowledge Graph Integration implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-212 — Coding Doctor

> **Trạng thái thực tế (2026-08-23):** PLANNED — chưa triển khai.

**Mục tiêu**  
Triển khai coding doctor như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Coding Doctor implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-213 — Coding Health Score

> **Trạng thái thực tế (2026-08-23):** PLANNED — chưa triển khai.

**Mục tiêu**  
Triển khai coding health score như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Coding Health Score implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-214 — Release Gate

> **Trạng thái thực tế (2026-08-23):** PLANNED — chưa triển khai.

**Mục tiêu**  
Triển khai release gate như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Release Gate implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-215 — Coding Certification

> **Trạng thái thực tế (2026-08-23):** PLANNED — chưa triển khai.

**Mục tiêu**  
Triển khai coding certification như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Coding Certification implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-216 — Benchmark Gate

> **Trạng thái thực tế (2026-08-23):** PLANNED — chưa triển khai.

**Mục tiêu**  
Triển khai benchmark gate như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Benchmark Gate implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-217 — AIOS 2.0 Coding Integration

> **Trạng thái thực tế (2026-08-23):** PLANNED — chưa triển khai.

**Mục tiêu**  
Triển khai aios 2.0 coding integration như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- AIOS 2.0 Coding Integration implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

## TASK-218 — Full M0–M26 Regression

> **Trạng thái thực tế (2026-08-23):** PLANNED — chưa triển khai (task cuối đóng toàn bộ roadmap).

**Mục tiêu**  
Triển khai full m0–m26 regression như một năng lực có contract, evidence và harness riêng.

**Phạm vi**
- API/schema; implementation; policy boundary; persistence/artifact khi cần; deterministic tests; integration với các task phụ thuộc.

**Deliverables**
- Full M0–M26 Regression implementation + contract/schema + tests + evidence + documentation.

**Acceptance Criteria**
- AC của task PASS; UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

**Dependency / Gate**
- Theo dependency của milestone.

---

# 4. Chuỗi năng lực M0–M26

```text
Governance → Runtime → Orchestrator → Desktop → Platform
→ Intelligence → Harness → Enterprise → Ecosystem → Autonomy
→ AIOS 1.0 → Deterministic Artifact → Compatibility
→ Harness Trust → Controlled Healing → Autonomous Harness
→ Independent Harness → Inference → Repository Context
→ Coder → Sandbox → Autonomous Coding Loop
→ Independent Verification → Adversarial Resilience
→ Quality Governance → Coding Evaluation → AIOS 2.0 Coding Edition
```

## 5. Coding Completion Contract

```text
AUTHORIZED
AND EXECUTED
AND VERIFIED
AND RESILIENT
AND GOVERNED
AND EVALUATED
AND CERTIFIED
```

Không coi coding task là hoàn thành chỉ vì agent dừng hoặc code chạy được.
