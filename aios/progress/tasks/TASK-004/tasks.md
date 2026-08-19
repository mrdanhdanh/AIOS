# TASK-004 — Breakdown

- [x] **4.1** Implement `aios/runtime/context.py` — ContextType (6 types), RuntimeContext, ContextStore with hierarchy + chain resolution
- [x] **4.2** Implement `aios/runtime/audit.py` — AuditStatus, AuditEvent (hash-chained), AuditTrail with integrity verification + query
- [x] **4.3** Implement `aios/runtime/artifact.py` — Artifact (SHA-256 + SemVer), ArtifactStore with on-write integrity + version resolution
- [x] **4.4** Implement `aios/runtime/permission.py` — PermissionScope, Permission (wildcard), PermissionBroker
- [x] **4.5** Implement `aios/runtime/policy.py` — PolicyDecision, PolicyRequest, PolicyRule, PolicyResult, deterministic PolicyEngine
- [x] **4.6** Update `aios/runtime/__init__.py` — export the public API for all five services
- [x] **4.7** Write `aios/runtime/tests/test_context.py` — 6 context types, hierarchy, chain, thread safety
- [x] **4.8** Write `aios/runtime/tests/test_audit.py` — chaining, tamper/reorder detection, query
- [x] **4.9** Write `aios/runtime/tests/test_artifact.py` — checksum, version sorting, integrity
- [x] **4.10** Write `aios/runtime/tests/test_permission.py` — grant/check, wildcard, revoke
- [x] **4.11** Write `aios/runtime/tests/test_policy.py` — permission gate, deny precedence, insufficient, determinism
- [x] **4.12** Run full test suite — all TASK-001/002/003/004 tests green (205 passed)
- [x] **4.13** Write regression.md — verify TASK-001/002/003 dependency closure green
