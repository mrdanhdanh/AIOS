# TASK-011 Implementation — M1 Remediation / Architecture Hardening

Implementation lives in `aios/governance/architecture/` and related governance/runtime hardening.

```
aios/governance/architecture/
  guard.py               # ArchitectureGuard — ARCH-001..004 enforcement
  tests/
    test_m1_hardening.py # M1 gate hardening tests (30 cases)
aios/governance/         # lifecycle/evidence/regression gates
aios/runtime/            # kernel/services wiring hardening
aios/core/               # contracts/container/events hardening
```

See `../spec.md`, `../test.md`, `../evaluation.md`, `../REGRESSION.md` for
acceptance, verification and regression evidence. Full suite: `python -m pytest aios -q` (544 PASS at TASK-011).
