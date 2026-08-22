# TASK-070 — Test

## How to run
```
python -m pytest aios/security -q
```

## What is covered
- **Unit / Contract** (`aios/security/tests/test_security_baseline.py`):
  - `TestExternalAuth` — external call không auth → BLOCK (AC1).
  - `TestPermissionFailClosed` — action không permission → BLOCK fail-closed; policy DENY override (AC2).
  - `TestSecretHandling` — secret trong log → redacted; context không giữ value (AC3).
  - `TestLeastPrivilege` — vượt scope → BLOCK; trong scope / wildcard → ALLOW (AC4).
  - `TestAuditTrail` — privileged action → audit evidence (có evidence_ref, dùng EvidenceStore) (AC5).
  - `TestDeterminism` — cùng context + action → cùng quyết định (AC6).
  - `TestIntegration` — Governor (T054) scope enforcement; API bridge `from_api_context` (AC7).
- **Architecture**: `security` layer = `unknown`; không import `aios.agents.*`.
- **Regression**: chỉ chạy package tests (`aios/security`), không phá existing
  `aios/security/tests/test_security.py` (IsolationManager).

## Result
27 passed.
