# TASK-152 — Context Refresh + Patch Chain

## Objective
Triển khai **Context Refresh + Patch Chain** (M21) như một năng lực có contract, evidence và harness riêng — làm mới context (Context Optimizer T024) và chuỗi hóa patch (Workspace/Snapshot T137) giữa các vòng lặp, sau khi verification gate (T151) PASS. TASK-152 là **refresh + chain, không phải optimizer mới** (dựa trên Verification Gate T151 + Context Optimizer T024 + Workspace/Snapshot T137 + Evidence T001).

## Scope
**In scope:** `aios/coding_loop/patch_chain.py` — `ContextRefreshPatchChain`, `PatchChain`.
**Out of scope:** optimizer mới (T024).

## Deliverables
- `aios/coding_loop/patch_chain.py` implementation + refresh + chain.
- Policy Boundary (T113) trên mọi refresh/chain.
- Integration với Verification Gate (T151) + Context Optimizer (T024) + Workspace/Snapshot (T137) + Evidence (T001).
- Unit + Contract + Integration + Architecture + Regression tests (`test_patch_chain.py`).

## Acceptance Criteria
- Context Refresh làm mới context mỗi vòng (T024).
- Patch Chain chuỗi hóa patch qua các vòng (T137).
- Snapshot trước/sau khớp (T137) — mismatch → fail-closed.
- Mọi patch có provenance (T001 Rule 5).
- Cùng state → cùng context (deterministic, T024).
- Tích hợp được với Verification Gate + Context Optimizer + Workspace/Snapshot + Evidence.
- Regression của các milestone trước PASS; không vi phạm invariants.

## Dependencies
- T151 (Verification Gate), T024 (Context Optimizer), T137 (Workspace / Snapshot Manager).
- T001 (Rule 5), T137 (Snapshot), T078 (Integrity), T113 (Policy).

## Governance references
- Rule 1..7 via `aios/governance/*`. `coding_loop` là `unknown` (infra) layer.
