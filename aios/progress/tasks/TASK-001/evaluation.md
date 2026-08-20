# TASK-001 — Evaluation

## Acceptance criteria results
| AC | Result | Evidence |
|----|--------|----------|
| Registry: duplicate ID -> REJECT | PASS | `tests/test_registry.py::test_duplicate_id_is_rejected` |
| Dependency: not-PASS dep -> BLOCK | PASS | `tests/test_dependency.py::test_task_runs_when_dependency_not_passed_is_blocked` |
| Dependency: cycle -> BLOCK | PASS | `tests/test_dependency.py::test_cyclic_dependency_is_detected_and_blocks` |
| Architecture: agent imports subprocess -> FAIL | PASS | `tests/test_architecture.py::test_agent_importing_subprocess_fails` |
| Architecture: agent imports provider -> FAIL | PASS | `tests/test_architecture.py::test_agent_importing_provider_fails` |
| Architecture: agent imports filesystem -> FAIL | PASS | `tests/test_architecture.py::test_agent_importing_filesystem_fails` |
| Deterministic: rule decides -> LLM calls 0 | PASS | `tests/test_deterministic.py::test_deterministic_rule_avoids_llm` |
| Deterministic: LLM fallback validated | PASS | `tests/test_deterministic.py::test_llm_only_called_when_insufficient` |
| Deterministic: invalid LLM output rejected | PASS | `tests/test_deterministic.py::test_llm_output_failing_validation_is_rejected` |
| Evidence: provenance chain complete | PASS | `tests/test_evidence.py::test_provenance_chain_is_complete_when_seeded` |
| State machine: missing artifact -> DONE REJECT | PASS | `tests/test_lifecycle.py::test_missing_artifact_blocks_done` |
| Regression: closure failure -> BLOCKED | PASS | `tests/test_regression.py::test_closure_failure_blocks_task` |
| New session can continue w/o chat memory | PASS | `docs/PLAN.md` + `docs/AGENTS.md` + `aios/progress/README.md` |

## Regression
- Dependency closure of TASK-001 is empty -> green by definition.
- Full suite (`python -m pytest aios/governance -q`) is green (39 tests: 6 registry + 5 dependency + 4 lifecycle + 3 evidence + 6 architecture + 4 deterministic + 3 regression + 4 unified gate + 4 agents).
