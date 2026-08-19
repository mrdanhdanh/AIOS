# TASK-004 — Critique 1

## Strengths
- Five independent services with clear boundaries, each testable in isolation —
  matches the "independent services + interfaces + tests" deliverable.
- Deterministic-first policy engine (Rule 4) is explicit: `INSUFFICIENT`
  escalation instead of silent LLM fallback. Good.
- Audit trail is genuinely tamper-evident (hash chaining) rather than a plain
  log. Good for provenance (Rule 5).
- Artifact integrity is enforced on write, not just on read.

## Risks / Gaps
1. **Policy `INSUFFICIENT` handling**: the spec says "Policy decides before
   Execution". `INSUFFICIENT` must not be treated as a silent allow by callers.
   The contract should state callers MUST block/escalate on `INSUFFICIENT`.
2. **Permission wildcard semantics**: `Permission.matches` must support prefix
   wildcards (`workflow:*`) in addition to full `*` and exact match, or real
   resource patterns become unworkable.
3. **Context store parent linking**: lazy parent linking (parent not yet
   stored) should be tolerated but documented; `resolve_chain` must not raise.
4. **Thread safety**: all five stores use locks; the spec doesn't explicitly
   require concurrency but the runtime will be concurrent, so it must be safe.

## Required Revisions
- Document `INSUFFICIENT` as "must block or escalate" in the policy contract
  (done — docstring + test).
- `Permission.matches` supports prefix wildcards `prefix*` (done).
- `ContextStore.resolve_chain` tolerates missing parents (done).
- All stores are lock-guarded (done).
