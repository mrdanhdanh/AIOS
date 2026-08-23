# TASK-170 — Prompt Injection Tester + Untrusted Artifact Isolation

## Objective
Two capabilities: probe prompt-injection sanitization and verify untrusted-artifact isolation. Deterministic, fail-closed: unsanitized injection or non-isolated untrusted artifact is BREACH.

## Scope
- Package: `aios/adversarial/` (unknown/infra layer, deterministic-first, fail-closed, provenance-bearing).
- Module: `aios/adversarial/prompt_injection.py` — class `PromptInjectionTester / UntrustedArtifactIsolation`.
- No LLM, no I/O, no provider/filesystem imports (ARCH-001..004 N/A for unknown layer).

## Deliverables
- Implementation + contract/schema + deterministic tests + evidence + documentation.

## Acceptance Criteria
- PromptInjectionAttack/Result and ArtifactIsolationAttack/Result immutable with non-empty attack_id (Rule 1).
- PromptInjectionTester: breached = injection_present AND not sanitized.
- UntrustedArtifactIsolation: breached = untrusted AND not isolated.
- Empty attack_id or non-attack input raises AdversarialError (fail-closed).
- BREACH never promoted to PASS (T078); result_id deterministic.

## Dependencies
- T001 (Evidence/Rule 1/5/6), T078 (Integrity), T164 (Verification Harness), T033 (Regression).
