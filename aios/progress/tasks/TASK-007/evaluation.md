# TASK-007 — Evaluation

## Acceptance criteria results

| AC | Result | Evidence |
|----|--------|----------|
| Four memory types (CONVERSATION/SESSION/KNOWLEDGE/ARTIFACT) | PASS | `test_memory.py::test_memory_type_all_four`, `test_store_list_by_type` |
| Isolation (scope_id never leaks) | PASS | `test_store_isolation_scope_a_not_in_scope_b`, `test_store_search_isolation` |
| Provenance & integrity (content_hash SHA-256 + verify) | PASS | `test_entry_create_computes_hash`, `test_entry_verify_fails_when_tampered`, `test_store_rejects_bad_hash`, `test_store_verify_all`, same for knowledge `test_document_create_computes_hash`/`test_verify_all` |
| Knowledge sources + metadata (LOCAL_DOC/LOCAL_PDF/LOCAL_CODE/INLINE) | PASS | `test_index_all_four_source_types_ingestable`, `test_index_provenance_preserved_through_ingest`, `test_index_ingest_and_get` |
| Deterministic retrieval (TF→priority→doc_id) | PASS | `test_search_deterministic_same_order`, `test_search_ranking_tf_then_source_priority_then_doc_id`, `test_search_no_embeddings_no_llm_pure_tf` |
| Retrieval carries evidence | PASS | `test_search_carries_evidence` (source_id/content_hash/metadata/producer on KnowledgeHit) |
| Kernel wiring (SINGLETON + health) | PASS | `RuntimeKernel` wires `MemoryStore`/`KnowledgeIndex` as SINGLETON; `health()` includes `memory_entries`/`knowledge_docs`/`knowledge_sources` (kernel.py + __init__.py exports) |
| Thread-safety | PASS | `test_store_thread_safety`, `test_thread_safety` (Barrier 20) |
| Test suite all green | PASS | `326 passed in 1.81s` (full `python -m pytest aios -q`) |
| Regression (TASK-001..006) | PASS | full suite 326/326 PASS; see REGRESSION.md |

## Regression
- Dependency closure of TASK-007 = {TASK-003}. TASK-003 suite (78) + TASK-007 (60) both PASS; full suite 326/326 PASS.

## Status
- All 10 acceptance criteria verified.
- REGRESSION gate: PASS.
- Unified Gate: PASS (spec + critique×2 + breakdown + review + implementation + test + evaluation + regression).
