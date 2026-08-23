# TASK-143 Implementation

Module: `aios/execution/replay.py`

Public classes:
- `SecurityReplayHarness` — secure run in sandbox under policy + deterministic replay.
- `ReplayRun` — record of a deterministic replay with `replay_deterministic` + hashes.

Properties: I/O-free, deterministic, fail-closed (sandbox-only + policy + replay mismatch detection). Provenance via `content_hash()`.
