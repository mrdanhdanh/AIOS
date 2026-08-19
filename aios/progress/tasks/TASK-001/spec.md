# TASK-001 — Task Governance System (Project Governance Foundation)

## Objective
Turn the 7 general rules from the master specification into a self-verifying
**Task Governance System** before any runtime exists. This is the control plane
for the whole AIOS development system: from TASK-002 onward, developers/agents
do not need to "remember" the 7 rules — the system enforces compliance.

## Scope
- 7 governance components, each with automated tests (not just convention):
  1. Task Registry (Rule 1)
  2. Dependency Graph (Rule 2)
  3. Architecture Guard (Rule 3)
  4. Deterministic Control Path (Rule 4)
  5. Evidence Store (Rule 5)
  6. Task State Machine (Rule 6)
  7. Regression Gate (Rule 7)
- Unified Task Gate converging all 7 rules.
- Progress structure + agent roles + CLIs.

## Deliverables
- `aios/governance/` package: 7 modules + unified gate + automated pytest tests.
- `aios/progress/` with `PLAN.md / LOG.md / STATS.md` and task folders
  (`_TEMPLATE/` and `TASK-001/` executing the full lifecycle).
- `docs/PLAN.md`, `AGENTS.md`, `aios/agents/` (orchestrator / spec-writer /
  critic / reviewer).
- CLI: `parse_spec.py` (registry from master spec, validate Rule 1/2) and
  `gate_check.py` (run unified gate).

## Acceptance Criteria
- Registry: create task with existing ID -> REJECT (test PASS).
- Dependency: run when dependency not PASS -> BLOCK; cyclic -> BLOCK (test PASS).
- Architecture: agent imports subprocess/provider directly -> ARCH GATE FAIL (test PASS).
- Deterministic: rule decides -> LLM call count 0; rule insufficient -> LLM called & validated (test PASS).
- Evidence: each PASS traceable provenance chain (test PASS).
- State Machine: missing artifact -> DONE REJECT (test PASS).
- Regression: failure in closure -> BLOCKED (test PASS).
- New session reading docs/PLAN.md + AGENTS.md + aios/progress/README.md can continue without chat memory.

## Dependencies
- None (M0 foundation).
