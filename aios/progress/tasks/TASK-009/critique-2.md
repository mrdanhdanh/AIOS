# TASK-009 — Critique 2 (Scope & Risk)

## Strengths
- Phân biệt rõ Capability vs Tool, Prompt vs rendering, Catalog (index) vs Registry (owner), Graph (relationship) vs Catalog (search).
- M1 boundaries rõ: không SQLite/auto-build/reasoning/Jinja2/vector DB; giữ implementation thuần in-memory + deterministic.

## Risks / Gaps
- Nếu `capability` và `runtime` cùng import nhau sẽ vi phạm ARCH-004; phải giữ `capability` không import `runtime`.
- Graph `find_path` cần deterministic BFS (queue ordered) để test ổn định.
- Catalog `search` cần lower-case, token substring, không dùng embedding.
- Thread-safety phải dùng `RLock` như Memory/Knowledge (đã chứng minh).
- Evidence/provenance: mỗi object cần `source` hoặc `provenance` để chain Evidence → Artifact → Task.

## Required revisions
- [x] Đảm bảo mọi module trong `aios/capability/` chỉ import stdlib + `aios.core`.
- [x] `find_path` BFS deterministic, tie-break theo node_id.
- [x] `search` deterministic trên lowercased `id/type/tags/description`.
- [x] Thêm `RLock` cho mọi registry/catalog/graph.
- [x] Provenance fields bắt buộc hoặc optional nhưng test AC-009-09 kiểm tra `source`/`provenance` tồn tại.
