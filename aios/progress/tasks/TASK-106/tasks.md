# Breakdown — TASK-106

1. `BehavioralConformanceReport` dataclass — `behavior_id, independent_observation, aios_expected, conformance, evidence_ref, authority="aios"`.
2. `BehavioralConformanceBridge.bridge` — bridge observation, tính `conformance` fail-closed, ghi provenance.
3. Tests (6) theo Test Matrix T106.
4. Tích hợp Oracle (T105) + Foundation (T104) + Behavioral (T089/T090).
