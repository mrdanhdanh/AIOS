# TASK-034 Implementation — Doctor + Readiness

Implementation lives in `aios/harness/` (M6 Harness — Doctor/Readiness).

```
aios/harness/
  doctor.py     # DoctorService (diagnostics)
  readiness.py  # ReadinessEngine (13 domain doctors, fail-closed)
  contracts.py  # ReadinessResult, DoctorReport
  __init__.py   # re-exports
  tests/
    test_doctor.py
    test_readiness.py
```

Diagnoses system and computes readiness (fail-closed). 13 domain doctors cover all subsystems.

See `../spec.md`, `../test.md`, `../evaluation.md`, `../regression.md` for acceptance, verification and regression evidence. Full suite: `python -m pytest aios -q` (2519 PASS current).
