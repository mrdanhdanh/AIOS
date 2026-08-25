# Implementation artifact copy — see aios/dashboard/control_center.py (canonical).
# Satisfies STATE_ARTIFACTS mapping (IMPLEMENTING: implementation/).

# TASK-237 changes (Unified Control Center Dashboard, M34):
# - PlaneSnapshot: per-plane state (ok | empty | error), fail-isolated.
# - ControlCenterView: unified read-only snapshot (system_health + 14 planes).
# - ControlCenterAggregator: collects every plane independently; a failing
#   plane yields an error entry instead of crashing the snapshot.
# - aios/api/routers/control_center.py: GET /api/v1/control-center (read-only).
# Tests: test_aggregator_returns_all_14_planes, test_aggregator_collects_ok_plane,
#        test_aggregator_isolates_plane_errors, test_aggregator_deterministic,
#        test_control_center_endpoint_returns_all_planes,
#        test_control_center_is_read_only_snapshot.
