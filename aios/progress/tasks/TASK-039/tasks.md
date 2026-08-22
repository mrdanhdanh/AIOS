# TASK-039 — Breakdown

## Steps
1. Create `aios/quota/contracts.py` — Quota (tenant_id, resource_type, limit, used, remaining, exceeded), QuotaUsage
2. Create `aios/quota/quota_manager.py` — QuotaManager: set_quota, check_quota, consume_quota (with exceeded check), get_usage, reset_quota
3. Implement atomic quota reservation and fail-closed on UNKNOWN
4. Implement cost estimation (estimated vs actual) and budget policy
5. Create `aios/quota/tests/` — 5 tests (set/check, consume, exceeded DENY, usage, reset)
6. Run architecture guard — verify no Governance → Resource execution ownership
7. Run full suite — 1783/1783 PASS (5 new), no regressions

## Dependencies
- TASK-038 Distributed Scheduler

## Exit Criteria
- All AC-039-01..10 PASS, gate PASS, no regressions
