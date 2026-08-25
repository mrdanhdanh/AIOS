# Implementation artifact copy — see aios/governance/evidence/store.py (canonical).
# Satisfies STATE_ARTIFACTS mapping (IMPLEMENTING: implementation/).

# TASK-235 changes (Evidence Quality & Integrity, M32):
# - detect_conflicts(): same-requirement status disagreement (excludes UNKNOWN/STALE).
# - replay(run_id): reconstruct evidence from a run.
# - quality_score(producer_trust): trust * freshness * verification in [0,1].
# - is_valid_for_evaluation(): rejects UNKNOWN / STALE / conflicted evidence.
# Tests: test_detect_conflicts_finds_disagreement, test_replay_reconstructs_from_run,
#        test_quality_score_and_validity.
