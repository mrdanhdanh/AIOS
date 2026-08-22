# Breakdown — TASK-105

1. `OracleResult` dataclass — `oracle_id, invariant_ref, independent_verdict, aios_policy_verdict, evidence_ref, authority="aios"`.
2. `InvariantMapping` — `register/resolve/is_mapped` (invariant → oracle check).
3. `IndependentVerificationOracle.query` — gọi oracle, bridge evidence (T104), tính `aios_policy_verdict` fail-closed.
4. Tests (6) theo Test Matrix T105.
5. Tích hợp Foundation (T104) + Harness + Integrity + Evidence.
