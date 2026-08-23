# Breakdown — TASK-133

1. `aios/coder/prompt.py` — `PromptTemplate` (immutable version) + `PromptRegistry`.
2. `PromptBuilder.build()` — deterministic render; fail-closed (missing var / unresolved placeholder → T078).
3. `BuiltPrompt` — `content_hash` (sha256, T078) + `evidence_id` (T001 Rule 5).
4. Versioning: (template_id, version) unique (T001 Rule 1); `latest()` helper.
5. Tests (9) theo Test Matrix TASK-133 + architecture guard.
6. Tích hợp: T125→T132 -> T133 (M19).
