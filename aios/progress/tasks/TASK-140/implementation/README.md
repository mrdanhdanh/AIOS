# TASK-140 Implementation

Module: `aios/execution/build_lint.py`

Public classes:
- `BuildLintRunner` — runs build/lint in a sandbox under policy (dispatches via `CapabilityDispatcher`).
- `BuildLintRun` — result with build + lint results and full provenance.
- `BuildResult`/`LintResult` + `BuildVerdict`/`LintVerdict` — outcomes with `content_hash` (T078).

Properties: I/O-free, deterministic, fail-closed (sandbox-only + policy + contract + BLOCKED detection). Provenance via `content_hash()`.
