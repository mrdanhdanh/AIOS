"""Tests for the agent role modules.

Confirms the agents operate through governance interfaces only and respect the
lifecycle / review contracts (Rule 3 / Rule 6).
"""

from aios.agents import Critic, Orchestrator, Reviewer, SpecWriter
from aios.agents.spec_writer import SpecInput
from aios.governance.gates import GateComponent, UnifiedTaskGate
from aios.governance.lifecycle import TaskLifecycle


def test_spec_writer_renders_sections():
    spec = SpecInput(
        task_id="TASK-001",
        objective="Governance system",
        scope="All 7 rules",
        deliverables=["registry", "gates"],
        acceptance=["create duplicate -> reject"],
        dependencies=["TASK-000"],
    )
    text = SpecWriter().render(spec)
    assert "## Objective" in text
    assert "## Acceptance Criteria" in text
    assert "## Scope" in text


def test_critic_flags_missing_sections():
    report = Critic().critique("", round_no=1)
    assert report.verdict == "REVISE"
    assert any("Acceptance" in f for f in report.findings)


def test_reviewer_requires_pre_impl_artifacts():
    reviewer = Reviewer()
    bad = reviewer.review({"spec.md": "x"})
    assert bad.approved is False
    good = reviewer.review({
        "spec.md": "x", "critique-1.md": "x",
        "critique-2.md": "x", "tasks.md": "x",
    })
    assert good.approved is True


def test_orchestrator_only_closes_when_gate_passes():
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

    gate = UnifiedTaskGate()
    gate.register("registry", lambda c: GateComponent("registry", True))
    gate.register("dependency", lambda c: GateComponent("dependency", True))
    gate.register("architecture", lambda c: GateComponent("architecture", True))
    gate.register("lifecycle", lambda c: GateComponent("lifecycle", True))
    gate.register("evidence", lambda c: GateComponent("evidence", True))
    gate.register("test_evaluate", lambda c: GateComponent("test_evaluate", True))
    gate.register("regression", lambda c: GateComponent("regression", True))

    orch = Orchestrator(
        ctx=__import__("aios.agents.orchestrator", fromlist=["AgentContext"]).AgentContext(
            lifecycle=lc, gate=gate,
            artifacts={
                "spec.md": "x", "critique-1.md": "x", "critique-2.md": "x",
                "tasks.md": "x", "review.md": "x", "implementation/": "x",
                "test.md": "x", "evaluation.md": "x", "regression.md": "x",
            },
        )
    )
    assert orch.close_if_gate_passes("TASK-001") is True
    assert lc.current("TASK-001") == "DONE"
