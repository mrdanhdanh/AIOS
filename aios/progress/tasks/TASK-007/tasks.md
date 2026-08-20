# TASK-007 — Breakdown

- [x] **7.1** Implement `aios/runtime/memory.py` — `MemoryError`, `MemoryType`, `MemoryEntry` (SHA-256 `content_hash` + `verify()`, provenance/metadata), `MemoryStore` (RLock, put/get/list_by_type/list_by_scope/search/delete/verify, isolation)
- [x] **7.2** Implement `aios/runtime/knowledge.py` — `KnowledgeError`, `KnowledgeSourceType`, `KnowledgeSource`, `KnowledgeDocument` (`content_hash`+`verify()`), `KnowledgeHit`, `KnowledgeIndex` (inverted index, `add_source`/`ingest`/`search` deterministic TF → source-type priority → doc_id, no LLM/embeddings)
- [x] **7.3** Update `aios/runtime/kernel.py` — wire `MemoryStore` + `KnowledgeIndex` as SINGLETON, add `memory`/`knowledge` accessors, extend `health()` with `memory_entries`/`knowledge_docs`
- [x] **7.4** Update `aios/runtime/__init__.py` — re-export memory + knowledge public API
- [x] **7.5** Write `aios/runtime/tests/test_memory.py` — types, lifecycle, isolation, provenance/integrity, search, thread-safety, errors
- [x] **7.6** Write `aios/runtime/tests/test_knowledge.py` — source types, ingestion, deterministic retrieval/ranking, provenance, evidence-carrying hits, thread-safety
- [x] **7.7** Extend/verify `test_kernel.py` — assert new singletons and health fields (via `health()` including `memory_entries`/`knowledge_docs`/`knowledge_sources`)
- [x] **7.8** Run full suite `python -m pytest aios -q` — zero failures (326 passed)
- [x] **7.9** Write `REGRESSION.md` + `test.md` + `evaluation.md` — verify dependency closure (TASK-003) and AC 1-10
