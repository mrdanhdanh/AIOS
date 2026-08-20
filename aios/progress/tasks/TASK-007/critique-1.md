# TASK-007 — Critique 1

## Strengths
- Offline-first substrate: pure-Python in-memory stores with SHA-256 content-hash — no embeddings, LLM, or network required, matching the Runtime-First/Offline-First pillars.
- Isolation by `scope_id` is explicit and testable; provenance (`content_hash` + producer/source/task_id/run_id) mirrors the Artifact/Evidence shape from TASK-004/Rule 5.
- Knowledge retrieval is deterministic (TF → source-type priority → doc_id) and therefore harness-replayable; no vector/LLM reranking keeps M1 simple and verifiable.
- Kernel wiring reuses the TASK-005 composition-root pattern (Container SINGLETON + health snapshot), so memory/knowledge are resolved by type without import coupling.

## Risks / Gaps
1. **Permission enforcement boundary**: store is cooperative (callers consult Policy/PermissionBroker) — must document that orchestrator layers enforce `MEMORY_READ/WRITE`, not the store itself, to avoid implying fail-closed inside the store for unit tests.
2. **Source ingestion without PDF parsing**: M1 ingests pre-extracted text; critique requests explicit note that callers extract PDF/code text before `ingest` so no parser dependency is introduced.
3. **Thread-safety surface**: both stores mutate inverted index / scope maps; require RLock + Barrier-tested concurrency.

## Required Revisions
- Document cooperative permission contract and M1 in-memory-only / no-eviction scope (done in spec).
- Make ranking fully deterministic and documented (TF → source-type priority → doc_id) (done).
- Require SHA-256 `verify()` on every entry/document (done).

## Verdict
APPROVE — spec is precise, testable, and layer-correct.
