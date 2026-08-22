# TASK-056 Implementation

## Modules
- `contracts.py` — `DurableCheckpoint` (full goal-level semantics + `content_hash`), `InterruptionCause`, `ResumeVerdict`.
- `layer.py` — `GoalDurabilityLayer`: checkpoint coordinator (atomic, monotonic sequence), `validate` (hash + provenance + policy), `detect_stale`, idempotency guard (`acknowledge_action`), `resume`.

## Design notes
- Layer over existing Runtime; no new StateStore/Checkpoint Service.
- Checkpoints store authoritative execution state + references (not memory payloads) — boundary with T057 preserved.
- Fail-closed: invalid/inconclusive checkpoints never resume; stale checkpoints trigger re-plan via T051.
