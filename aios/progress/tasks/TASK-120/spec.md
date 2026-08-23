# TASK-120 — Semantic + Hybrid Index

## Objective
Triển khai **Semantic + Hybrid Index** (M18) như một năng lực có contract, evidence và harness riêng, tích hợp với các task phụ thuộc theo dependency của milestone.

## Scope
**In scope:** `aios/context/hybrid_index.py` — `HybridIndex, HybridIndexResult, HybridQueryResult, Embedding`.
**Out of scope:** pipeline/retriever mới ngoài phạm vi; vendor lock-in.

## Deliverables
- `aios/context/hybrid_index.py` implementation + contract/schema.
- Unit + Contract + Integration + Architecture + Regression tests trong `aios/context/tests/test_context.py`.
- Tích hợp theo dependency: T118/T119 -> T120 -> T121.

## Acceptance Criteria
- Mọi artifact mang `content_hash` (T078) + provenance (T001 Rule 5).
- Fail-closed: invalid/unresolved/inconclusive -> reject (T078).
- Deterministic: cùng input + cùng state -> cùng output; LLM call count = 0.
- Secret isolation (T040/T113): không đọc/lộ secret.
- Tích hợp dependency theo chuỗi T118/T119 -> T120 -> T121.
- Regression của các milestone trước PASS; không vi phạm invariants.

## Dependencies
- T118/T119 -> T120 -> T121.
- T001 (Evidence/Rule 5), T078 (Integrity), T040 (Credential), T113 (Security), T024 (Context Optimizer) theo từng task.

## Governance references
- Rule 1..7 via `aios/governance/*`. `context` là `unknown` (infra) layer.
