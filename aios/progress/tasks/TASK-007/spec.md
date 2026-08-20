# TASK-007 — Memory + Knowledge

## Objective
Give AIOS an offline-first, deterministic memory and knowledge substrate so conversations, sessions, knowledge snippets and artifact references are stored with strict isolation, content-addressed provenance, and deterministic retrieval — without requiring an LLM, embeddings service, or network. TASK-007 adds a **MemoryStore** (4 memory types with scoped isolation) and a **KnowledgeIndex** (ingest from local docs / PDF-extracted text / code sources with metadata, deterministic TF-ranked retrieval whose hits carry provenance evidence pointers), both wired into the `RuntimeKernel` `Container` as singletons.

## Scope
- **Memory** (`aios/runtime/memory.py`): `MemoryType` (CONVERSATION/SESSION/KNOWLEDGE/ARTIFACT), `MemoryEntry` (content-hash, scope_id, provenance, metadata, SemVer-friendly version), `MemoryStore` (thread-safe `RLock`, put/get/list_by_type/list_by_scope/search/delete/verify, isolation enforced — a query scoped to `scope_id` never returns entries from another scope; cross-scope reads are rejected unless caller explicitly requests unscoped listing).
- **Knowledge** (`aios/runtime/knowledge.py`): `KnowledgeSourceType` (LOCAL_DOC/LOCAL_PDF/LOCAL_CODE/INLINE), `KnowledgeSource`, `KnowledgeDocument` (content-hash + provenance), `KnowledgeIndex` (in-memory inverted index; `add_source`/`ingest`/`search` with deterministic ranking: term-frequency → source-type priority → doc_id tiebreak; no embeddings/LLM; hits return `KnowledgeHit` with provenance `source_id`/`content_hash`/`metadata` suitable as evidence).
- **Kernel wiring** (`aios/runtime/kernel.py`, `aios/runtime/__init__.py`): register `MemoryStore` and `KnowledgeIndex` as `SINGLETON` in `RuntimeKernel`, expose `memory`/`knowledge` accessors, extend `health()`, re-export public API via `runtime/__init__.py`.
- **Policy/permission touchpoints**: `PermissionScope.MEMORY_READ/WRITE` already reserved; `MemoryStore` checks are cooperative (callers consult `PermissionBroker`/`PolicyEngine`), store itself is fail-open for unit tests but documents the contract — later orchestrator layers enforce it through the Runtime. Provenance is carried on every entry/document so `AuditTrail`/`EvidenceStore` can chain it.
- **Out of scope**: vector embeddings, remote knowledge bases, LLM-based retrieval/reranking, persistence to disk (in-memory only for M1), TTL/eviction policies beyond explicit `delete`.

## Deliverables
- `aios/runtime/memory.py` — `MemoryError`, `MemoryType`, `MemoryEntry`, `MemoryStore`.
- `aios/runtime/knowledge.py` — `KnowledgeError`, `KnowledgeSourceType`, `KnowledgeSource`, `KnowledgeDocument`, `KnowledgeHit`, `KnowledgeIndex`.
- `aios/runtime/kernel.py` — updated to wire `MemoryStore` + `KnowledgeIndex`.
- `aios/runtime/__init__.py` — extended to export the new memory/knowledge public API.
- `aios/runtime/tests/test_memory.py` — isolation, provenance, lifecycle, search, thread-safety, error paths.
- `aios/runtime/tests/test_knowledge.py` — source ingestion, deterministic retrieval, provenance, source types, thread-safety.
- `aios/runtime/tests/test_kernel.py` — extended (or supplemented) to assert new kernel wiring.
- `aios/progress/tasks/TASK-007/` governance artifacts (spec, critique×2, tasks.md, review, test.md, evaluation, REGRESSION.md).

## Acceptance Criteria
1. **Four memory types** `CONVERSATION/SESSION/KNOWLEDGE/ARTIFACT` exist and `MemoryStore` stores/retrieves each type correctly (automated test PASS).
2. **Isolation**: entries written under `scope_id="scope-A"` are never returned by `list_by_scope("scope-B")` or `search(..., scope_id="scope-B")`; unscoped `list`/`search` returns all but callers must opt-in (automated test PASS).
3. **Provenance & integrity**: every `MemoryEntry`/`KnowledgeDocument` carries `content_hash` (SHA-256) and `provenance` (source/producer/task_id/run_id); `verify()` recomputes hash; tampered content fails verification (automated test PASS).
4. **Knowledge sources + metadata**: `LOCAL_DOC`, `LOCAL_PDF`, `LOCAL_CODE`, `INLINE` sources can be registered; ingesting a document preserves `source_id`, `metadata`, `content_hash`, and provenance (automated test PASS).
5. **Deterministic retrieval**: same `KnowledgeIndex` + same documents + same query → same ranked order; ranking is TF-score → source-type priority → doc_id (automated test PASS). No LLM/embeddings/network is used.
6. **Retrieval carries evidence**: each `KnowledgeHit` exposes `source_id`/`content_hash`/`metadata` so a caller can build an evidence chain (automated test PASS).
7. **Kernel wiring**: `RuntimeKernel` resolves `MemoryStore` and `KnowledgeIndex` as singletons via the `Container`; `health()` includes `memory_entries`/`knowledge_docs` (automated test PASS).
8. **Thread-safety**: concurrent `put`/`ingest`/`search` from multiple threads does not corrupt state (automated test PASS via `threading.Barrier`).
9. **Test suite**: `python -m pytest aios -q` passes with zero failures.
10. **Regression**: TASK-001..006 tests continue to pass (regression gate: dependency closure {TASK-003}); no architecture violations (`agent` never imports runtime internals directly beyond allowed layers).

## Dependencies
- TASK-003 (Kernel Foundations) — DONE. Uses `Container`, `SemVer` validation, `EventBus` patterns.
- Indirectly builds on TASK-004 conventions (`Artifact` checksum/provenance shape, `PermissionScope.MEMORY_READ/WRITE`, `AuditTrail` chain) — no hard code dependency but follows same idioms.

## Governance references
- Rule 1..7 via `aios/governance/*`. Architecture: `runtime` layer — relative imports only; no `agent`/`orchestrator` imports. Deterministic-first: ranking/hashing/search are pure Python, no LLM call.

## Notes
- Offline-first: both stores are pure-Python, in-memory, no external SDKs; PDF/code sources are ingested as pre-extracted text (callers do extraction before `ingest`) so no PDF parser dependency is required for M1.
- Later M5 tasks (TASK-023 Memory Coordinator, TASK-057 Autonomous Memory) will add coordination, eviction, and persistence; this task is the M1 substrate.
