"""Tests for DecisionPipeline — AC-010-02..08 (TASK-010)."""

import pytest

from aios.orchestrator.decision_pipeline import DecisionPipeline, DecisionPipelineError
from aios.orchestrator.planner import Planner, ValidationError
from aios.orchestrator.workflow_matcher import WorkflowLibrary


class TestDecisionPipeline:
    def test_deterministic_no_llm(self):
        pipe = DecisionPipeline()
        result = pipe.execute({"text": "run tests"})
        assert result.source == "deterministic"
        assert result.llm_call_count == 0
        assert pipe.llm_call_count == 0
        assert result.plan is not None
        assert len(result.plan.nodes) == 1

    def test_workflow_reuse_no_planner(self):
        lib = WorkflowLibrary()
        lib.register("crud-generator-v1", capabilities=["api.create", "db.migrate"])
        from aios.orchestrator.workflow_matcher import WorkflowMatcher

        pipe = DecisionPipeline(workflow_matcher=WorkflowMatcher(library=lib))
        result = pipe.execute({"text": "create crud api"})
        assert result.source == "workflow"
        assert result.llm_call_count == 0
        assert len(result.plan.nodes) == 2

    def test_planner_fallback_only_when_needed(self):
        planner = Planner(llm_callable=lambda x: "cap_a,cap_b", validator=lambda s: True)
        pipe = DecisionPipeline(planner=planner)
        result = pipe.execute({"text": "do something completely unknown xyz123"})
        assert result.source == "llm"
        assert result.llm_call_count == 1
        assert pipe.llm_call_count == 1
        assert len(result.plan.nodes) == 2

    def test_planner_not_called_when_rule_sufficient(self):
        called = {"n": 0}

        def fake_llm(x):
            called["n"] += 1
            return "cap_a"

        planner = Planner(llm_callable=fake_llm, validator=lambda s: True)
        pipe = DecisionPipeline(planner=planner)
        pipe.execute({"text": "run tests"})
        assert called["n"] == 0

    def test_planner_not_called_when_workflow_matched(self):
        called = {"n": 0}

        def fake_llm(x):
            called["n"] += 1
            return "cap_a"

        lib = WorkflowLibrary()
        lib.register("crud-generator-v1", capabilities=["api.create"])
        from aios.orchestrator.workflow_matcher import WorkflowMatcher

        planner = Planner(llm_callable=fake_llm, validator=lambda s: True)
        pipe = DecisionPipeline(workflow_matcher=WorkflowMatcher(library=lib), planner=planner)
        pipe.execute({"text": "create crud api"})
        assert called["n"] == 0

    def test_planner_validation_reject(self):
        planner = Planner(llm_callable=lambda x: "cap_a", validator=lambda s: False)
        pipe = DecisionPipeline(planner=planner)
        with pytest.raises(ValidationError):
            pipe.execute({"text": "unknown xyz"})

    def test_policy_boundary(self):
        planner = Planner(llm_callable=lambda x: "cap_a", validator=lambda s: True)
        pipe = DecisionPipeline(planner=planner, policy_checker=lambda plan: False)
        with pytest.raises(DecisionPipelineError, match="policy"):
            pipe.execute({"text": "unknown xyz"})

    def test_policy_allow(self):
        planner = Planner(llm_callable=lambda x: "cap_a", validator=lambda s: True)
        pipe = DecisionPipeline(planner=planner, policy_checker=lambda plan: True)
        result = pipe.execute({"text": "unknown xyz"})
        assert result.plan is not None

    def test_offline_deterministic(self):
        pipe = DecisionPipeline()
        # No planner configured, but deterministic request should still work
        result = pipe.execute({"text": "health"})
        assert result.source == "deterministic"
        assert result.llm_call_count == 0

    def test_offline_insufficient_no_planner_raises(self):
        pipe = DecisionPipeline()
        with pytest.raises(DecisionPipelineError):
            pipe.execute({"text": "unknown xyz"})

    def test_evidence_chain(self):
        pipe = DecisionPipeline()
        result = pipe.execute({"text": "run tests"})
        ev = result.evidence
        assert ev.request_text == "run tests"
        assert ev.normalized.intent == "run_tests"
        assert ev.rule_decision.status == "SUFFICIENT"
        assert ev.plan is not None
        assert ev.source == "deterministic"
        assert ev.to_dict()["request_text"] == "run tests"

    def test_evidence_planner(self):
        planner = Planner(llm_callable=lambda x: "cap_a", validator=lambda s: True)
        pipe = DecisionPipeline(planner=planner)
        result = pipe.execute({"text": "unknown xyz"})
        assert result.evidence.planner_called is True
        assert result.evidence.planner_raw == "cap_a"

    def test_governance_request_compat(self):
        from aios.governance.deterministic import Request

        pipe = DecisionPipeline()
        result = pipe.execute(Request(text="run tests", metadata={}))
        assert result.source == "deterministic"
