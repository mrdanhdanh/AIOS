"""Tests for Normalizer — AC-010-01 (TASK-010)."""

from aios.orchestrator.normalizer import Normalizer, NormalizedRequest


class TestNormalization:
    def test_same_semantic_stable(self):
        n = Normalizer()
        r1 = n.normalize({"text": "run tests"})
        r2 = n.normalize({"text": "Run Tests"})
        r3 = n.normalize({"text": "run tests."})
        assert r1.intent == r2.intent == r3.intent == "run_tests"
        assert r1.normalized_text == r2.normalized_text == r3.normalized_text

    def test_alias_health(self):
        n = Normalizer()
        for txt in ["health", "system health", "show system health", "health check"]:
            r = n.normalize({"text": txt})
            assert r.intent == "health", f"failed for {txt!r}"

    def test_alias_review_code(self):
        n = Normalizer()
        for txt in ["review code", "review project", "review_code"]:
            r = n.normalize({"text": txt})
            assert r.intent == "review_code"

    def test_alias_crud(self):
        n = Normalizer()
        r = n.normalize({"text": "create crud api"})
        assert r.intent == "create_crud_api"

    def test_target_resolution_default(self):
        n = Normalizer()
        r = n.normalize({"text": "run tests"})
        assert r.target_type == "workspace"
        assert r.target_value == "current"

    def test_target_resolution_file(self):
        n = Normalizer()
        r = n.normalize({"text": "review file main.py"})
        assert r.target_type == "file"
        assert r.target_value == "main.py"

    def test_mode_priority_defaults(self):
        n = Normalizer()
        r = n.normalize({"text": "run tests"})
        assert r.mode == "execute"
        assert r.priority == "normal"

    def test_mode_priority_from_metadata(self):
        n = Normalizer()
        r = n.normalize({"text": "run tests", "metadata": {"mode": "simulate", "priority": "high"}})
        assert r.mode == "simulate"
        assert r.priority == "high"

    def test_invalid_mode_fallback(self):
        n = Normalizer()
        r = n.normalize({"text": "run tests", "metadata": {"mode": "invalid"}})
        assert r.mode == "execute"

    def test_source_channel(self):
        n = Normalizer()
        r = n.normalize({"text": "run tests", "metadata": {"source_channel": "cli"}})
        assert r.source_channel == "cli"

    def test_unknown_intent(self):
        n = Normalizer()
        r = n.normalize({"text": "do something completely unknown xyz123"})
        assert r.intent != ""
        assert isinstance(r, NormalizedRequest)

    def test_governance_request_compat(self):
        from aios.governance.deterministic import Request

        n = Normalizer()
        r = n.normalize(Request(text="run tests", metadata={}))
        assert r.intent == "run_tests"
