# TASK-012 — Critique 1 (Spec Review)

## Strengths
- Spec scopes Operational Orchestration correctly as layer between Decision Pipeline and Runtime: Goal Manager + Task Queue + Permission Broker + Failure Recovery, không trở thành Runtime thứ hai.
- Deliverables pin exact files (`goal_manager.py`, `task_queue.py`, `permission_broker.py`, `failure_recovery.py`) với contracts rõ, persistence, thread-safe, fail-closed.
- AC-012-01..10 mirror T012.md test scenarios (resume, dependency, permission deny, retry bounded, recovery policy, state authority) và gate requirements.
- Out-of-scope explicitly defers Worker/Tool/multi-tenant/cron to later tasks.

## Risks / Gaps
- Goal persistence must be file-based JSON roundtrip, not just in-memory; need to verify `to_dict/from_dict` + `save_to_file/load_from_file` with restart simulation.
- TaskQueue dependency evaluation must be deterministic and priority must not override dependency — need explicit test for `B depends on A, B=HIGH, A=LOW` still BLOCKED.
- Permission Broker must delegate to runtime PolicyEngine, not decide itself; need to verify DENY→BLOCKED and ASK→human approval with evidence.
- Failure Recovery must be bounded (max_attempts) and fallback policy-gated; need to verify no infinite retry and fallback only when policy allows.
- State authority: orchestration state must only reference `execution_id`, not own Runtime execution state — need architecture test.

## Required revisions
- [x] Lock Goal lifecycle CREATED→PLANNED→ACTIVE→PAUSED→ACTIVE→COMPLETED with terminal states and valid transitions.
- [x] Define Task statuses PENDING/READY/RUNNING/PAUSED/BLOCKED/SUCCEEDED/FAILED/CANCELLED with dependency-aware evaluation.
- [x] Implement Permission Broker aggregate/normalize/deduplicate + delegate to PolicyEngine + ASK approval.
- [x] Implement FailureClassifier + RetryPolicy (exponential) + FailureRecovery with history and policy-gated fallback.
- [x] Add persistence for GoalManager and TaskQueue (JSON file).

## Decision
- APPROVE with required revisions addressed — proceed to critique-2.
