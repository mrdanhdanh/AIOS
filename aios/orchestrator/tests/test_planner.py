"""Tests for Planner — AC-010-04/05 (TASK-010)."""

import pytest

from aios.orchestrator.normalizer import Normalizer
from aios.orchestrator.planner import Planner, PlannerError, PlannerRequest, ValidationError


class TestPlanner:
    def test_planner_called_only_when_needed(self):
        n = Normalizer()
        nr = n.normalize({"text": "complex request xyz"})
        planner = Planner(llm_callable=lambda x: "cap_a,cap_b", validator=lambda s: True)
        req = PlannerRequest(normalized_request=nr)
        resp = planner.plan(req)
        assert resp.validated is True
        assert resp.plan is not None
        assert len(resp.plan.nodes) == 2
        assert planner.call_count == 1

    def test_planner_no_callable_raises(self):
        n = Normalizer()
        nr = n.normalize({"text": "complex"})
        planner = Planner(llm_callable=None)
        req = PlannerRequest(normalized_request=nr)
        with pytest.raises(PlannerError):
            planner.plan(req)

    def test_planner_empty_output_reject(self):
        n = Normalizer()
        nr = n.normalize({"text": "complex"})
        planner = Planner(llm_callable=lambda x: "", validator=lambda s: True)
        req = PlannerRequest(normalized_request=nr)
        with pytest.raises(ValidationError):
            planner.plan(req)

    def test_planner_validator_reject(self):
        n = Normalizer()
        nr = n.normalize({"text": "complex"})
        planner = Planner(llm_callable=lambda x: "cap_a", validator=lambda s: False)
        req = PlannerRequest(normalized_request=nr)
        with pytest.raises(ValidationError):
            planner.plan(req)

    def test_planner_json_output(self):
        import json

        n = Normalizer()
        nr = n.normalize({"text": "complex"})
        raw = json.dumps({"nodes": [{"id": "n1", "capability": "cap_x"}, {"id": "n2", "capability": "cap_y"}]})
        planner = Planner(llm_callable=lambda x: raw, validator=lambda s: True)
        req = PlannerRequest(normalized_request=nr)
        resp = planner.plan(req)
        assert len(resp.plan.nodes) == 2
        assert resp.plan.nodes[0].capability == "cap_x"

    def test_planner_capability_registry_check(self):
        from aios.capability.capability import CapabilityRegistry, CapabilityContract

        reg = CapabilityRegistry()
        reg.register(CapabilityContract.create(capability_id="cap_a", version="1.0.0"))
        n = Normalizer()
        nr = n.normalize({"text": "complex"})
        planner = Planner(llm_callable=lambda x: "cap_a", validator=lambda s: True, capability_registry=reg)
        req = PlannerRequest(normalized_request=nr)
        resp = planner.plan(req)
        assert resp.validated

        # Unknown capability should fail when registry non-empty
        planner2 = Planner(llm_callable=lambda x: "unknown_cap", validator=lambda s: True, capability_registry=reg)
        with pytest.raises(ValidationError):
            planner2.plan(req)
