# TASK-035 Implementation — Identity + Principal + RBAC/ABAC

Implementation lives in `aios/identity/` (M7 Enterprise — Identity).

```
aios/identity/
  contracts.py        # Principal (5 types: User/Service/Agent/Workflow/System), Role, Permission
  identity_service.py # IdentityService (resolve, authorize)
  rbac.py             # RBAC resolver (Role → Permission, deny-by-default)
  abac.py             # ABAC engine (Subject/Resource/Action/Environment, deterministic)
  delegation.py       # Delegation (scope restriction, expiration, provenance, attenuation)
  __init__.py         # re-exports
  tests/
    test_identity.py
    test_rbac.py
    test_abac.py
    test_delegation.py
```

Fail-closed: `ALLOW/DENY/ASK` with reason and provenance. No parallel control plane.

See `../spec.md`, `../test.md`, `../evaluation.md`, `../regression.md` for acceptance, verification and regression evidence. Full suite: `python -m pytest aios -q` (2519 PASS current).
