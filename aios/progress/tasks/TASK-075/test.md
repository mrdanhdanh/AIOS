# TASK-075 — Test

## How to run
```
python -m pytest aios/model_router aios/cost_meter -q
```

## What is covered
- **Policy-driven routing (AC1):** `test_route_not_hardcoded_policy_drives_selection`
  asserts COST_OPTIMIZED → cheapest provider, LATENCY_OPTIMIZED → fastest provider.
- **Fail-closed no eligible (AC1):** `test_route_fail_closed_no_eligible`.
- **Provenance (AC6):** `test_route_has_provenance_evidence`, `test_evidence_ref_provenance`.
- **Fallback (AC4 / T055):** `test_provider_down_fallback_route`, `test_unknown_failure_safe_stops`.
- **Deterministic-first (AC5 / Rule 4):** `test_sufficient_intent_llm_call_count_zero`,
  `test_insufficient_intent_llm_fallback_validator`, `test_insufficient_validator_failure_raises`.
- **Deterministic stability (AC7):** `test_same_intent_policy_same_route`.
- **Cost budget (AC2):** `test_budget_exceeded_escalate_stop`, `test_record_per_step_and_goal`.
- **Perf SLO (AC3):** `test_within_slo_passes`, `test_latency_slo_violation`,
  `test_throughput_slo_violation`, `test_check_helpers`.
- **Integration (AC8):** `test_full_flow_model_router_deterministic_recovery`.
