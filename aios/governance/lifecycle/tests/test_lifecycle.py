"""Automated tests for the Task State Machine gate (Rule 6)."""

import pytest

from aios.governance.lifecycle import LifecycleError, TaskLifecycle


def test_normal_transition_requires_artifact():
    lc = TaskLifecycle()
    lc.init("TASK-001")
    with pytest.raises(LifecycleError):
        # SPECIFIED needs spec.md
        lc.transition("TASK-001", "SPECIFIED", provided_artifacts=[])
    lc.transition("TASK-001", "SPECIFIED", provided_artifacts=["spec.md"])
    assert lc.current("TASK-001") == "SPECIFIED"


def test_full_lifecycle_happy_path():
    lc = TaskLifecycle()
    lc.init("TASK-001")
    steps = [
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
    ]
    for state, arts in steps:
        lc.transition("TASK-001", state, provided_artifacts=arts)
    assert lc.current("TASK-001") == "READY_TO_CLOSE"
    # Close requires all mandatory artifacts across the lifecycle.
    all_arts = [a for _, arts in steps for a in arts]
    lc.close("TASK-001", provided_artifacts=all_arts)
    assert lc.current("TASK-001") == "DONE"


def test_missing_artifact_blocks_done():
    """Rule 6: missing one mandatory artifact -> DONE is REJECTED."""
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
    # Provide everything EXCEPT evaluation.md.
    provided = [
        "spec.md", "critique-1.md", "critique-2.md", "tasks.md",
        "review.md", "implementation/", "test.md", "regression.md",
    ]
    assert lc.can_close("TASK-001", provided) is False
    with pytest.raises(LifecycleError):
        lc.close("TASK-001", provided_artifacts=provided)


def test_backwards_transition_rejected():
    lc = TaskLifecycle()
    lc.init("TASK-001")
    lc.transition("TASK-001", "SPECIFIED", provided_artifacts=["spec.md"])
    with pytest.raises(LifecycleError):
        lc.transition("TASK-001", "PLANNED", provided_artifacts=[])
