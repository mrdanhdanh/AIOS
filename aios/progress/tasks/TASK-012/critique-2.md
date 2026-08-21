# TASK-012 — Critique 2 (Architecture & Test Review)

## Strengths
- Orchestrator package remains pure Python, no LLM, offline-first, deterministic.
- Goal/Task persistence is file-based JSON, not RAM-only, supporting resume after restart.
- TaskQueue is logical (which task next), not technical scheduling (when) — separation from Scheduler Service is explicit.
- Permission Broker delegates to runtime, Failure Recovery is bounded and policy-gated.

## Risks / Gaps
- `aios/orchestrator` must not import `aios.agents` (layering: orchestrator may import runtime/capability/tool/unknown only). Verify via guard.
- TaskQueue must not implement cron/technical scheduling; only logical queue ops (enqueue/dequeue/peek/pause/resume/reorder/prioritize/cancel/block/unblock).
- Failure Recovery must not duplicate Runtime retry engine; it handles orchestration-level recovery only.
- Tests must cover all 10 ACs distinctly: persistence, resume, dependency, queue separation, permission, fail-closed, retry bounded, recovery policy, state authority, regression.

## Required revisions
- [x] Verify orchestrator imports only runtime/capability/tool/unknown (no agent).
- [x] Ensure TaskQueue has no cron/scheduler logic.
- [x] Ensure FailureRecovery delegates fallback to policy_checker.
- [x] Create 5 test files covering AC-012-01..10 with ≥40 tests total.

## Decision
- APPROVE with required revisions addressed — proceed to review.
