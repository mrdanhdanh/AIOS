# TASK-013 — Critique 2 (Architecture & Test Review)

## Strengths
- Worker package is pure Python, deterministic, offline-first, no LLM, no direct Tool/Runtime/Provider/filesystem imports.
- Worker lifecycle is state-machine controlled with valid transitions, thread-safe, fail-closed, distinct from Task lifecycle.
- Capability-only access via CapabilityRegistry; permission boundary via PolicyEngine delegation; evidence with provenance chain.
- Four concrete workers (General/Coder/Doctor/SystemDoctor) share BaseWorker contract but specialize domain logic.

## Risks / Gaps
- `aios/worker` must be classified as `worker` layer in Architecture Guard (between orchestrator and runtime) — verify via guard LAYER_ORDER and ALLOWED_IMPORT_LAYERS.
- Worker must not import `aios.runtime.providers`, `aios.runtime.filesystem`, `subprocess`, `os` execution primitives — verify via AST scan.
- Worker must not import `aios.runtime.kernel` or `aios.runtime.execution` internals directly — only via Capability abstraction.
- Tests must cover all 11 ACs distinctly: contract, capability-only, runtime boundary, permission boundary, lifecycle, result, evidence, routing, failure, architecture, regression.
- Worker failure must propagate to Orchestrator/FailureRecovery, not create parallel control plane — need integration test.

## Required revisions
- [x] Verify worker imports only capability/unknown (no runtime/tool/agent) via guard scan_source.
- [x] Ensure BaseWorker capability access goes through CapabilityRegistry.resolve, not direct tool invocation.
- [x] Ensure WorkerRouter fallback only when policy allows (policy_checker delegate).
- [x] Create 8 test files covering AC-013-01..11 with ≥60 tests total + architecture + integration.

## Decision
- APPROVE with required revisions addressed — proceed to review.
