# Implementation artifact copy — see aios/governance/evidence/store.py (canonical).
# Satisfies STATE_ARTIFACTS mapping (IMPLEMENTING: implementation/).

# TASK-234 changes (Automatic Evidence Generation, M32):
# - Evidence gains requirement_id / freshness (1h TTL) / coverage; is_stale().
# - EvidenceStore gains _coverage map + coverage_map / is_requirement_covered.
# - record_execution_evidence passes requirement_id + freshness so every
#   execution auto-emits coverage-tracked, freshness-aware Evidence.
# Tests: test_evidence_freshness_and_stale, test_coverage_map_tracks_requirement.
