# TASK-133 Implementation

Prompt Architecture + PromptBuilder + Versioning lives in:

- `aios/coder/prompt.py` — `PromptRegistry`, `PromptTemplate`, `PromptBuilder`, `BuiltPrompt`, `PromptError`.
- Tests trong `aios/coder/tests/test_prompt.py` (9 tests, Test Matrix TASK-133).

Design:
- `PromptRegistry` — immutable (template_id, version) pairs (T001 Rule 1); `register()` reject duplicate; `latest()` helper.
- `PromptBuilder.build()` — deterministic render; fail-closed (T078): missing variable / unresolved placeholder → `PromptError`.
- `BuiltPrompt` ghi `content_hash` (sha256) + `evidence_id` (T001 Rule 5). Same input → same hash (deterministic).

Integration (import-level, no rewrite):
- `aios.coder.contract` (T125) — agent boundary
- `aios.governance.evidence` (T001) / `aios.verification_integrity` (T078)
- `aios.coder.prompt` (T133) -> `aios.coder.filesafety` (T134)
