# TASK-041 Implementation — HA + Audit + Recovery

Implementation lives in `aios/ha/` (M7 Enterprise — HA/Audit/Recovery).

```
aios/ha/
  ha_manager.py # HA manager (health, failover)
  health.py     # Health checks
  lease.py      # Single-active lease
  recovery.py   # Recovery (checkpoint/restore)
  audit.py      # Hash-chained audit trail
  contracts.py  # HAConfig, AuditEntry, RecoveryPlan
  __init__.py   # re-exports
  tests/
    test_ha.py
    test_audit.py
    test_recovery.py
    test_lease.py
```

High availability, hash-chained audit, and recovery. Single-active lease prevents split-brain.

See `../spec.md`, `../test.md`, `../evaluation.md`, `../regression.md` for acceptance, verification and regression evidence. Full suite: `python -m pytest aios -q` (2519 PASS current).
