# TASK-049 Implementation — Certification

Implementation lives in `aios/certification/` (M8 Ecosystem — Certification).

```
aios/certification/
  contracts.py  # CertificationContract, TrustLevel
  pipeline.py   # Certification pipeline (profiles/checks/revocation/expiry)
  certifier.py  # Certifier (certify/verify/revoke)
  release.py    # Release certification
  __init__.py   # re-exports
  tests/
    test_certification.py
    test_pipeline.py
```

Certification and trust for ecosystem. Profiles/checks/revocation reasons/expiry.

See `../spec.md`, `../test.md`, `../evaluation.md`, `../regression.md` for acceptance, verification and regression evidence. Full suite: `python -m pytest aios -q` (2519 PASS current).
