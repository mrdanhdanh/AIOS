"""Tests for WorkflowMatcher — AC-010-03 (TASK-010)."""

import pytest

from aios.orchestrator.rule_engine import RuleDecision
from aios.orchestrator.workflow_matcher import WorkflowLibrary, WorkflowMatcher, WorkflowMatcherError


class TestWorkflowLibrary:
    def test_register_and_find(self):
        lib = WorkflowLibrary()
        lib.register("crud-generator-v1", capabilities=["api.create", "db.migrate"], description="CRUD")
        wf = lib.find_for_intent("create crud api")
        assert wf is not None
        assert wf["workflow_id"] == "crud-generator-v1"

    def test_duplicate_reject(self):
        lib = WorkflowLibrary()
        lib.register("wf1", capabilities=["cap_a"])
        with pytest.raises(WorkflowMatcherError):
            lib.register("wf1", capabilities=["cap_b"])

    def test_empty_id_reject(self):
        lib = WorkflowLibrary()
        with pytest.raises(WorkflowMatcherError):
            lib.register("", capabilities=["cap_a"])

    def test_no_match(self):
        lib = WorkflowLibrary()
        lib.register("wf1", capabilities=["cap_a"])
        assert lib.find_for_intent("unknown xyz") is None


class TestWorkflowMatcher:
    def test_sufficient_passthrough(self):
        lib = WorkflowLibrary()
        lib.register("wf1", capabilities=["cap_a"])
        m = WorkflowMatcher(library=lib)
        d = RuleDecision(status="SUFFICIENT", plan=None, reason="already", intent="health")
        result = m.match(d)
        assert result.status == "SUFFICIENT"

    def test_insufficient_matched(self):
        lib = WorkflowLibrary()
        lib.register("crud-generator-v1", capabilities=["api.create", "db.migrate"])
        m = WorkflowMatcher(library=lib)
        d = RuleDecision(status="INSUFFICIENT", reason="no rule", intent="create_crud_api")
        result = m.match(d)
        assert result.status == "SUFFICIENT"
        assert result.plan is not None
        assert len(result.plan.nodes) == 2

    def test_insufficient_no_match(self):
        lib = WorkflowLibrary()
        m = WorkflowMatcher(library=lib)
        d = RuleDecision(status="INSUFFICIENT", reason="no rule", intent="unknown xyz")
        result = m.match(d)
        assert result.status == "INSUFFICIENT"

    def test_match_intent_helper(self):
        lib = WorkflowLibrary()
        lib.register("wf1", capabilities=["cap_a"], tags=["crud"])
        m = WorkflowMatcher(library=lib)
        assert m.match_intent("crud").status == "MATCHED"
        assert m.match_intent("unknown").status == "NO_MATCH"
