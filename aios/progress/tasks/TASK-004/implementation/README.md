# TASK-004 — Implementation

The implementation lives in `d:\AIOS\aios\runtime\`.

```
aios/runtime/
  context.py     # ContextType (6), RuntimeContext, ContextStore
  audit.py       # AuditStatus, AuditEvent (hash-chained), AuditTrail
  artifact.py    # Artifact (SHA-256 + SemVer), ArtifactStore
  permission.py  # PermissionScope, Permission, PermissionBroker
  policy.py      # PolicyDecision, PolicyRequest, PolicyRule, PolicyResult, PolicyEngine
  __init__.py    # public API exports
  tests/
    test_context.py
    test_audit.py
    test_artifact.py
    test_permission.py
    test_policy.py
```

`verify_task004.py` below runs a self-contained smoke check of all five runtime
services (no pytest required).

```python
# Run with: python aios/progress/tasks/TASK-004/implementation/verify_task004.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[5]))

from aios.runtime import (
    ContextStore, ContextType, RuntimeContext,
    AuditTrail, AuditStatus,
    ArtifactStore, Artifact,
    PermissionBroker, Permission, PermissionScope,
    PolicyEngine, PolicyRequest, PolicyDecision,
)

ok = True
def check(name, cond):
    global ok
    ok &= bool(cond)
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}")

# Context
store = ContextStore()
req = RuntimeContext.create(ContextType.REQUEST)
agent = RuntimeContext.create(ContextType.AGENT, parent_id=req.context_id)
store.put(req); store.put(agent)
check("context chain", [c.context_type for c in store.resolve_chain(agent.context_id)][:2] == [ContextType.AGENT, ContextType.REQUEST])

# Audit
trail = AuditTrail()
trail.record("a", "x", "r1"); trail.record("a", "y", "r2")
check("audit integrity", trail.verify_integrity())

# Artifact
arts = ArtifactStore()
arts.put(Artifact.create("lib", "a", version="1.0.0"))
arts.put(Artifact.create("lib", "b", version="2.0.0"))
check("artifact latest", arts.get_latest("lib").version == "2.0.0")

# Permission
broker = PermissionBroker()
broker.grant("agent-1", Permission(PermissionScope.CAPABILITY_INVOKE, "*"))
check("permission wildcard", broker.has("agent-1", PermissionScope.CAPABILITY_INVOKE, "capability:math"))

# Policy (deterministic, fail-closed)
eng = PolicyEngine(broker=broker)
eng.add_rule(__import__("aios.runtime.policy", fromlist=["PolicyRule"]).PolicyRule(
    "allow-math", lambda r: r.resource.startswith("capability:"),
    PolicyDecision.ALLOW, reason="math"))
res = eng.evaluate(PolicyRequest("agent-1", "invoke", "capability:math", scope=PermissionScope.CAPABILITY_INVOKE))
check("policy allow via permission+rule", res.decision == PolicyDecision.ALLOW)

print("\nRESULT:", "ALL PASS" if ok else "FAILURES PRESENT")
raise SystemExit(0 if ok else 1)
```
