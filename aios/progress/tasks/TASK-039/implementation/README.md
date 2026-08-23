# TASK-039 Implementation — Quota + Cost + Resource Governance

Implementation lives in `aios/quota/` (M7 Enterprise — Quota/Cost).

```
aios/quota/
  contracts.py     # QuotaPolicy, CostBudget, ResourceLimit
  quota_manager.py # QuotaManager (tenant-scoped limits, cost tracking)
  __init__.py      # re-exports
  tests/
    test_quota.py
    test_cost.py
```

Tenant-scoped resource and cost governance. Quota enforcement is fail-closed.

See `../spec.md`, `../test.md`, `../evaluation.md`, `../regression.md` for acceptance, verification and regression evidence. Full suite: `python -m pytest aios -q` (2519 PASS current).
