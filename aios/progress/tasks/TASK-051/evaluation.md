# TASK-051 — Evaluation

## Acceptance vs Evidence
| AC | File | Status | Evidence |
|----|------|--------|----------|
| AC-051-01 | contracts.py | PASS | AutonomousPlan dataclass with all fields + to_dict |
| AC-051-02 | planner.py | PASS | test_rule_based_plan_generated_without_llm (llm_call_count==0) |
| AC-051-03 | planner.py | PASS | test_llm_only_when_needed (call count==1) |
| AC-051-04 | validation.py | PASS | test_validation_rejects_unknown_capability / _cycle / _side_effect |
| AC-051-05 | planner.py | PASS | test_replan_creates_new_version (version+1, SUPERSEDED) |
| AC-051-06 | planner.py | PASS | test_replan_safety_requires_approval_for_policy_change |
| AC-051-07 | (architecture) | PASS | no subprocess/provider/filesystem import |
| AC-051-08 | (regression) | PASS | full suite green |

## Verdict
DONE — Unified Task Gate PASS.
