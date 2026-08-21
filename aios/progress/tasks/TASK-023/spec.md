# TASK-023 — Memory Coordinator

## Objective
Build Memory Coordinator as the central coordination layer between 4 memory stores (Conversation, Session, Knowledge, Artifact) and Context Service. Provides unified query, retrieval, filtering, ranking, deduplication, and budget-aware selection.

## Scope
### In scope
- MemoryQuery/MemoryCandidate/MemoryScore/MemorySelection/MemoryContext contracts
- Retrieval from 4 memory types via contract
- Deterministic ranking without LLM
- Deduplication
- Memory budget selection
- Provenance/evidence metadata
- Memory isolation boundary (INV-011)

### Out of scope
- Context compression (TASK-024)
- Model selection (TASK-025)
- Multi-tenant isolation (M7)
- Autonomous memory (M9)

## Deliverables
- `aios/memory_coordinator/__init__.py`
- `aios/memory_coordinator/contracts.py` — query/candidate/score/selection/context
- `aios/memory_coordinator/coordinator.py` — main coordinator
- `aios/memory_coordinator/ranker.py` — deterministic ranking
- `aios/memory_coordinator/dedup.py` — deduplication
- `aios/memory_coordinator/tests/` — tests

## Acceptance Criteria
- AC-023-01: Full unified contract
- AC-023-02: Accesses all 4 memory types via contract
- AC-023-03: Retrieval strategy per policy
- AC-023-04: Deterministic ranking without LLM
- AC-023-05: Out-of-scope candidates filtered
- AC-023-06: Duplicate memory doesn't bloat context
- AC-023-07: Selection within memory budget
- AC-023-08: Selected memory has valid provenance
- AC-023-09: Agent cannot access Memory implementation directly
- AC-023-10: Output compatible with Context Service
- AC-023-11: Runs offline with mock providers
- AC-023-12: M0–M4 regression PASS
- AC-023-13: No INV-001..010/INV-011 violation

## Dependencies
- TASK-022 (Orchestrator v2)

## Governance references
- Rule 1..7 satisfied via `aios/governance/*`.
