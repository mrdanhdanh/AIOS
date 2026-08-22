# TASK-053 Implementation

## Modules
- `contracts.py` — `AutonomousCycle`, `CycleStatus`, `Decision`, `StopCondition`, `CandidateLearning`.
- `loop.py` — `LoopController` / `AutonomousLoop` orchestrating the cycle; loop-level cost/failure accumulators; deterministic stop conditions.

## Design notes
- The loop *coordinates*; all side-effecting steps are delegated to injected collaborators (observer/actor/evaluator) that go through Policy/Permission/Runtime.
- Budgets (cost, failures, iterations, runtime, no-progress) are loop-level accumulators so stop conditions fire correctly.
- Learning is produced as a candidate and never auto-promoted within the loop.
