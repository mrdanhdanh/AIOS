# Breakdown — TASK-125

1. `aios/coder/contract.py` — `CoderAgentContract` (I/O-free, capability-injected, immutable agent_id).
2. `CodingTaskState` enum + `_CODING_TRANSITIONS` (PLANNED→CODING→REVIEWING↔PATCHING→DONE).
3. `CoderAgentStateMachine` với fail-closed guards (thiếu artifact / policy reject → REJECT, T001 Rule 6 / T113).
4. Provenance: mọi transition ghi `TransitionRecord` (evidence_id, run_id, content_hash) — T001 Rule 5.
5. Deterministic: cùng (state, artifacts) → cùng transition + cùng content_hash.
6. Tests (12) theo Test Matrix TASK-125 + architecture guard (unknown layer, no forbidden imports).
7. Tích hợp dependency: T124 -> T125 -> T126/T127 (M19).
