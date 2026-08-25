# Implementation artifact copy — see aios/runtime/workflow/definition.py
# (canonical: WorkflowDefinition.to_execution_plan / from_execution_plan).
# This folder satisfies the STATE_ARTIFACTS mapping (IMPLEMENTING: implementation/).

# TASK-228 changes (Unified ExecutionPlan Contract, M29):
# 1. to_execution_plan now sets plan.metadata["contract"]="unified-execution-plan",
#    plan.metadata["policy_ref"]="governance.unified-gate",
#    plan.metadata["permissions"]=list(self.permissions), and per-step metadata
#    gains explicit "policy_ref" / "permission" / "evidence_ref" fields while
#    keeping backward-compatible keys (scope/resource/command/cwd/timeout/tool_type).
# 2. New classmethod WorkflowDefinition.from_execution_plan(plan) provides the
#    lossless 2-way converter (id/command/cwd/permissions preserved).
# 3. Tests: test_to_execution_plan_carries_governance_fields,
#    test_execution_plan_round_trip_lossless (aios/runtime/tests/test_workflow.py).
