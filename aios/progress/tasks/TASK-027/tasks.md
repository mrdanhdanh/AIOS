# TASK-027 — Breakdown

## Steps
1. Create `aios/execution_graph/contracts.py` — ExecutionGraph, GraphNode, GraphEdge, NodeState contracts
2. Create `aios/execution_graph/compiler.py` — ExecutionGraphCompiler pipeline: Schema Validation → Node/Edge Materialization → Reference Validation → Duplicate/Self-loop/Cycle Detection → Entry/Terminal Detection → Topological Order
3. Implement acyclic enforcement (DFS/Kahn), self-loop rejection, missing node detection, duplicate edge normalization, conditional dependency support
4. Create `aios/execution_graph/tests/test_compiler.py` — 14 tests (compilation, cycle detection, self-loop, missing node, topological order, parallelism boundary)
5. Run architecture guard — verify no Graph Compiler → Scheduler/Resource direct coupling
6. Run full suite — 1707/1707 PASS (14 new), no regressions

## Dependencies
- TASK-026 Planning Engine (ExecutionPlan input)

## Exit Criteria
- All AC-027 PASS, gate PASS, no regressions
