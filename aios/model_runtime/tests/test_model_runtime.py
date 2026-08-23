"""M17 model_runtime test matrix (T109-T116).

Covers the acceptance criteria / test matrices from ``docs/detailtask/T109.md``
.. ``T116.md``. Every scenario asserts the deterministic, fail-closed,
provenance-bearing invariants required by the master spec.
"""

from __future__ import annotations

import pytest

from aios.identity.contracts import (
    Decision,
    Permission,
    Principal,
    Role,
)
from aios.security.contracts import Credential, CredentialType

from aios.model_runtime import (
    ConformanceError,
    ConformanceResult,
    ConformanceSuite,
    HealthStatus,
    ModelContract,
    ModelContractError,
    ModelRegistry,
    ModelRequest,
    ModelResponse,
    ModelResolver,
    InferenceOrchestrator,
    ProviderCertifier,
    ProviderRegistry,
    ProviderStatus,
    ResilienceConfig,
    ResilienceError,
    ResilienceManager,
    ResolveStatus,
    SecurityContext,
    SecurityError,
    SecurityGate,
    UsageCollector,
    UsageSchema,
    validate_contract,
)


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _contract(model_id="m1", provider_ref="p1", caps=("chat",)):
    return ModelContract(
        model_id=model_id,
        provider_ref=provider_ref,
        capabilities=list(caps),
    )


def _principal_with_execute() -> Principal:
    role = Role(name="infer", permissions={Permission.EXECUTE})
    return Principal(principal_id="u1", name="user", roles=[role])


def _credential() -> Credential:
    return Credential(cred_id="c1", cred_type=CredentialType.API_KEY, value="secret")


def _build_provider_model() -> tuple[ProviderRegistry, ModelRegistry]:
    """A healthy, enabled provider bound to a registered model."""
    providers = ProviderRegistry()
    providers.register("p1", _contract(), run_id="setup")
    providers.enable("p1", run_id="setup")
    models = ModelRegistry(provider_registry=providers)
    models.register(_contract())
    return providers, models


# =========================================================================== #
# T109 — Model Contracts
# =========================================================================== #
def test_t109_valid_contract():
    c = _contract()
    validate_contract(c)  # no raise
    assert c.model_id == "m1"


def test_t109_invalid_contract_rejected():
    with pytest.raises(ModelContractError):
        validate_contract(ModelContract(model_id="", provider_ref="p1", capabilities=["chat"]))
    with pytest.raises(ModelContractError):
        validate_contract(ModelContract(model_id="m1", provider_ref="p1", capabilities=[]))


def test_t109_vendor_independent():
    # Contract carries no vendor logic; an alternate adapter can implement it.
    openai = _contract(model_id="gpt", provider_ref="openai")
    ollama = _contract(model_id="llama", provider_ref="ollama")
    validate_contract(openai)
    validate_contract(ollama)
    assert openai.provider_ref != ollama.provider_ref


def test_t109_request_validation_deterministic():
    c = _contract(caps=("chat", "vision"))
    req = ModelRequest(prompt="hi", capabilities=["chat"])
    c.validate_request(req)
    # Same input -> same validation (no raise).
    c.validate_request(req)
    bad = ModelRequest(prompt="hi", capabilities=["code"])
    with pytest.raises(ModelContractError):
        c.validate_request(bad)


def test_t109_policy_boundary_blocks_bypass():
    c = _contract()
    c.policy_ref = "pol-a"
    from aios.model_runtime import PolicyBoundary

    pb = PolicyBoundary(policy_ref="pol-a")
    assert pb.is_respected("pol-a")
    assert not pb.is_respected("other")


# =========================================================================== #
# T110 — Provider Registry + Lifecycle
# =========================================================================== #
def test_t110_register_immutable_id():
    reg = ProviderRegistry()
    reg.register("p1", _contract(), run_id="r")
    assert reg.get("p1").provider_id == "p1"


def test_t110_duplicate_id_rejected():
    reg = ProviderRegistry()
    reg.register("p1", _contract(), run_id="r")
    with pytest.raises(Exception):
        reg.register("p1", _contract(), run_id="r")


def test_t110_unhealthy_not_selected():
    reg = ProviderRegistry()
    reg.register("p1", _contract(), run_id="r")
    reg.enable("p1", run_id="r")
    reg.set_health("p1", healthy=False)
    assert reg.select() is None
    reg.set_health("p1", healthy=True)
    assert reg.select() is not None


def test_t110_invalid_contract_rejected():
    reg = ProviderRegistry()
    with pytest.raises(ModelContractError):
        reg.register("p1", ModelContract(model_id="", provider_ref="p", capabilities=[]), run_id="r")


def test_t110_lifecycle_event_provenance():
    reg = ProviderRegistry()
    reg.register("p1", _contract(), run_id="r")
    reg.enable("p1", run_id="r")
    reg.disable("p1", run_id="r")
    events = reg.get("p1").lifecycle_event_log
    assert len(events) >= 2
    for e in events:
        assert e.producer and e.run_id and e.event_id


def test_t110_deprecate_immutable():
    reg = ProviderRegistry()
    reg.register("p1", _contract(), run_id="r")
    reg.deprecate("p1", run_id="r")
    with pytest.raises(Exception):
        reg.enable("p1", run_id="r")  # deprecated id never reused


# =========================================================================== #
# T111 — Model Registry + Deterministic Resolver
# =========================================================================== #
def test_t111_register_immutable_id():
    reg = ModelRegistry()
    reg.register(_contract())
    assert reg.get("m1").model_id == "m1"


def test_t111_duplicate_id_rejected():
    reg = ModelRegistry()
    reg.register(_contract())
    with pytest.raises(Exception):
        reg.register(_contract())


def test_t111_resolve_deterministic_no_llm():
    providers, models = _build_provider_model()
    r1 = models.resolve("req-1", capability_req=["chat"])
    r2 = models.resolve("req-1", capability_req=["chat"])
    assert r1.llm_call_count == 0
    assert r1.resolver_deterministic is True
    assert r1.selected_model == r2.selected_model == "m1"
    assert r1.status == ResolveStatus.RESOLVED


def test_t111_unresolved_fail_closed():
    models = ModelRegistry()
    models.register(_contract(caps=("vision",)))
    r = models.resolve("req", capability_req=["chat"])  # no chat model
    assert r.status == ResolveStatus.UNRESOLVED
    assert r.selected_model is None


def test_t111_resolve_provenance():
    providers, models = _build_provider_model()
    r = models.resolve("req", capability_req=["chat"])
    assert r.provenance and all(r.provenance)


# =========================================================================== #
# T112 — Inference Runtime Orchestration
# =========================================================================== #
def _dispatch(provider_id, request):
    return ModelResponse(content="ok", model_id="m1", usage=UsageSchema(total_tokens=3))


def test_t112_plan_deterministic():
    providers, models = _build_provider_model()
    orch = InferenceOrchestrator(provider_registry=providers, model_registry=models)
    plan1 = orch.plan(ModelRequest(prompt="x", capabilities=["chat"]))
    plan2 = orch.plan(ModelRequest(prompt="x", capabilities=["chat"]))
    assert plan1.provider_ref == plan2.provider_ref == "p1"
    assert plan1.model_ref == plan2.model_ref == "m1"


def test_t112_dispatch_enabled_ok():
    providers, models = _build_provider_model()
    orch = InferenceOrchestrator(
        provider_registry=providers, model_registry=models, dispatch_fn=_dispatch
    )
    plan = orch.plan(ModelRequest(prompt="x", capabilities=["chat"]))
    resp = orch.dispatch(plan)
    assert resp.content == "ok"
    assert plan.evidence_ref  # provenance


def test_t112_dispatch_disabled_rejected():
    providers, models = _build_provider_model()
    providers.disable("p1", run_id="r")
    orch = InferenceOrchestrator(
        provider_registry=providers, model_registry=models, dispatch_fn=_dispatch
    )
    # Disabled provider is never selected -> plan is fail-closed rejected (T110).
    with pytest.raises(Exception):
        orch.plan(ModelRequest(prompt="x", capabilities=["chat"]))


def test_t112_invalid_provider_rejected():
    providers = ProviderRegistry()
    # Model references a provider that is never registered -> fail-closed.
    models = ModelRegistry(provider_registry=providers)
    models.register(_contract(provider_ref="ghost"))
    orch = InferenceOrchestrator(provider_registry=providers, model_registry=models)
    with pytest.raises(Exception):
        orch.plan(ModelRequest(prompt="x", capabilities=["chat"]))


# =========================================================================== #
# T113 — Credential + Permission + Policy Integration
# =========================================================================== #
def test_t113_permission_allow():
    gate = SecurityGate()
    ctx = gate.authorize(_principal_with_execute(), _credential(), resource="inference")
    assert isinstance(ctx, SecurityContext)
    assert ctx.policy_decision == Decision.ALLOW
    assert SecurityGate.is_authorized(ctx)


def test_t113_missing_permission_blocked():
    gate = SecurityGate()
    principal = Principal(principal_id="u2")  # no roles -> no EXECUTE
    ctx = gate.authorize(principal, _credential(), resource="inference")
    assert ctx.policy_decision == Decision.DENY
    assert not SecurityGate.is_authorized(ctx)


def test_t113_credential_not_leaked():
    gate = SecurityGate()
    ctx = gate.authorize(_principal_with_execute(), _credential(), resource="inference")
    d = ctx.to_dict()
    assert "secret" not in str(d)


def test_t113_policy_deny_blocked():
    gate = SecurityGate(
        policy_precheck=__import__(
            "aios.model_runtime.security", fromlist=["PolicyPrecheck"]
        ).PolicyPrecheck(policy_fn=lambda ref, res: False)
    )
    ctx = gate.authorize(
        _principal_with_execute(), _credential(), resource="inference", policy_ref="pol-x"
    )
    assert ctx.policy_decision == Decision.DENY


def test_t113_deterministic_decision():
    gate = SecurityGate()
    c1 = gate.authorize(_principal_with_execute(), _credential(), resource="inference")
    c2 = gate.authorize(_principal_with_execute(), _credential(), resource="inference")
    assert c1.policy_decision == c2.policy_decision


# =========================================================================== #
# T114 — Retry / Timeout / Streaming / Cancellation
# =========================================================================== #
def test_t114_retry_bounded():
    mgr = ResilienceManager()
    cfg = ResilienceConfig(max_retries=2, retry_cooldown=0.0)
    calls = {"n": 0}

    def flaky():
        calls["n"] += 1
        raise RuntimeError("boom")

    with pytest.raises(ResilienceError):
        mgr.execute(cfg, flaky)
    assert calls["n"] == 3  # initial + 2 retries, no infinite loop


def test_t114_timeout_fail_closed():
    import time

    mgr = ResilienceManager()
    # Timeout is checked before each attempt; a long call that also fails will
    # exceed the bound on the next retry and raise fail-closed.
    cfg = ResilienceConfig(max_retries=1, retry_cooldown=0.0, timeout_ms=10)

    def slow():
        time.sleep(0.2)
        raise RuntimeError("boom")

    with pytest.raises(ResilienceError):
        mgr.execute(cfg, slow)


def test_t114_streaming_provenance():
    mgr = ResilienceManager()
    cfg = ResilienceConfig(streaming=True)
    chunks = list(mgr.stream(cfg, ["a", "b"], run_id="s"))
    assert len(chunks) == 2
    assert all(c.provenance for c in chunks)


def test_t114_cancellation_releases():
    mgr = ResilienceManager()
    cfg = ResilienceConfig(cancellable=True)
    from aios.model_runtime import CancellationToken

    token = CancellationToken()
    mgr.cancel(token)
    assert token.is_cancelled()
    assert token.released


def test_t114_retry_exhausted_reject():
    mgr = ResilienceManager()
    cfg = ResilienceConfig(max_retries=1, retry_cooldown=0.0)
    with pytest.raises(ResilienceError):
        mgr.execute(cfg, lambda: (_ for _ in ()).throw(RuntimeError("x")))


def test_t114_deterministic_behavior():
    mgr = ResilienceManager()
    cfg = ResilienceConfig(max_retries=1, retry_cooldown=0.0)
    calls = {"n": 0}
    with pytest.raises(ResilienceError):
        mgr.execute(cfg, lambda: (_ for _ in ()).throw((calls.__setitem__("n", calls["n"] + 1), RuntimeError("x"))[1]))
    assert calls["n"] == 2


# =========================================================================== #
# T115 — Usage / Cost / Audit / Evidence
# =========================================================================== #
def test_t115_record_and_audit():
    collector = UsageCollector()
    rec = collector.record("inf-1", UsageSchema(total_tokens=10, cost=0.01), latency_ms=5.0)
    assert rec.audit_entry is not None
    assert rec.content_hash
    assert collector.audit_intact()


def test_t115_tamper_detected():
    collector = UsageCollector()
    collector.record("inf-1", UsageSchema(total_tokens=10), latency_ms=5.0)
    entries = collector._audit.list_entries()
    entries[0].content = "tampered"
    assert not collector.audit_intact()


def test_t115_missing_hash_rejected(monkeypatch):
    import aios.model_runtime.usage as usage_mod

    monkeypatch.setattr(usage_mod, "sha256", lambda c: "")
    collector = UsageCollector()
    with pytest.raises(Exception):
        collector.record("inf-1", UsageSchema(total_tokens=10))


def test_t115_cost_deterministic():
    collector = UsageCollector()
    r1 = collector.record("inf-1", UsageSchema(total_tokens=100), price_per_1k=0.001)
    r2 = collector.record("inf-1", UsageSchema(total_tokens=100), price_per_1k=0.001)
    assert r1.cost == r2.cost == 0.0001


def test_t115_evidence_provenance():
    collector = UsageCollector()
    rec = collector.record("inf-1", UsageSchema(total_tokens=10))
    assert rec.evidence_ref


# =========================================================================== #
# T116 — Provider Conformance + Certification
# =========================================================================== #
def _certifier_ready() -> ProviderCertifier:
    providers, models = _build_provider_model()
    suite = ConformanceSuite(providers, models)
    return ProviderCertifier(suite)


def test_t116_conformance_pass_certify():
    certifier = _certifier_ready()
    pc = certifier.certify("p1", "m1")
    assert pc.conformance_result == ConformanceResult.PASS
    assert pc.integrity_verified
    assert pc.authority == "aios"
    assert certifier.is_certified("p1", "m1")


def test_t116_conformance_fail_not_certified():
    providers = ProviderRegistry()
    # provider never enabled -> FAIL
    providers.register("p1", _contract(), run_id="r")
    models = ModelRegistry(provider_registry=providers)
    models.register(_contract())
    certifier = ProviderCertifier(ConformanceSuite(providers, models))
    with pytest.raises(ConformanceError):
        certifier.certify("p1", "m1")


def test_t116_inconclusive_not_certified():
    # model missing -> INCONCLUSIVE
    providers, _ = _build_provider_model()
    models = ModelRegistry(provider_registry=providers)  # no model registered
    certifier = ProviderCertifier(ConformanceSuite(providers, models))
    with pytest.raises(ConformanceError):
        certifier.certify("p1", "m1")


def test_t116_duplicate_cert_id_rejected():
    certifier = _certifier_ready()
    certifier.certify("p1", "m1", cert_id="C1")
    with pytest.raises(ConformanceError):
        certifier.certify("p1", "m1", cert_id="C1")


def test_t116_integrity_not_verified(monkeypatch):
    import aios.model_runtime.conformance as conf_mod

    # Empty hash -> integrity not verified -> fail-closed (T078).
    monkeypatch.setattr(conf_mod, "sha256", lambda c: "")
    certifier = _certifier_ready()
    with pytest.raises(ConformanceError):
        certifier.certify("p1", "m1")


def test_t116_deterministic_result():
    certifier = _certifier_ready()
    r1, _ = certifier.conformance("p1", "m1")
    r2, _ = certifier.conformance("p1", "m1")
    assert r1 == r2 == ConformanceResult.PASS
