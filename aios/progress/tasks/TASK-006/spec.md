# TASK-006 — Model Contract + Provider Registry

## Objective
Give AIOS a vendor-neutral model access layer so the system is never locked to a
single LLM vendor and can run fully offline for development, testing, and
governance replay. TASK-006 introduces a **model contract** (capabilities,
metadata, cost, offline flag) and a **provider registry** that selects a model
*deterministically* by capability and metadata — no LLM is involved in
selection. A `MockProvider` runs offline with zero external dependencies, so the
entire runtime stack is verifiable without network or third-party SDKs.

## Scope
- **Contract** (`aios.runtime.providers.contract`): capability enum, model
  metadata, usage/cost estimation, completion request/result, and the
  `ProviderAdapter` interface that every vendor must implement.
- **Adapters** (`aios.runtime.providers.adapters`): `MockProvider` (offline,
  deterministic), `OpenAIProvider` (lazy-imports the `openai` SDK; unavailable
  offline without the SDK), `OllamaProvider` (stdlib `urllib` POST to a local
  Ollama server).
- **Registry** (`aios.runtime.providers.registry`): registers providers, lists
  models, and `select_model`/`ProviderRegistry.select` choose a model by
  capability + metadata with a stable, deterministic ranking.

## Deliverables
- `aios/runtime/providers/contract.py` — contract primitives + `ProviderAdapter`.
- `aios/runtime/providers/adapters.py` — `MockProvider`, `OpenAIProvider`,
  `OllamaProvider`.
- `aios/runtime/providers/registry.py` — `ProviderRegistry`, `select_model`,
  `RegistryError`.
- `aios/runtime/providers/__init__.py` — public API for the providers package.
- `aios/runtime/__init__.py` — extended to export the provider API.
- `aios/runtime/providers/tests/test_contract.py`, `test_adapters.py`,
  `test_registry.py`.
- `aios/progress/tasks/TASK-006/` governance artifacts.

## Acceptance Criteria
1. **Provider swappable via contract**: any provider implementing
   `ProviderAdapter` can be registered without changing calling code
   (automated test PASS).
2. **Mock runs offline**: `MockProvider.is_offline()` is `True` and
   `complete()` works with zero external dependencies (automated test PASS).
3. **Capability metadata**: `ModelMetadata.supports`/`satisfies` filters models
   by required capabilities (automated test PASS).
4. **Deterministic selection**: `select_model` returns the same model for the
   same inputs; ranking is offline-first, then lower cost, then model id
   (automated test PASS).
5. **Cost estimation**: `UsageRecord.estimate` computes tokens + cost from
   metadata (automated test PASS).
6. **Call accounting**: the registry tracks `call_count` for deterministic
   first-call-count assertions in later tasks (automated test PASS).
7. **Test suite**: `python -m pytest aios -q` passes with zero failures.
8. **Regression**: TASK-001..005 tests continue to pass (regression gate).

## Dependencies
- TASK-004 (Runtime Services I) — DONE. The provider layer sits on the runtime;
  later it can be wired into the `RuntimeKernel` `Container`.
- TASK-005 (Runtime Services II) — DONE.

## Notes
- Offline-first is a core principle: the registry auto-registers `MockProvider`
  as the zero-config default so the stack boots with no network.
- `OpenAIProvider` and `OllamaProvider` are import-safe (lazy/stdlib) but cannot
  complete without their environment (SDK installed / Ollama server running);
  tests assert their behavior only where the environment allows.
