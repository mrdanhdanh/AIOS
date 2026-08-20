# TASK-009 — Critique 1 (Spec Review)

## Strengths
- Spec phân tách rõ 4 trụ cột: Capability Registry / Prompt Registry / System Catalog / Knowledge Graph v1, mỗi trụ cột có contract, API, fail-closed và metadata/provenance riêng.
- Capability-First được diễn đạt đúng nguyên tắc: Agent → Capability → Registry/Router → Tool; Tool tự khai báo capability; một capability map nhiều tool.
- Prompt dùng `str.format` subset + `{identifier}` + version, tránh Jinja2 ở M1 — phù hợp deterministic-first, offline-first.
- Graph v1 giới hạn in-memory + manual theo amendment — scoped chính xác, không scope-creep sang SQLite/auto-build.

## Risks / Gaps
- Cần làm rõ `CapabilityContract.resources` validate (`cpu>0`, `memory` regex) giống WorkflowResource để fail-closed đồng nhất.
- `CapabilityRegistry.resolve` cần định nghĩa deterministic tie-break khi nhiều tool healthy (priority → registration order) và `health` field để Router M2 dùng.
- Prompt `variables` nên suy ra từ template (regex `{identifier}`) và validate missing/extra var trước render.
- Catalog và Graph cần ghi rõ `source`/`provenance` field để AC-009-09 có thể test UNKNOWN không thành confirmed.
- Kernel wiring phải đảm bảo 4 singletons không tạo circular dependency (capability không import runtime).

## Required revisions
- [x] Bổ sung validate chi tiết cho resources/permissions trong CapabilityContract.
- [x] Định nghĩa rõ `register_tool(capability_id, tool_id, priority/health)` và `resolve(capability_id) → [tool_id]`.
- [x] Prompt render: extract variables, fail khi thiếu, không silent.
- [x] CatalogEntry/GraphNode/GraphEdge bắt buộc `provenance` hoặc `source`, test reject khi thiếu.
- [x] Ghi chú layering: `aios/capability` chỉ import `tool`/`unknown`, `runtime.kernel` import `capability` downward.
