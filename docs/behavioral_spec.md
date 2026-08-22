# Behavioral Spec — AIOS 1.x Behavioral Conformance (M13)

- **Status:** PUBLISHED
- **Date:** 2026-08-22
- **Covers:** TASK-089 (Behavioral Conformance), TASK-090 (Harness Coverage +
  Readiness), TASK-091 (Meta-Harness / Verify-the-Verifier), TASK-092 (System
  Readiness vs Harness Trust), TASK-093 (Behavioral Spec + ADR-0008)
- **ADR:** ADR-0008
- **Related ADR:** ADR-Compatibility (M12)
- **Developer reference:** DX (T071) — `aios/devkit/`

## 1. Purpose

M13 establishes **behavioral conformance** for AIOS 1.x: the system must behave
*observably* according to a written spec, the harness must *cover* and *verify*
that behavior, the verifier itself must be *verified*, and a build is only
*certified* when the system is **ready AND the harness is trusted**.

This is a behavioral/harness milestone — it adds no runtime feature. It builds on
Harness (T030/T032), Evidence (T001 Rule 5), Conformance (T087), Certification
(T073), Verification Integrity (T078) and DX (T071).

## 2. Behavior scenarios (T089)

A behavior scenario is **observable** — it describes `given` / `when` / `then` in
terms of externally visible behavior, never internal state.

| Field | Meaning |
|-------|---------|
| `scenario_id` | stable identifier |
| `given` | precondition (observable) |
| `when` | action (observable) |
| `then` | expected observable output |
| `actual_observable` | what the system actually produced |
| `conforms` | `actual == expected` (fail-closed) |
| `evidence_ref` | provenance of the run (T001) |

Module: `aios/behavioral/behavioral.py` (`BehaviorScenario`, `BehaviorHarness`,
`BehaviorConformanceChecker`). Integration: `aios.harness.verification`
(VerificationPipeline, ReplayEngine), `aios.governance.evidence.store`,
`aios.conformance.conformance`.

**Fail-closed:** a deviation from `then`, or a non-observable spec, yields
`conforms = False`. Every run records provenance. Same scenario + same system →
same observable (deterministic).

## 3. Harness coverage + readiness (T090)

The harness surface is mapped to coverage; a build is only **READY** when
coverage meets the threshold (default: full coverage, fail-closed).

| Field | Meaning |
|-------|---------|
| `total_surfaces` | surfaces in scope |
| `harnessed_surfaces` | surfaces the harness covers |
| `coverage_ratio` | `harnessed / total` |
| `gaps` | uncovered surfaces (always reported) |
| `readiness` | `READY` \| `NOT_READY` |

Module: `aios/harness_coverage/coverage.py` (`CoverageMap`, `CoverageChecker`,
`CoverageReport`). Integration: `aios.certification.certifier` (only READY
reports are certified).

**Fail-closed:** coverage below threshold → `NOT_READY` → no certification. Gaps
are never hidden.

## 4. Meta-harness / verify-the-verifier (T091)

The harness is tested by the meta-harness using known-answer and mutation tests,
with the verifier locked per run (T078).

| Check | Requirement |
|-------|-------------|
| known-answer | harness returns the known verdict |
| mutation | a mutated input changes the verdict (detected) |
| verifier lock | verifier version/config locked (T078) |

Module: `aios/meta_harness/meta.py` (`MetaHarness`, `MetaCheck`, `MetaResult`).
Integration: `aios.verification_integrity.integrity` (IntegrityChecker /
VerifierLock), `aios.harness_coverage.coverage` (requires READY to run).

**Fail-closed:** wrong known-answer OR undetected mutation OR unlocked verifier →
meta `FAIL`.

## 5. System readiness vs harness trust (T092)

A build is certified only when **both** conditions hold: the system is ready
(health + gates) **and** the harness is trusted (coverage READY + meta PASS).

| `combined` | Condition |
|------------|-----------|
| `READY_TRUSTED` | system ready AND harness trusted → certify |
| `READY_UNTRUSTED` | system ready but harness untrusted → no certify |
| `NOT_READY` | system not ready → no certify |

Module: `aios/readiness_trust/trust.py` (`TrustGate`, `ReadinessTrust`).
Integration: `aios.harness_coverage.coverage`, `aios.meta_harness.meta`,
`aios.certification.certifier`.

**Fail-closed:** untrusted → never certify. Both required, not just one.

## 6. Integration map

| Capability | Module | Task |
|------------|--------|------|
| Behavioral conformance | `aios/behavioral` | T089 |
| Harness coverage + readiness | `aios/harness_coverage` | T090 |
| Meta-harness | `aios/meta_harness` | T091 |
| Readiness vs trust | `aios/readiness_trust` | T092 |
| Behavioral spec + ADR review | `aios/behavioral_docs` | T093 |

## 7. Developer reference (T071 DX)

Scaffolding and verification tooling for behavioral/harness modules is provided by
the Developer Kit (`aios/devkit/`) and the `aiagent dx` CLI surface (T071). New
behavior scenarios should be added under `aios/behavioral/tests/` and reviewed by
`aios/behavioral_docs` before publication.
