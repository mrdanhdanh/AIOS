# TASK-125 — Coder Agent Contract + State Machine

## Objective
Triển khai **Coder Agent Contract + State Machine** (M19) như một năng lực có contract, evidence và harness riêng — định nghĩa contract cho coder agent (I/O-free, capability-injected) và state machine vòng đời coding task. TASK-125 là **contract + state machine, không phải agent runtime mới** (dựa trên Agent Orchestrator T001/AGENTS + Worker Plane T013 + Lifecycle T001 Rule 6).

## Scope
**In scope:** `aios/coder/contract.py` — `CoderAgentContract`, `CoderAgentStateMachine`, `CodingTaskState`, `TransitionRecord`.
**Out of scope:** generator/planner/patch runtime mới (T126-T128); vendor lock-in.

## Deliverables
- `aios/coder/contract.py` implementation + contract/schema.
- Unit + Contract + Integration + Architecture + Regression tests trong `aios/coder/tests/test_coder.py`.
- Tích hợp theo dependency: T124 -> T125 -> T126/T127 (M19).

## Acceptance Criteria
- Coder Agent Contract định nghĩa rõ agent I/O-free, capability-injected.
- State Machine coding task đúng lifecycle (PLANNED→CODING→REVIEWING→PATCHING→DONE, T001 Rule 6).
- Agent không import forbidden module (ARCH-001..004) → BLOCK.
- Thiếu artifact → transition REJECT (fail-closed, T001 Rule 6).
- Mọi transition có provenance (T001 Rule 5).
- Cùng state + artifact → cùng transition (deterministic).
- Tích hợp được với Worker + Lifecycle + Architecture + Evidence.
- Regression của các milestone trước PASS; không vi phạm invariants.

## Dependencies
- T124 (Context Harness) -> T125 -> T126/T127.
- T001 (Evidence/Rule 5, Lifecycle Rule 6), T013 (Worker), T113 (Policy), ARCH (Guard).

## Governance references
- Rule 1..7 via `aios/governance/*`. `coder` là `unknown` (infra) layer.
