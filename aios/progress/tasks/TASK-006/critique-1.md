# TASK-006 — Critique 1

## Strengths
- Clean vendor-neutral contract: `ProviderAdapter` defines the only seam AIOS
  depends on; concrete vendors (OpenAI, Ollama, Mock) are pluggable.
- Offline-first done right: `MockProvider` is pure-Python, deterministic, and is
  the default registered provider — the whole stack boots with zero config.
- Selection is fully deterministic (capability filter -> prefer -> offline-first
  -> cost -> model-id tiebreak), so no part of the system needs an LLM to choose
  a model. This keeps the harness replayable and the cost gates stable.
- Cost accounting via `UsageRecord.estimate` + registry `call_count` gives a
  foundation for the deterministic LLM-call-count assertions required later.

## Risks / Gaps
1. **Adapter completion side-effects**: `OpenAIProvider`/`OllamaProvider`
   `complete()` perform network I/O and will raise when unavailable. The
   registry must not assume every selected provider can complete offline. Tests
   must validate *selection routing* rather than forcing live remote calls in a
   network-less CI environment.
2. **Registry call log**: `call_count` currently counts `complete()` invocations
   at the registry boundary. Confirm that is the intended unit for later
   first-call-count assertions (vs per-provider counts).
3. **Capability vocabulary**: the `ModelCapability` enum must stay in sync with
   what downstream tasks (memory embeddings, decision pipelines) actually need.

## Required Revisions
- Ensure `select_model` is deterministic and documented with its ranking order
  (done).
- Make adapter `complete()` failures raise a typed `ProviderError` with a clear
  `ProviderErrorCode` so callers can branch (done).
- Default registry to offline `MockProvider` (done).
