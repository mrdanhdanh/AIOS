# TASK-006 — Review

## Pre-implementation checklist
- [x] spec.md present
- [x] critique-1.md present
- [x] critique-2.md present
- [x] tasks.md present

## Notes
Both critiques converge on APPROVE. The vendor-neutral `ProviderAdapter`
contract cleanly decouples AIOS from any single LLM vendor, and the deterministic
selection (`select_model`) needs no LLM to choose a model — supporting the
offline-first and harness-replayable pillars. The `MockProvider` default makes
the stack boot with zero network/config. The only environment-dependent paths
(`OpenAIProvider`/`OllamaProvider.complete()`) are covered by import-safe and
monkeypatched unit tests, and selection routing is validated without forcing
live remote calls. Architecture boundaries (relative imports within
`aios/runtime`) are preserved.

## Decision
- APPROVED
