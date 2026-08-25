"""Tests for SelfImproverAgent (TASK-225)."""

from dataclasses import dataclass

from aios.agents.self_improver import (
    SelfImproverAgent,
    ImprovementProposal,
    SelfImproverResult,
)


@dataclass
class FakeEvidence:
    evidence_id: str
    task_id: str
    producer: str
    type: str
    status: str


class FakeStore:
    def __init__(self, records):
        self._records = records

    def list_all(self):
        return self._records


class FakeRegistry:
    def get_task(self, tid):
        return None

    def list_tasks(self):
        return []


def _records():
    return [
        FakeEvidence("e1", "TASK-001", "orchestrator", "test", "FAIL"),
        FakeEvidence("e2", "TASK-001", "orchestrator", "test", "FAIL"),
        FakeEvidence("e3", "TASK-002", "orchestrator", "test", "FAIL"),
        FakeEvidence("e4", "TASK-003", "runtime", "eval", "PASS"),
    ]


def test_pure_no_side_effects():
    agent = SelfImproverAgent(FakeStore(_records()), FakeRegistry())
    res = agent.analyze()
    assert res.analyzed_tasks == 3
    assert any(p.target_module == "orchestrator" for p in res.proposals)


def test_fail_closed_no_signals():
    agent = SelfImproverAgent(FakeStore([]), FakeRegistry())
    assert agent.propose_next() is None


def test_deterministic():
    a = SelfImproverAgent(FakeStore(_records()), FakeRegistry()).analyze()
    b = SelfImproverAgent(FakeStore(_records()), FakeRegistry()).analyze()
    assert a.to_dict() == b.to_dict()


def test_propose_next_returns_best():
    p = SelfImproverAgent(FakeStore(_records()), FakeRegistry()).propose_next()
    assert isinstance(p, ImprovementProposal)
    assert p.confidence >= 0.6
