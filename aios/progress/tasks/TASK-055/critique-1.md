# TASK-055 — Critique 1

## Missing spec sections
- Failure classification keyword map enumerated in `FailureClassifier._KEYWORDS`.
- Circuit breaker fields (failure_count/threshold/cooldown/half_open_probe/last_failure/last_recovery/scope/state) in `circuit.CircuitBreaker`.

## Risks
- Shared keyword "unavailable" could misclassify dependency as transient. Mitigation: ordered keyword map (dependency/policy/state/resource/logical before transient).
- Unverified recovery could be promoted. Mitigation: `attempt` sets NOT_RECOVERED when verify is falsy/raises.

## Verdict
Implementable. Proceed.
