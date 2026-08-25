# TASK-236 — Task Breakdown

1. Tạo `aios/autonomous_recovery/lifecycle.py` với `RemediationPhase`, `RemediationReport`, `UnifiedRemediationLifecycle`.
2. Wire detect→diagnose→candidate→simulation→apply→integrity; kill switch hard guard ở bước 0.
3. Verdict cuối fail-closed: success = applied ∧ re_test ∧ ¬rollback ∧ integrity.
4. Tạo `aios/autonomous_recovery/tests/test_lifecycle.py` (4 tests).
5. Chạy full suite + architecture gate + `gate_check.py --task TASK-236`.
6. Cập nhật PLAN/STATS/LOG, commit DONE (Quy tắc 8).
