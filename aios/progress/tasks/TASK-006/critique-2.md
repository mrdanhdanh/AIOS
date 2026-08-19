# TASK-006 — Critique 2

## Convergence with Critique 1
Both critiques converge on the vendor-neutral contract and the importance of
deterministic, capability-driven selection that needs no LLM. This critique adds
integration-readiness checks for downstream M1 tasks.

## Additional Observations
1. **Kernel wiring**: the provider registry should be registerable into the
   `RuntimeKernel` `Container` (TASK-005) so orchestration/task code resolves it
   by type without import coupling — consistent with the composition-root pattern
   TASK-005 established.
2. **Offline default is the replay anchor**: because `MockProvider` is the
   default, the harness governance replay (deterministic control path) can run
   end-to-end without network — this supports the M1 "Harness-Verified" pillar.
3. **Cost gate foundation**: `UsageRecord.estimate` + `call_count` are the seeds
   of the deterministic cost/quota gate that later tasks (decision pipeline,
   regression) will build on.
4. **No external deps in the contract**: `contract.py` and `registry.py` are
   pure-Python + stdlib; only `OpenAIProvider` optionally touches a third-party
   SDK (lazy). Good for the offline-first constraint.

## Required Revisions
- Keep `adapters.py` import-safe (lazy `openai`, stdlib `urllib` for Ollama)
  (done).
- Keep selection pure and deterministic (done).
- Expose the provider API from `aios.runtime.__init__` for one import surface
  (done).
