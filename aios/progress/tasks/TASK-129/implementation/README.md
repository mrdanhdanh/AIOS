# TASK-129 Implementation

Code Review Agent lives in:

- `aios/coder/review.py` — `CodeReviewAgent`, `ReviewReport`, `Finding`, `Severity`, `Verdict`, `ReviewError`.
- Tests trong `aios/coder/tests/test_review.py` (8 tests, Test Matrix TASK-129).

Design:
- `CodeReviewAgent` là pure, I/O-free (T125/AGENTS); chỉ trả `ReviewReport`, không apply/patch (T022 no God Object).
- Review rules (`_FORBIDDEN_PATTERNS`): static/contract checks (subprocess/os.system/eval/print).
- Fail-closed: BLOCK finding → `Verdict.BLOCK` (T078); `policy_ok=False` → `ReviewError` (T113).
- Mọi finding + report ghi `evidence_id` (T001 Rule 5) + `content_hash` (sha256, deterministic).

Integration (import-level, no rewrite):
- `aios.coder.contract` (T125) — agent boundary
- `aios.coder.generation` (T127) / `aios.coder.patch` (T128) — review targets
- `aios.governance.architecture` (ARCH) / `aios.agents.reviewer` (T001)
- `aios.coder.review` (T129) -> `aios.coder.artifact` (T130)
