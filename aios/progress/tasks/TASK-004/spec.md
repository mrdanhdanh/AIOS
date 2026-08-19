# TASK-004 — Runtime Services I

## Objective
Build the five independent runtime control services that every later M1 task
(TASK-005 through TASK-009) wires together: **Context** (six context types +
hierarchical store), **Audit** (append-only, hash-chained trail), **Artifact**
(content-addressable blobs with checksum + SemVer), **Permission** (scopes +
broker), and **Policy** (deterministic pre-check decided before execution).

These services establish the runtime as the control substrate: agents/workers
may only reach capabilities through it, and no service may bypass the typed
contract layer. The deterministic-first principle (Rule 4) is enforced by the
policy engine, which decides via rules + permissions and only returns
`INSUFFICIENT` (never auto-calling an LLM) when the deterministic path is
exhausted.

## Scope
- **Context** (`aios.runtime.context`): 6 context types — REQUEST, AGENT,
  WORKFLOW, CAPABILITY, TOOL, EXECUTION; hierarchical `ContextStore` with
  parent linkage and chain resolution.
- **Audit** (`aios.runtime.audit`): hash-chained `AuditTrail` with tamper-
  evident integrity verification and query by actor/action/context/status.
- **Artifact** (`aios.runtime.artifact`): `Artifact` with SHA-256 checksum and
  SemVer version; `ArtifactStore` enforces integrity on write and resolves
  latest version.
- **Permission** (`aios.runtime.permission`): `PermissionScope` enum + wildcard
  `Permission` + `PermissionBroker`.
- **Policy** (`aios.runtime.policy`): deterministic `PolicyEngine` with ordered
  rule table; `DENY` precedence; permission gate; `INSUFFICIENT` escalation.

## Deliverables
- `aios/runtime/context.py` — ContextType, RuntimeContext, ContextStore.
- `aios/runtime/audit.py` — AuditStatus, AuditEvent, AuditTrail.
- `aios/runtime/artifact.py` — Artifact, ArtifactStore.
- `aios/runtime/permission.py` — PermissionScope, Permission, PermissionBroker.
- `aios/runtime/policy.py` — PolicyDecision, PolicyRequest, PolicyRule,
  PolicyResult, PolicyEngine.
- `aios/runtime/__init__.py` — public API exports.
- `aios/runtime/tests/test_context.py`, `test_audit.py`, `test_artifact.py`,
  `test_permission.py`, `test_policy.py`.
- `aios/progress/tasks/TASK-004/` governance artifacts.

## Acceptance Criteria
1. **Six context types**: `ContextType` enumerates exactly the 6 required types
   (automated test PASS).
2. **Context hierarchy**: contexts link to parents; `resolve_chain` walks to
   root (automated test PASS).
3. **Audit tamper-evidence**: altering or reordering events breaks
   `verify_integrity()` (automated test PASS).
4. **Artifact integrity**: checksum verified on write; mismatch rejected
   (automated test PASS).
5. **Artifact versioning**: `versions()` orders by SemVer; `get_latest()`
   returns highest (automated test PASS).
6. **Permission wildcard**: `"workflow:*"` grants `"workflow:demo"`; `"*"`
   grants any resource (automated test PASS).
7. **Policy pre-check before execution**: request lacking permission -> `DENY`
   (fail-closed); matching `DENY` rule overrides `ALLOW` (automated test PASS).
8. **Deterministic-first**: policy returns a repeatable decision without any LLM
   call path; unknown requests return `INSUFFICIENT` (automated test PASS).
9. **Test suite**: `python -m pytest aios -q` passes with zero failures.
10. **Regression**: all TASK-001/002/003 tests continue to pass (regression gate).

## Dependencies
- TASK-003 (Kernel Foundations) — DONE. Uses `aios.core.version.SemVer`,
  `aios.core.events`, `aios.core.container` primitives; respects layering
  (runtime never imports agent/orchestrator).

## Governance references
- Rule 1..7 satisfied via `aios/governance/*`. Architecture enforced via
  relative imports within `aios/runtime/` (no upward layer imports).
