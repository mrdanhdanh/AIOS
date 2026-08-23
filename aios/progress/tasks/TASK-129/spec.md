# TASK-129 — Code Review Agent

## Objective
Triển khai **Code Review Agent** (M19) như một năng lực có contract, evidence và harness riêng — review code artifact/patch (T127/T128) theo contract, I/O-free, capability-injected, không trở thành God Object. TASK-129 là **review agent, không phải runtime mới** (dựa trên Coder Agent T125 + Patch T128 + Architecture Guard ARCH + Reviewer T001/AGENTS).

## Scope
**In scope:** `aios/coder/review.py` — `CodeReviewAgent`, `ReviewReport`, `Finding`, `Severity`, `Verdict`, `ReviewError`.
**Out of scope:** coding artifact/evidence (T130).

## Deliverables
- `aios/coder/review.py` implementation + contract/schema.
- Unit + Contract + Integration + Architecture + Regression tests trong `aios/coder/tests/test_review.py`.
- Tích hợp: T127/T128 -> T129 -> T130 (M19).

## Acceptance Criteria
- Review Agent review artifact/patch (T127/T128) theo contract, I/O-free.
- Agent không import forbidden module (ARCH-001..004) → BLOCK.
- Finding block → verdict BLOCK (fail-closed, T078).
- Mọi finding có provenance (T001 Rule 5).
- Cùng artifact + rules → cùng verdict (deterministic).
- Review chỉ đề xuất, không bypass policy (T022).
- Tích hợp được với Coder Agent + Patch + Architecture + Reviewer + Evidence.
- Regression của các milestone trước PASS; không vi phạm invariants.

## Dependencies
- T127 (Generation), T128 (Patch) -> T129 -> T130.
- T001 (Rule 1/5), T022 (Orchestrator v2), T078 (Integrity), T113 (Policy), ARCH (Guard).

## Governance references
- Rule 1..7 via `aios/governance/*`. `coder` là `unknown` (infra) layer.
