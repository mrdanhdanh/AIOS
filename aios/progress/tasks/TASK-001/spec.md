# TASK-001 — Task Governance System (Project Governance Foundation)

## Objective
Biến 7 Quy tắc chung thành hệ thống kiểm soát task tự kiểm chứng (self-verifying Task
Governance System) trước khi có runtime.

## Scope
### In scope
- 7 governance components với automated tests (registry, dependency, architecture,
  deterministic, evidence, lifecycle, regression) + unified gate.
- `aios/progress/` system (PLAN/LOG/STATS, task folders, template).
- `docs/PLAN.md`, `AGENTS.md`, `aios/agents/` roles.
- CLI: `parse_spec.py` (Rule 1/2), `gate_check.py` (unified gate).
### Out of scope
- Runtime implementation (TASK-002+).
- Kiến trúc guard thực thi trên toàn bộ codebase (sẽ mở rộng ở TASK-016).

## Deliverables
- `aios/governance/` package (8 modules + tests).
- `aios/progress/` (PLAN.md, LOG.md, STATS.md, tasks/, registry).
- `docs/PLAN.md`, `AGENTS.md`, `aios/agents/*`.

## Acceptance Criteria
- Registry: duplicate ID → REJECT (test PASS).
- Dependency: missing/cyclic → BLOCK (test PASS).
- Architecture: agent import subprocess/provider → FAIL (test PASS).
- Deterministic: rule decides → LLM call 0; fallback → validated (test PASS).
- Evidence: PASS truy được provenance chain (test PASS).
- State Machine: thiếu artifact → DONE REJECT (test PASS).
- Regression: failure in closure → BLOCKED (test PASS).

## Dependencies / Gate
- M0, không dependency.

## Invariants (General Rules)
- Rule 1 (immutable ID) · Rule 2 (dependency/milestone) · Rule 3 (no bypass)
- Rule 4 (deterministic-first) · Rule 5 (evidence provenance) · Rule 6 (lifecycle) · Rule 7 (regression)
