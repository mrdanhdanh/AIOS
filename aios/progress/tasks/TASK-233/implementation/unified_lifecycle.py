# Implementation artifact copy — see aios/autonomous_loop/lifecycle.py (canonical).
# Satisfies STATE_ARTIFACTS mapping (IMPLEMENTING: implementation/).

# TASK-233 changes (Unified Autonomous Lifecycle, M31):
# - UnifiedAutonomousLifecycle wraps the existing LoopController (T053) and adds
#   two hard guards: RetryGuard (T226, stable per-goal signature) and
#   KillSwitchController (fail-closed global halt).
# - No new subsystem; pure orchestration over existing autonomous modules.
# Tests: test_unified_lifecycle_runs_through_loop,
#        test_unified_lifecycle_halts_under_killswitch,
#        test_unified_lifecycle_retryguard_autostop.
