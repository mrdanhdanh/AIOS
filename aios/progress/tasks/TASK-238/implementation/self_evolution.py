# Implementation artifact copy — see aios/agents/self_evolution.py (canonical).
# Satisfies STATE_ARTIFACTS mapping (IMPLEMENTING: implementation/).

# TASK-238 changes (Self-Evolution Lifecycle, M35):
# - EvolutionPhase: IDLE/PROPOSAL/EXPERIMENT/INDEPENDENT/POLICY/REGRESSION/
#   PROMOTED/REJECTED.
# - SelfEvolutionReport: fail-closed, provenance-carrying result.
# - SelfEvolutionLifecycle.run(...): Proposal -> Experiment -> Harness ->
#   Independent -> Policy -> Regression -> Promote (artifact ONLY, no self-modify).
# Tests: test_lifecycle_promotes_when_all_gates_pass,
#        test_lifecycle_rejects_without_proposal,
#        test_lifecycle_rejects_on_failed_independent,
#        test_lifecycle_rejects_on_failed_regression,
#        test_lifecycle_deterministic_same_inputs.
