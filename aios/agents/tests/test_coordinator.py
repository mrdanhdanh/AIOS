"""Tests for the CoordinatorAgent (prototype controller)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

import pytest

from aios.agents.coordinator import CoordinatorAgent, CoordinationResult
from aios.agents.spec_writer import SpecInput, SpecWriter
from aios.agents.critic import Critic, CritiqueReport
from aios.agents.reviewer import Reviewer, ReviewReport


@dataclass
class _FakeOrchestrator:
    close_result: bool = True

    def advance(self, task_id, to_state, artifacts=None):
        return to_state

    def can_close(self, task_id):
        return self.close_result

    def close_if_gate_passes(self, task_id):
        return self.close_result


def _spec_input() -> SpecInput:
    return SpecInput(
        task_id="TASK-900",
        objective="Demo objective",
        scope="Bounded scope",
        deliverables=["impl module", "write tests"],
        acceptance=["AC1", "AC2"],
        dependencies=[],
    )


def test_coordinate_happy_path_closes():
    coord = CoordinatorAgent(
        spec_writer=SpecWriter(),
        critic=Critic(),
        reviewer=Reviewer(),
        orchestrator=_FakeOrchestrator(close_result=True),
    )
    result = coord.coordinate("TASK-900", _spec_input())
    assert isinstance(result, CoordinationResult)
    assert result.approved is True
    assert result.closed is True
    assert "spec.md" in result.artifacts
    assert "critique-1.md" in result.artifacts
    assert "critique-2.md" in result.artifacts
    assert "tasks.md" in result.artifacts
    step_names = [s.name for s in result.steps]
    assert step_names == ["spec", "critique-1", "critique-2", "breakdown", "review", "orchestrate"]


def test_coordinate_fail_closed_when_review_rejects():
    class _RejectReviewer(Reviewer):
        def review(self, artifacts):
            return ReviewReport(approved=False, notes=["forced reject"])

    coord = CoordinatorAgent(
        spec_writer=SpecWriter(),
        critic=Critic(),
        reviewer=_RejectReviewer(),
        orchestrator=_FakeOrchestrator(close_result=True),
    )
    result = coord.coordinate("TASK-900", _spec_input())
    assert result.approved is False
    assert result.closed is False
    # orchestrate step must not have run / closed
    assert all(s.name != "orchestrate" for s in result.steps)


def test_coordinate_deterministic_same_input_same_output():
    def build():
        return CoordinatorAgent(
            spec_writer=SpecWriter(),
            critic=Critic(),
            reviewer=Reviewer(),
            orchestrator=_FakeOrchestrator(close_result=True),
        ).coordinate("TASK-900", _spec_input())

    r1, r2 = build(), build()
    assert r1.to_dict() == r2.to_dict()
