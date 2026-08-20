# TASK-009 — Breakdown

- [x] **9.1** Tạo package `aios/capability/` — `__init__.py` + `contracts.py` (CAPABILITY/PROMPT/CATALOG/GRAPH contracts, version 1.0.0, check helpers)
- [x] **9.2** Implement `aios/capability/capability.py` — `CapabilityError`, `CapabilityContract` (id/version/description/permissions/resources/tags/provenance + validate), `CapabilityRegistry` (RLock, register/get/list/find/remove/resolve, register_tool multi-tool mapping, health/priority, fail-closed)
- [x] **9.3** Implement `aios/capability/prompt.py` — `PromptError`, `PromptContract` (prompt_id/version/template/{identifier} variables/metadata + validate + render), `PromptRegistry` (register/get/version lookup/list/render, duplicate reject, missing var fail)
- [x] **9.4** Implement `aios/capability/catalog.py` — `CatalogError`, `CatalogEntry`, `SystemCatalog` (index/search/find_by_id/type/tag, provenance, RLock, deterministic lowercased substring)
- [x] **9.5** Implement `aios/capability/graph.py` — `GraphError`, `NodeType`, `EdgeType`, `GraphNode`, `GraphEdge`, `KnowledgeGraph` (in-memory, manual add_node/add_edge, neighbors/find_path BFS deterministic, reject invalid/duplicate/missing)
- [x] **9.6** Update `aios/runtime/kernel.py` — wire 4 singletons (CapabilityRegistry, PromptRegistry, SystemCatalog, KnowledgeGraph), expose `capabilities`/`prompts`/`catalog`/`graph` accessors, extend `health()`
- [x] **9.7** Update `aios/runtime/__init__.py` — re-export capability public API (keep layering downward only)
- [x] **9.8** Write `aios/capability/tests/test_capability.py` — AC-009-01/02/10, multi-tool, health/priority, errors, thread-safety
- [x] **9.9** Write `aios/capability/tests/test_prompt.py` — AC-009-04/05/10, version, render, missing var, duplicate, thread-safety
- [x] **9.10** Write `aios/capability/tests/test_catalog.py` — AC-009-06/09/10, index, search/query/type/tag, provenance
- [x] **9.11** Write `aios/capability/tests/test_graph.py` — AC-009-07/08/09/10, add/traversal, find_path, boundary, reject
- [x] **9.12** Write `aios/capability/tests/test_capability_architecture.py` — AC-009-03, architecture boundary (capability vs tool layer)
- [x] **9.13** Write `aios/capability/tests/test_kernel_wiring.py` — kernel singletons + health
- [x] **9.14** Run `python -m pytest aios -q` — zero failures, coverage fail_under 80, architecture invariants
- [x] **9.15** Write `test.md` + `evaluation.md` + `REGRESSION.md` + governance `review.md` + update `PLAN.md`/`LOG.md`/`STATS.md`
