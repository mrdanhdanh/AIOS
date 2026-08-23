# TASK-141 Implementation

Module: `aios/execution/collector.py`

Public classes:
- `OutputArtifactCollector` — collects run output/artifacts with secret isolation.
- `CollectedArtifact` — collected outputs + artifacts with `content_hash` (T078).
- `OutputCapture` — single captured stream with integrity hash.
- `redact` — secret redaction (T040/T113).

Properties: I/O-free, deterministic, fail-closed (empty output rejected; empty artifact has empty hash). Provenance via `provenance()`.
