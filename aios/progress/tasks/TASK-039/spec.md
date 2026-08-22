# TASK-039 — Quota + Cost + Resource Governance

## Objective
Build Enterprise Resource Governance that controls quota, resource consumption, concurrency, LLM tokens/cost, tool calls, storage, sandbox time, and budget per tenant. Ensures no single tenant can monopolize system resources. Governance decides "is tenant allowed?" while Resource Service decides "does system have resources?".

## Scope
### In scope
- Tenant Quota: concurrent_executions, cpu, memory, llm_tokens, storage, LLM calls, tool calls, execution/sandbox time
- Cost Governance: Cost Estimator (estimated vs actual), Budget Policy (ALLOW/DENY/ASK/DOWNGRADE/QUEUE), UsageLedger
- Quota evaluation: Identity → Tenant → Quota Lookup → Current Usage → Requested → ALLOW/DENY (atomic reservation: check → reserve → execute → settle/release)
- Cost evaluation: EstimatedCost vs ActualCost with provenance
- Budget Policy: daily, per_execution, per_request with action_on_exceed
- UsageLedger: immutable usage/cost records with tenant/project/principal/execution provenance
- Integration with TASK-035 Identity, TASK-036 Tenant, TASK-025 Model Router, TASK-038 Distributed Scheduler, Resource Service

### Out of scope
- Replacing Resource Service (Governance is decision layer, not resource owner)
- Building billing infrastructure
- Creating a parallel control plane

## Deliverables
- `aios/quota/contracts.py` — Quota, QuotaUsage
- `aios/quota/quota_manager.py` — QuotaManager (set_quota, check_quota, consume_quota, get_usage, reset_quota)
- `aios/quota/tests/` — quota and cost governance tests

## Acceptance Criteria
- AC-039-01: Tenant over concurrent_executions → DENY
- AC-039-02: Tenant over CPU/RAM quota → DENY
- AC-039-03: Tenant within quota → ALLOW
- AC-039-04: Concurrent requests no race over quota
- AC-039-05: Reservation released on fail/cancel
- AC-039-06: Cost estimated before execution, actual recorded after
- AC-039-07: Budget exceeded → DENY or policy action
- AC-039-08: Cost constraint passed to Model Router
- AC-039-09: Fail-closed on UNKNOWN quota/budget
- AC-039-10: Regression M1–M6 PASS

## Dependencies
- TASK-038 — Distributed Scheduler + Lease + Failover

## Governance references
- Rule 1..7 satisfied via `aios/governance/*`.
- INV-022..029 preserved.
