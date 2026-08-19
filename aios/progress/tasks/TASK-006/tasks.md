# TASK-006 — Breakdown

- [x] **6.1** Implement `aios/runtime/providers/contract.py` — `ProviderError`, `ProviderErrorCode`, `ModelCapability`, `ModelMetadata` (`supports`/`satisfies`), `UsageRecord.estimate`, `CompletionRequest`, `CompletionResult`, `ProviderAdapter`
- [x] **6.2** Implement `aios/runtime/providers/adapters.py` — `MockProvider` (offline, deterministic, `queue_response`, `call_count`), `OpenAIProvider` (lazy SDK, `UNAVAILABLE` without SDK), `OllamaProvider` (stdlib `urllib` POST)
- [x] **6.3** Implement `aios/runtime/providers/registry.py` — `RegistryError`, `select_model` (deterministic ranking), `ProviderRegistry` (register/list/select/complete/call_count, defaults to MockProvider)
- [x] **6.4** Implement `aios/runtime/providers/__init__.py` — public API for the providers package
- [x] **6.5** Update `aios/runtime/__init__.py` — export the provider API
- [x] **6.6** Write `test_contract.py` — capabilities/satisfies, usage estimate, request defaults, error codes
- [x] **6.7** Write `test_adapters.py` — mock offline/count/queue, openai import-safe, ollama urllib call (monkeypatched)
- [x] **6.8** Write `test_registry.py` — register/list, capability routing, deterministic selection, call accounting, contract-swap
- [x] **6.9** Run full test suite — all TASK-001..006 tests green (266 passed)
- [x] **6.10** Write regression.md — verify TASK-001..005 dependency closure green
