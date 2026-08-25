# Implementation artifact copy — see aios/autonomous_recovery/lifecycle.py (canonical).
# Satisfies STATE_ARTIFACTS mapping (IMPLEMENTING: implementation/).

# TASK-236 changes (Unified Remediation Lifecycle, M33):
# - RemediationPhase: IDLE/DETECTED/DIAGNOSED/CANDIDATE/SIMULATED/VERIFIED/
#   APPLIED/ROLLED_BACK/HALTED/DONE.
# - RemediationReport: fail-closed, provenance-carrying result.
# - UnifiedRemediationLifecycle.run(...): Detect -> Diagnose -> Candidate ->
#   Risk Score -> Simulation -> Independent Verification -> Approval/Auto-Apply
#   -> Rollback if FAIL -> Integrity -> (Kill Switch hard guard).
# Tests: test_lifecycle_runs_to_done_with_low_risk_candidate,
#        test_lifecycle_escalates_without_traceable_diagnosis,
#        test_lifecycle_halts_under_kill_switch,
#        test_lifecycle_deterministic_same_inputs.
