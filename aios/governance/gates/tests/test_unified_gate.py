"""Automated tests for the Unified Task Gate.

This includes a full integration test that wires the seven real governance
submodules and demonstrates the convergence rule:

    Registry AND Dependency AND Architecture AND Lifecycle
    AND Evidence AND Test/Evaluate AND Regression => DONE (else BLOCKED)
"""

import pytest

from aios.governance.architecture import ArchitectureGuard, GateResult as ArchResult
from aios.governance.dependency import DependencyGraph
from aios.governance.deterministic import DeterministicControlPath, Request
from aios.governance.evidence import EvidenceStore, Artifact, Requirement, Run, TaskRecord
from aios.governance.gates import GateComponent, UnifiedTaskGate
from aios.governance.lifecycle import TaskLifecycle
from aios.governance.regression import RegressionOutcome, RegressionRunner
from aios.governance.task_registry import TaskRegistry, TaskStatus


# --------------------------------------------------------------------------- #
# Unit test for the convergence logic
# --------------------------------------------------------------------------- #
def test_unified_gate_passes_only_when_all_pass():
    gate = UnifiedTaskGate()
    gate.register("registry", lambda ctx: GateComponent("registry", True, "ok"))
    gate.register("dependency", lambda ctx: GateComponent("dependency", True, "ok"))

    result = gate.evaluate({})
    assert result.passed is True

    gate.register("architecture", lambda ctx: GateComponent("architecture", False, "agent imports subprocess"))
    result = gate.evaluate({})
    assert result.passed is False
    assert result.components[-1].passed is False


def test_unified_gate_fails_closed_on_exception():
    gate = UnifiedTaskGate()
    gate.register("evidence", lambda ctx: (_ for _ in ()).throw(RuntimeError("boom")))
    result = gate.evaluate({})
    assert result.passed is False
    assert result.components[0].detail.startswith("checker error")


# --------------------------------------------------------------------------- #
# Integration test: a task that satisfies every gate -> DONE
# --------------------------------------------------------------------------- #
def _build_clean_system():
    """Build a registry/graph/lifecycle/evidence/regression for a clean task."""
    reg = TaskRegistry()
    reg.create_task("TASK-001", "Governance", milestone="M0")
    reg.create_task("TASK-002", "Scaffold", milestone="M1", dependencies=["TASK-001"])

    graph = DependencyGraph()
    graph.add_task("TASK-001")
    graph.add_task("TASK-002", ["TASK-001"])

    lc = TaskLifecycle()
    lc.init("TASK-001")
    for state, arts in [
        ("SPECIFIED", ["spec.md"]),
        ("CRITIQUED_1", ["critique-1.md"]),
        ("CRITIQUED_2", ["critique-2.md"]),
        ("BROKEN_DOWN", ["tasks.md"]),
        ("REVIEWED", ["review.md"]),
        ("IMPLEMENTING", ["implementation/"]),
        ("TESTING", ["test.md"]),
        ("EVALUATING", ["evaluation.md"]),
        ("REGRESSION", ["regression.md"]),
        ("READY_TO_CLOSE", []),
    ]:
        lc.transition("TASK-001", state, provided_artifacts=arts)
    lc.close(
        "TASK-001",
        provided_artifacts=[
            "spec.md", "critique-1.md", "critique-2.md", "tasks.md",
            "review.md", "implementation/", "test.md", "evaluation.md",
            "regression.md",
        ],
    )

    store = EvidenceStore()
    store.add_requirement(Requirement("REQ-001", "governance"))
    store.add_task_record(TaskRecord("TASK-001", "REQ-001"))
    store.add_artifact(Artifact("ART-001", "TASK-001", "REQ-001"))
    store.add_run(Run("RUN-001", "ART-001", "TASK-001"))
    store.add_evidence(
        evidence_id="EVID-001", task_id="TASK-001", run_id="RUN-001",
        producer="pytest", type="test-pass", source="x", content="PASS",
        parent_artifact="ART-001",
    )

    def test_runner(tid):
        # Dependency TASK-001 DONE => its tests "pass".
        return RegressionOutcome(tid, passed=True)

    reg_runner = RegressionRunner(test_runner)

    return reg, graph, lc, store, reg_runner


def test_integration_all_rules_pass_yields_done():
    reg, graph, lc, store, reg_runner = _build_clean_system()
    arch_guard = ArchitectureGuard()
    det_path = DeterministicControlPath(llm_fallback=lambda nr: "x", validator=lambda s: True)

    gate = UnifiedTaskGate()

    def registry_check(ctx):
        return GateComponent("registry", reg.exists("TASK-001"), "id unique/immutable")

    def dependency_check(ctx):
        ready, blocker = graph.is_ready("TASK-002", lambda t: "PASS" if t == "TASK-001" else "BLOCKED")
        return GateComponent("dependency", ready, f"blocker={blocker}")

    def architecture_check(ctx):
        res = arch_guard.check(sources=[("from aios.governance import TaskRegistry\n", "aios/agents/orchestrator.py")])
        return GateComponent("architecture", res.passed, f"{len(res.violations)} violations")

    def lifecycle_check(ctx):
        closed = lc.current("TASK-001") == "DONE"
        return GateComponent("lifecycle", closed, "state machine reached DONE")

    def evidence_check(ctx):
        adm = store.is_admissible("EVID-001")
        return GateComponent("evidence", adm, "provenance chain complete")

    def test_evaluate_check(ctx):
        plan = det_path.execute(Request(text="status"))
        return GateComponent("test_evaluate", plan.source == "deterministic", "deterministic path used")

    def regression_check(ctx):
        closure = graph.get_closure("TASK-002")
        res = reg_runner.run("TASK-002", closure)
        return GateComponent("regression", not res.blocked, f"failed={res.failed_task}")

    for fn in [
        registry_check, dependency_check, architecture_check, lifecycle_check,
        evidence_check, test_evaluate_check, regression_check,
    ]:
        pass

    gate.register("registry", registry_check)
    gate.register("dependency", dependency_check)
    gate.register("architecture", architecture_check)
    gate.register("lifecycle", lifecycle_check)
    gate.register("evidence", evidence_check)
    gate.register("test_evaluate", test_evaluate_check)
    gate.register("regression", regression_check)

    result = gate.evaluate({})
    assert result.passed is True, result.summary()
    assert len(result.components) == 7


def test_integration_architecture_failure_blocks():
    """Any single failed component -> unified gate BLOCKED."""
    reg, graph, lc, store, reg_runner = _build_clean_system()
    arch_guard = ArchitectureGuard()
    det_path = DeterministicControlPath(llm_fallback=lambda nr: "x", validator=lambda s: True)

    gate = UnifiedTaskGate()

    gate.register("registry", lambda c: GateComponent("registry", reg.exists("TASK-001")))
    gate.register("dependency", lambda c: GateComponent("dependency", True))
    gate.register("architecture", lambda c: GateComponent(
        "architecture", False, "agent imports subprocess"))
    gate.register("lifecycle", lambda c: GateComponent("lifecycle", lc.current("TASK-001") == "DONE"))
    gate.register("evidence", lambda c: GateComponent("evidence", store.is_admissible("EVID-001")))
    gate.register("test_evaluate", lambda c: GateComponent("test_evaluate", True))
    gate.register("regression", lambda c: GateComponent("regression", True))

    result = gate.evaluate({})
    assert result.passed is False
    assert any(c.name == "architecture" and not c.passed for c in result.components)
