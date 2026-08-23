# TASK-133 — Prompt Architecture + PromptBuilder + Versioning

## Objective
Triển khai **Prompt Architecture + PromptBuilder + Versioning** (M19) như một năng lực có contract, evidence và harness riêng — versioned prompt templates, deterministic builder render template với variables, immutable version registry (T001 Rule 1). Mọi built prompt có `content_hash` (T078) + provenance (T001 Rule 5).

## Scope
**In scope:** `aios/coder/prompt.py` — `PromptRegistry`, `PromptTemplate`, `PromptBuilder`, `BuiltPrompt`, `PromptError`.
**Out of scope:** file safety (T134).

## Deliverables
- `aios/coder/prompt.py` implementation + contract/schema.
- Unit + Contract + Integration + Architecture + Regression tests trong `aios/coder/tests/test_prompt.py`.
- Tích hợp: T125→T132 -> T133 (M19).

## Acceptance Criteria
- AC của task PASS; UNKNOWN không được nâng thành PASS (fail-closed, T078).
- Evidence có provenance (T001 Rule 5).
- Regression của dependency PASS; không vi phạm invariants.

## Dependencies
- T125..T132 -> T133.
- T001 (Rule 1/5), T078 (Integrity).

## Governance references
- Rule 1..7 via `aios/governance/*`. `coder` là `unknown` (infra) layer.
