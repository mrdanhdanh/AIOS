# TASK-145 — Implementation

Module: `aios/coding_loop/state_machine.py`

Exports:
- `CodingLoopStateMachine` — deterministic, fail-closed coding loop state machine.
- `CodingLoopState` — OBSERVING / CLASSIFYING / DIAGNOSING / REPAIRING / VERIFYING / REFRESHING / SAFETY / DONE.
- `CodingLoopRecord` — immutable-by-id loop record (`loop_id`, `policy_ref`, `evidence_ref`, `authority="aios"`).
- `TransitionEvent` — recorded transition with provenance.
- `TRANSITIONS` — closed deterministic state→next-state map.

Key invariants:
- `transition()` fail-closed: requires `artifact` (T001 Rule 6) and `policy_ref` (T113).
- `next_state()` deterministic: same state → same next state.
- `loop_id` immutable (T001 Rule 1).
- `provenance()` carries `content_hash` (T078).

Integration: built on Autonomous Loop T053 + Goal Engine T050 + Evidence T001 Rule 5/6.
