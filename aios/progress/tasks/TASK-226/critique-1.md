# Critique 1 — TASK-226

- Spec is concrete and measurable; AC map to deterministic behavior.
- Ensure `RetryGuard` stays in `aios/runtime/` (ARCH-003 compliant: runtime may import runtime). It must NOT be imported by `aios/agents/` directly — agents receive it via capability injection.
- Consider a `reset()` call after a successful step so a prior failure doesn't permanently block a recovered path.
