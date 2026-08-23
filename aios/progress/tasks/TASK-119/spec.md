# TASK-119 — Dependency Graph

## Objective
Triển khai **Dependency Graph** (M18) như một năng lực có contract, evidence và harness riêng, tích hợp với các task phụ thuộc theo dependency của milestone.

## Scope
**In scope:** `aios/context/dependency_graph.py` — `DependencyGraph, DependencyGraphResult, DepNode, DepEdge`.
**Out of scope:** pipeline/retriever mới ngoài phạm vi; vendor lock-in.

## Deliverables
- `aios/context/dependency_graph.py` implementation + contract/schema.
- Unit + Contract + Integration + Architecture + Regression tests trong `aios/context/tests/test_context.py`.
- Tích hợp theo dependency: T117/T118 -> T119 -> T120.

## Acceptance Criteria
- Mọi artifact mang `content_hash` (T078) + provenance (T001 Rule 5).
- Fail-closed: invalid/unresolved/inconclusive -> reject (T078).
- Deterministic: cùng input + cùng state -> cùng output; LLM call count = 0.
- Secret isolation (T040/T113): không đọc/lộ secret.
- Tích hợp dependency theo chuỗi T117/T118 -> T119 -> T120.
- Regression của các milestone trước PASS; không vi phạm invariants.

## Dependencies
- T117/T118 -> T119 -> T120.
- T001 (Evidence/Rule 5), T078 (Integrity), T040 (Credential), T113 (Security), T024 (Context Optimizer) theo từng task.

## Governance references
- Rule 1..7 via `aios/governance/*`. `context` là `unknown` (infra) layer.
