# TASK-002 — Critique 1

## Strengths
- Covers the foundational cross-cutting concerns (config, logging, metadata,
  healthcheck) that every later module depends on.
- Ties acceptance criteria to automated tests, consistent with TASK-001
  governance principles.
- Backward-compatibility regression requirement protects existing governance
  gate tests.

## Risks / Gaps
1. **Config validation**: The spec does not specify what happens when an
   environment variable has an invalid type (e.g. `AIOS_LOG_LEVEL=not_a_level`).
   Must fail-closed with a clear error, not silently fall back to default.
2. **Healthcheck extensibility**: A flat list of probes may not scale. Consider
   allowing probe registration so later tasks (M6+) can add subsystem checks
   without modifying the core healthcheck module.
3. **Metadata provenance**: `PackageMetadata` should include a `commit_hash` or
   `build_id` field so that evidence records in the Evidence Store can link
   runtime version to a specific build.
4. **Test isolation**: Shared `conftest.py` must not leak state between tests;
   use `tmp_path` fixture for any file-system side effects.
5. **No logging rotation**: The logging module sets up handlers but does not
   specify rotation policy; acceptable for M1 but should be noted as a future
   concern.

## Required Revisions
- Add config validation with explicit error on invalid env-var values (done in
  implementation).
- Use a probe registry pattern for healthcheck extensibility (done).
- Add `commit_hash` field to `PackageMetadata` (done).
- Ensure conftest fixtures are session-scoped where safe and function-scoped
  otherwise (done).
