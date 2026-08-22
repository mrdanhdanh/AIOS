# TASK-030 — Execution Verification + Evidence + Replay

## Objective
Build the Verification subsystem for the Harness so that `Execution succeeded ≠ Task succeeded`. Verification checks post-conditions, invariants, policy and evidence before producing a verdict (PASS/PASS_WITH_WARNING/FAIL/INCONCLUSIVE). Every run creates a traceable Evidence Package (`Evidence → Run → Execution → Task/Request`) and supports replay without side effects (no real tool calls). Enforces INV-018 Evidence First and INV-019 Verification Before Verdict.

## Scope
### In scope
- Verification contracts: VerificationContract, VerificationRequest, VerificationResult, EvidenceRef, EvidencePackage, ReplayRequest, ReplayResult, Verdict
- Verification pipeline: Preconditions → Postconditions → Invariants → Evidence → Verdict
- Evidence Package: request, normalized-request, plan, execution-graph, events, tool-results, test-results, evaluation, artifacts, verdict with provenance
- Evidence collection and provenance chain
- Replay engine: reconstruct execution state from Evidence Package without side effects
- Fail-closed: missing/insufficient evidence → INCONCLUSIVE (UNKNOWN never promoted to PASS)
- Integration with TASK-029 Harness Kernel (reuse without modifying kernel)

### Out of scope
- Test Harness + Scenario (TASK-031)
- Evaluation Harness (TASK-032)
- Benchmark/Regression/Doctor (TASK-033/034)
- Distributed replay (M7)
- Direct Runtime implementation access (INV-017)

## Deliverables
- `aios/harness/verification.py` — VerificationPipeline, EvidencePackage, VerificationResult, Verdict
- `aios/harness/contracts.py` — shared HarnessSpec/HarnessRun/RunResult (from TASK-029)
- `aios/harness/kernel.py` — HarnessKernel reuse (from TASK-029)
- `aios/harness/tests/test_verification.py` — verification, evidence, replay, fail-closed tests
- `aios/harness/tests/test_kernel.py` — kernel lifecycle tests (shared)

## Acceptance Criteria
- AC-030-01: Execution succeeds but post-condition fails → FAIL (not PASS)
- AC-030-02: Precondition fails → verification does not run normally, verdict FAIL or INCONCLUSIVE per policy
- AC-030-03: Deterministic post-conditions checked (file exists, tests pass, checksum, coverage, expected state)
- AC-030-04: Invariant violation → FAIL
- AC-030-05: Every Harness Run creates retrievable Evidence Package
- AC-030-06: Every evidence traceable: Evidence → Run → Execution → Task/Request
- AC-030-07: Replay from Evidence Package does not call real tools and creates no side effects
- AC-030-08: Verdict not inferred from `exit_code == 0`; must be based on verification evidence
- AC-030-09: Missing/insufficient evidence → INCONCLUSIVE, not PASS (fail-closed)
- AC-030-10: Full regression of dependencies PASS before DONE

## Dependencies
- TASK-029 — Harness Kernel + Contract + Registry + Run

## Governance references
- Rule 1..7 satisfied via `aios/governance/*`.
- INV-017 Harness Isolation, INV-018 Evidence First, INV-019 Verification Before Verdict, INV-020 Evaluation Determinism, INV-021 Release Gate.
