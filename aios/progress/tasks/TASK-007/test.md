# TASK-007 — Test Report

## Tests
- `aios/runtime/tests/test_memory.py` — 27 tests: MemoryType, MemoryEntry hash/provenance, MemoryStore put/get/list_by_type/list_by_scope/search isolation & ranking, delete, verify_all, contains/len, thread-safety (Barrier 20).
- `aios/runtime/tests/test_knowledge.py` — 33 tests: KnowledgeSourceType, KnowledgeDocument hash/provenance, KnowledgeIndex add_source/ingest/list_by_source, all 4 source types, deterministic ranking (TF→priority→doc_id), source_type filter, limit, empty/no-match, evidence-carrying hits, case-insensitive, verify_all, contains/len, thread-safety (Barrier 20).
- Existing `aios/runtime/tests/test_kernel.py` — kernel wiring still green; `health()` now includes `memory_entries`/`knowledge_docs`/`knowledge_sources`.

## Command
```
python -m pytest aios -q
```

## Result
- `60 passed` for `test_memory.py` + `test_knowledge.py` isolated.
- `326 passed` full suite (`aios/...`) — zero failures.
- REGRESSION: dependency closure (TASK-003) green; TASK-001..006 still green.

## Coverage notes
- Isolation: entries scoped to `scope-A` never appear in `scope-B` queries (store + search).
- Provenance: every entry/document carries `content_hash` + `producer`/`source`/`task_id`/`run_id`/`metadata`; `verify()` recomputes SHA-256.
- Deterministic retrieval: same index + same docs + same query → same ranked order (TF → source-type priority → doc_id).
- Thread-safety: concurrent put/ingest/search via `threading.Barrier` does not corrupt state.
