# TASK-075 — Evaluation

## Acceptance criteria results
| AC | Result | Evidence |
|----|--------|----------|
| AC1 — no hardcoded provider (policy-driven) | PASS | `test_route_not_hardcoded_policy_drives_selection` |
| AC2 — cost metered per-step/goal; over budget → escalate/stop | PASS | `test_budget_exceeded_escalate_stop`, `test_record_per_step_and_goal` |
| AC3 — perf within SLO | PASS | `test_within_slo_passes`, `test_latency_slo_violation`, `test_throughput_slo_violation` |
| AC4 — provider down → fallback route (T055) | PASS | `test_provider_down_fallback_route` |
| AC5 — LLM only on INSUFFICIENT (Rule 4) | PASS | `test_sufficient_intent_llm_call_count_zero`, `test_insufficient_intent_llm_fallback_validator` |
| AC6 — route + cost provenance evidence | PASS | `test_route_has_provenance_evidence`, `test_evidence_ref_provenance` |
| AC7 — same intent + policy → same route | PASS | `test_same_intent_policy_same_route` |
| AC8 — integrates Model Router + Deterministic + Recovery | PASS | `test_full_flow_model_router_deterministic_recovery` |
| AC9 — prior milestone tests green; no invariant violations | PASS | existing `aios/model_router/tests/test_router.py`, `test_fallback.py` still pass |

## Test Matrix
| Scenario | Expected | Result |
| -------- | -------- | ------ |
| intent đến | route via policy (not hardcoded) | PASS |
| cost vượt budget | escalate/stop (T067/T068) | PASS (`CostExceeded`) |
| provider hỏng | fallback route (T055) | PASS |
| deterministic SUFFICIENT | LLM call count = 0 (Rule 4) | PASS |
| deterministic INSUFFICIENT | LLM fallback + validator | PASS |
| cùng intent + policy | cùng route (deterministic) | PASS |

## Regression
- Dependency closure (T001, T055, T074): green within `aios/model_router` + `aios/cost_meter`.
