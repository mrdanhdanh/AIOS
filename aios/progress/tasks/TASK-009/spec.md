# TASK-009 — Capability Foundation

## Objective
Xây nền móng cho mô hình Capability-First của AIOS: Agent chỉ nhìn thấy Capability abstraction, mọi Tool implementation được chọn qua Registry/Router. Đồng thời tạo metadata foundation gồm Prompt Registry (version + deterministic template), System Catalog (index + search trên metadata của mọi registry) và Knowledge Graph v1 (in-memory, manual, biểu diễn quan hệ Agent/Skill/Workflow/Capability/Tool/Artifact/Model/Prompt) để Orchestrator/M2 có thể discover, search và biết relationship mà không hard-code Agent→Tool.

## Scope
- **Capability** (`aios/capability/capability.py`): `CapabilityContract` (id, version, description, permissions, resources, tags, provenance), `CapabilityRegistry` (register/get/list/find/remove/resolve, nhiều tool trên một capability, discovery mapping, health/availability, thread-safe, fail-closed), provider/tool mappings via `register_tool`.
- **Prompt** (`aios/capability/prompt.py`): `PromptContract` (prompt_id, version, template, variables `{identifier}`, metadata, created_at/updated_at, render deterministic qua `str.format` subset), `PromptRegistry` (register/get/version lookup/list, duplicate reject, missing variable fail-closed).
- **System Catalog** (`aios/capability/catalog.py`): `CatalogEntry` + `SystemCatalog` (index metadata từ mọi registry, search(query), find_by_id/type/tag, provenance, thread-safe, deterministic).
- **Knowledge Graph v1** (`aios/capability/graph.py`): `GraphNode`/`GraphEdge` + `KnowledgeGraph` (in-memory, manual `add_node`/`add_edge`, `neighbors`/`find_path`, 8 node types, 5+ edge types, reject duplicate/missing/invalid, không SQLite, không auto-build, không LLM).
- **Kernel wiring** (`aios/runtime/kernel.py`): đăng ký 4 stores làm SINGLETON, expose accessors, mở rộng `health()`.
- **Out of scope**: graph persistence/SQLite, automatic event-driven builder, reasoning engine, Jinja2, vector embeddings, capability router đầy đủ (để TASK-014).

## Deliverables
- `aios/capability/__init__.py` — public re-exports + package doc.
- `aios/capability/contracts.py` — `CAPABILITY_CONTRACT`, `PROMPT_CONTRACT`, `CATALOG_CONTRACT`, `GRAPH_CONTRACT`.
- `aios/capability/capability.py` — `CapabilityError`, `CapabilityContract`, `CapabilityRegistry`.
- `aios/capability/prompt.py` — `PromptError`, `PromptContract`, `PromptRegistry`.
- `aios/capability/catalog.py` — `CatalogError`, `CatalogEntry`, `SystemCatalog`.
- `aios/capability/graph.py` — `GraphError`, `NodeType`, `EdgeType`, `GraphNode`, `GraphEdge`, `KnowledgeGraph`.
- `aios/runtime/kernel.py` — wire 4 singletons + health.
- `aios/runtime/__init__.py` — re-export capability API (optional, giữ layering).
- Tests: `aios/capability/tests/test_capability.py`, `test_prompt.py`, `test_catalog.py`, `test_graph.py`, `test_capability_architecture.py`, `test_kernel_wiring.py`.

## Acceptance Criteria
1. **AC-009-01 — Capability Registry**: `register → resolve → inspect → list` thành công mà không biết tool implementation (test PASS).
2. **AC-009-02 — Multiple tools**: một capability (`execute_code`) map tới nhiều tool (`PythonTool`, `DockerTool`) (test PASS).
3. **AC-009-03 — Agent boundary**: Agent chỉ đi qua capability; direct Agent→Tool import bị architecture test phát hiện (test PASS, ARCH-004).
4. **AC-009-04 — Prompt version**: đăng ký và resolve `prompt_id + version` (test PASS).
5. **AC-009-05 — Prompt rendering**: `"Review {file}"` với `file=main.py` render đúng; missing variable fail rõ ràng (test PASS).
6. **AC-009-06 — Catalog index**: index và search theo id/type/tag/query (test PASS).
7. **AC-009-07 — Graph**: tạo `Agent --USES--> Capability --IMPLEMENTED_BY--> Tool` và truy vấn (test PASS).
8. **AC-009-08 — Graph boundary**: in-memory, manual, deterministic, không SQLite/LLM/auto-scan (test PASS).
9. **AC-009-09 — Provenance**: metadata trong Catalog/Graph giữ source/provenance, không nâng UNKNOWN thành confirmed (test PASS).
10. **AC-009-10 — Fail closed**: invalid capability/prompt/catalog/graph bị REJECT (test PASS); `python -m pytest aios -q` xanh; regression TASK-003..008 PASS; `capability` layer không import `runtime`.

## Dependencies
- TASK-003 Kernel Foundations (DONE) — `Container`, `SemVer`, `EventBus` patterns.
- TASK-006 Model Registry metadata và TASK-007 Memory/Knowledge chỉ là nguồn metadata cho Catalog, không hard dependency.

## Governance references
- Rule 1..7 via `aios/governance/*`. Layering `capability` — chỉ import `tool`/`unknown`; `runtime` wire `capability` (downward). Deterministic-first: mọi registry/graph/catalog thuần Python, không LLM.

## Notes
- Offline-first, in-memory, thuần Python + stdlib + `aios.core`.
- M1 cố ý KHÔNG làm: SQLite persistence, auto-build từ event bus, distributed graph, Jinja2 (str.format subset đủ).
