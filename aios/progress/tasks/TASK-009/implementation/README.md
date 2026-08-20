# TASK-009 — Implementation Notes

## Modules
- `aios/capability/contracts.py` — 4 contracts (capability/prompt/catalog/graph) version 1.0.0, `check_capability_contracts`.
- `aios/capability/capability.py` — `CapabilityContract` + `CapabilityRegistry` (RLock, validate, register/get/list/find/remove, register_tool health/priority, resolve deterministic).
- `aios/capability/prompt.py` — `PromptContract` + `PromptRegistry` ((prompt_id, version) key, `{identifier}` placeholders, render fail-closed, `versions`/`render` helpers).
- `aios/capability/catalog.py` — `CatalogEntry` + `SystemCatalog` (index/upsert/remove, search/find_by_id/type/tag, provenance, deterministic sorted).
- `aios/capability/graph.py` — `GraphNode`/`GraphEdge` + `KnowledgeGraph` (in-memory, manual add_node/add_edge, neighbors/find_path BFS deterministic, 8 node types, 7 edge types).
- `aios/capability/__init__.py` — public re-exports.
- `aios/runtime/kernel.py` — wires 4 singletons, exposes `capabilities`/`prompts`/`catalog`/`graph`, extends `health()`.

## Decisions
- RLock on every store (matching TASK-007 pattern) for thread-safety.
- Capability resources validate like WorkflowResource (cpu>0, memory regex) for fail-closed consistency across contracts.
- Prompt template rejects stray braces outside `{identifier}`; extra kwargs ignored, missing fails.
- Catalog search is lowercased substring over id/type/tags/description/metadata (no embeddings).
- Graph rejects duplicate node_id, duplicate edge_id, missing-node edge, duplicate (from,to,edge_type) triple, self-loop; BFS queue ordered by sorted neighbor ids.
- Layering: `aios/capability` only imports `aios.core` + stdlib; `runtime.kernel` imports `capability` downward.

## Boundaries (M1)
- No SQLite persistence, no auto-build, no reasoning engine, no Jinja2, no vector search — per amendment.
