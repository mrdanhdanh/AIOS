"""Tests for RuleEngine — AC-010-02 (TASK-010)."""

from aios.orchestrator.normalizer import Normalizer
from aios.orchestrator.rule_engine import RuleEngine


class TestRuleEngine:
    def test_known_intents_sufficient(self):
        re = RuleEngine()
        n = Normalizer()
        for intent in ["status", "health", "help", "list_tasks", "list_skills", "review_code", "diagnose_runtime", "run_tests"]:
            nr = n.normalize({"text": intent})
            d = re.decide(nr)
            assert d.status == "SUFFICIENT", f"failed for {intent}"
            assert d.plan is not None
            assert len(d.plan.nodes) == 1

    def test_unknown_insufficient(self):
        re = RuleEngine()
        n = Normalizer()
        nr = n.normalize({"text": "do something unknown xyz123"})
        d = re.decide(nr)
        assert d.status == "INSUFFICIENT"
        assert d.plan is None

    def test_run_tests_sufficient(self):
        re = RuleEngine()
        n = Normalizer()
        nr = n.normalize({"text": "run tests"})
        d = re.decide(nr)
        assert d.status == "SUFFICIENT"
        assert d.plan.nodes[0].capability == "test.run"

    def test_health_sufficient(self):
        re = RuleEngine()
        n = Normalizer()
        nr = n.normalize({"text": "system health"})
        d = re.decide(nr)
        assert d.status == "SUFFICIENT"

    def test_is_sufficient_helper(self):
        re = RuleEngine()
        n = Normalizer()
        nr = n.normalize({"text": "health"})
        d = re.decide(nr)
        assert d.is_sufficient() is True
        nr2 = n.normalize({"text": "unknown xyz"})
        d2 = re.decide(nr2)
        assert d2.is_sufficient() is False
