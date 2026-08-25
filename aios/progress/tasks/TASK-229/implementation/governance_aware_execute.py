# Implementation artifact copy — see aios/cli/workflow_cli.py and
# aios/governance/evidence/store.py (canonical).
# Satisfies STATE_ARTIFACTS mapping (IMPLEMENTING: implementation/).

# TASK-229 changes (Unified Execution Entry-Point, M29):
# 1. _governance_precheck(kernel, plan): explicit PolicyEngine.evaluate +
#    PermissionBroker.has per step (fail-closed) BEFORE any real execution.
# 2. --simulate now calls record_execution_evidence(..., simulated=True) so
#    simulation emits SIMULATED Evidence (same unified ExecutionPlan contract).
# 3. Real exec runs pre-check first; RetryGuard observes FAILED steps and
#    reports auto-stop on repeated identical failure signatures.
# 4. record_execution_evidence gained a `simulated` kwarg (Evidence type
#    SIMULATED, run_id prefixed run-sim-).
# Tests: test_simulate_emits_evidence, test_governance_precheck_denies_missing_permission,
#        test_governance_precheck_allows_granted (aios/cli/tests/test_execute.py).
