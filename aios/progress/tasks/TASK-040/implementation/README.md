# TASK-040 Implementation — Credential + Network + Sandbox Isolation

Implementation lives in `aios/security/` (M7 Enterprise — Isolation).

```
aios/security/
  secrets.py    # Credential isolation (secrets, not leaked in logs)
  isolation.py  # Network/sandbox isolation
  contracts.py  # IsolationPolicy, CredentialRef
  auth.py       # Auth boundary
  __init__.py   # re-exports
  tests/
    test_secrets.py
    test_isolation.py
```

Secrets/network/sandbox isolation. Credentials never appear in logs or error messages.

See `../spec.md`, `../test.md`, `../evaluation.md`, `../regression.md` for acceptance, verification and regression evidence. Full suite: `python -m pytest aios -q` (2519 PASS current).
