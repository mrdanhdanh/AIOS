# Breakdown — TASK-129

1. `aios/coder/review.py` — `CodeReviewAgent` (I/O-free, capability-injected, T125).
2. Review rules (`_FORBIDDEN_PATTERNS`): static/contract checks (subprocess/os.system/eval/print).
3. `Finding` (severity + evidence_id) + `ReviewReport` (verdict, content_hash).
4. Fail-closed: BLOCK finding → `Verdict.BLOCK` (T078); `policy_ok=False` → `ReviewError` (T113).
5. Deterministic: cùng content → cùng verdict + content_hash.
6. Tests (8) theo Test Matrix TASK-129 + architecture guard.
7. Tích hợp: T127/T128 -> T129 -> T130 (M19).
