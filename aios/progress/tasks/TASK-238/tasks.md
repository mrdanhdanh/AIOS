# TASK-238 — Task Breakdown

1. Tạo `aios/agents/self_evolution.py`: `EvolutionPhase`, `SelfEvolutionReport`, `SelfEvolutionLifecycle`.
2. Wire Proposal (SelfImproverAgent) -> Experiment (ExperimentController) -> Independent -> Policy -> Regression -> Promote (artifact only).
3. Đảm bảo no self-modify: Promote chỉ emit `PromotionDecision`.
4. Tạo `aios/agents/tests/test_self_evolution.py` (5 tests).
5. Chạy full suite + architecture gate + `gate_check.py --task TASK-238`.
6. Cập nhật PLAN/STATS/LOG + master spec header (238/238), commit DONE (Quy tắc 8).
