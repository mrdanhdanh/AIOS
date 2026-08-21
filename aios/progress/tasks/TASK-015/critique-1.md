# TASK-015 — Critique 1

## Reviewer: Critic Agent
## Verdict: APPROVE (with notes)

## Strengths
- Spec covers full Skill lifecycle: RESOLVE→VALIDATE→INSTALL→ENABLE→READY→DISABLE→UNLOAD→RELOAD→UPGRADE→ROLLBACK→REMOVE with deterministic transitions.
- Dependency resolver handles direct + transitive, version constraints, conflict and cycle detection (fail-closed).
- Sandbox Pool design covers warm-start, health check, acquire/release, reset, idle eviction, resource/timeout, isolation.
- Persistence and rollback safety are explicit: backup certified state before upgrade, restore on failure.
- Capability/Policy/Permission integration is correct: skill declares, runtime enforces.
- Offline-first and evidence provenance are preserved.

## Issues (non-blocking)
- Ensure Skill layer only imports `aios.core` + stdlib, never runtime/orchestrator/agent internals directly (ARCH-004). Manager is at runtime/orchestrator boundary, not skill layer.
- SkillManager must not become God Object: delegate to Resolver, Registry, SandboxPool, Policy, StateStore.
- Sandbox reset must be verifiable: test must prove no state leakage between executions.
- Rollback must be atomic: if rollback itself fails, state must be FAILED/BLOCKED, not silently healthy.
- Persistent state must survive restart: test must simulate restart by re-instantiating manager from persisted store.

## Required revisions (addressed)
- [x] Skill contracts at skill layer (core/stdlib only), manager at runtime layer.
- [x] Manager delegates to specialized components.
- [x] Sandbox reset verifiable via tests.
- [x] Rollback failure → FAILED/BLOCKED.
- [x] Persistence restart test.

## Decision
APPROVE — proceed to critique-2.
