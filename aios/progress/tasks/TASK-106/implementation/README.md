# TASK-106 Implementation

Behavioral Conformance Bridge lives in `aios/independent_harness/`:

- `aios/independent_harness/behavioral_bridge.py` — `BehavioralConformanceReport`, `BehavioralConformanceBridge`.
- Tests trong `aios/independent_harness/tests/test_independent_harness.py` (Test Matrix T106).

Integration (import-level, no rewrite):
- `aios.independent_harness.foundation` (HarnessRegistry, EvidenceIngestBoundary, PolicyAuthority) — T104
- `aios.independent_harness.oracle` (IndependentVerificationOracle) — T105
- `aios.behavioral.behavioral` (BehaviorScenario, BehaviorSurface) — T089/T090
- `aios.verification_integrity` (VerdictClass) — T078
