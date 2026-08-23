# AIOS — Master Task Specification

## Runtime-First · Plugin-First · Offline-First · Harness-Verified · Coding-Plane

> **Trạng thái tài liệu:** CLEAN ROADMAP — không giả định task nào đã hoàn thành.
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

# M12

## TASK-084 — Version + Compatibility Baseline

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
