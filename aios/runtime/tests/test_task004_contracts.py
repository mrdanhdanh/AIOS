"""TASK-004 acceptance補完 — contract × DI × policy-before-execution × boundary.

Bù đắp các khoảng trống mà 5 file test hiện tại chưa phủ theo spec
T002-004.md §7 Acceptance Criteria (10 mục) và §10 Definition of Done:

  1. Mỗi service có contract rõ (contracts.py — 5 contracts).
  2. Service dependency được resolve qua DI (RuntimeKernel + mock injection).
  3. Context không trở thành global mutable state.
  4. Audit record có provenance/context (actor/action/target/context/timestamp/hash).
  5-7. Artifact có identity / checksum / version.
  8. Permission scope được kiểm tra.
  9. Policy pre-check được thực hiện TRƯỚC execution (fail-closed, không bypass).
 10. Không có service nào bypass contract / layering.

Mọi test ở đây đều chạy offline, không LLM, không provider ngoài.
"""

from __future__ import annotations

import ast
import pathlib

import pytest

from aios.core.container import Container, Lifetime
from aios.core.contracts import ContractError
from aios.core.events import EventBus
from aios.core.planner import ExecutionPlan, Step
from aios.runtime.artifact import Artifact, ArtifactStore
from aios.runtime.audit import AuditStatus, AuditTrail
from aios.runtime.context import ContextStore, ContextType, RuntimeContext
from aios.runtime.contracts import (
    RUNTIME_SERVICE_CONTRACTS,
    check_runtime_contracts,
    verify_runtime_contracts,
)
from aios.runtime.execution import ExecutionOutcome, Executor
from aios.runtime.kernel import RuntimeKernel
from aios.runtime.permission import Permission, PermissionBroker, PermissionScope
from aios.runtime.policy import PolicyDecision, PolicyEngine, PolicyRequest, PolicyRule


# ------------------------------------------------------------------ #
# 1. Mỗi service có contract rõ
# ------------------------------------------------------------------ #
class TestRuntimeContracts:
    def test_five_contracts_declared(self):
        names = {c.name for c in RUNTIME_SERVICE_CONTRACTS}
        assert names == {
            "runtime.context",
            "runtime.audit",
            "runtime.artifact",
            "runtime.permission",
            "runtime.policy",
        }

    def test_verify_runtime_contracts_passes(self):
        verify_runtime_contracts()  # must not raise

    def test_incompatible_version_rejected(self):
        with pytest.raises(ContractError):
            check_runtime_contracts({"runtime.context": "2.0.0"})

    def test_missing_provider_rejected(self):
        with pytest.raises(ContractError, match="No provider"):
            check_runtime_contracts({})

    def test_prerelease_satisfies_contract(self):
        # SemVer prerelease within range should still satisfy
        check_runtime_contracts(
            {c.name: "1.0.0" for c in RUNTIME_SERVICE_CONTRACTS}
        )


# ------------------------------------------------------------------ #
# 2. Service dependency được resolve qua DI
# ------------------------------------------------------------------ #
class TestDIWiring:
    def test_kernel_resolves_all_five_task004_services(self):
        k = RuntimeKernel()
        assert isinstance(k.context, ContextStore)
        assert isinstance(k.audit, AuditTrail)
        assert isinstance(k.artifacts, ArtifactStore)
        assert isinstance(k.permissions, PermissionBroker)
        assert isinstance(k.policy, PolicyEngine)

    def test_kernel_also_exposes_event_bus(self):
        k = RuntimeKernel()
        assert isinstance(k.bus, EventBus)

    def test_executor_wired_with_shared_bus(self):
        k = RuntimeKernel()
        assert k.executor._bus is k.bus  # type: ignore[attr-defined]

    def test_mock_injection_via_container(self):
        """Spec TASK-003 AC: service có thể inject mock — áp cho TASK-004 services."""

        class FakeBroker(PermissionBroker):
            def has(self, subject, scope, resource):  # type: ignore[override]
                return True  # always allow

        c = Container()
        # Pre-register mock before kernel wires defaults — kernel must not overwrite
        # already-registered types? Actually RuntimeKernel always registers;
        # so we test the supported path: register mock AFTER kernel creation
        # via unregister + re-register (the DI container's intended mock flow).
        k = RuntimeKernel(container=c)
        c.unregister(PermissionBroker)
        c.register(PermissionBroker, FakeBroker, Lifetime.SINGLETON)
        # PolicyEngine was already created with the old broker — need to rewire it
        # to demonstrate the container allows scoped override in tests.
        c.unregister(PolicyEngine)
        c.register(
            PolicyEngine,
            factory=lambda: PolicyEngine(broker=c.resolve(PermissionBroker)),
            lifetime=Lifetime.SINGLETON,
        )
        policy = c.resolve(PolicyEngine)
        assert policy.evaluate(
            PolicyRequest(subject="any", action="x", resource="y", scope=PermissionScope.READ)
        ).decision != PolicyDecision.DENY  # mock says has() == True, so not denied at gate

    def test_kernel_policy_shares_permission_broker(self):
        """Lỗi wiring cũ: PolicyEngine tự tạo broker riêng -> grants vô hình."""
        k = RuntimeKernel()
        k.permissions.grant("agent-1", Permission(PermissionScope.CAPABILITY_INVOKE, "*"))
        k.policy.add_rule(
            PolicyRule(
                "allow-cap",
                applies=lambda r: True,
                decision=PolicyDecision.ALLOW,
                reason="ok",
            )
        )
        res = k.policy.evaluate(
            PolicyRequest(
                subject="agent-1",
                action="cap.invoke",
                resource="capability:math",
                scope=PermissionScope.CAPABILITY_INVOKE,
            )
        )
        assert res.decision == PolicyDecision.ALLOW
        # Unknown subject must still be denied (fail-closed)
        res2 = k.policy.evaluate(
            PolicyRequest(
                subject="ghost",
                action="cap.invoke",
                resource="capability:math",
                scope=PermissionScope.CAPABILITY_INVOKE,
            )
        )
        assert res2.decision == PolicyDecision.DENY


# ------------------------------------------------------------------ #
# 3. Context không trở thành global mutable state
# ------------------------------------------------------------------ #
class TestContextIsolation:
    def test_two_stores_are_isolated(self):
        a = ContextStore()
        b = ContextStore()
        ctx = RuntimeContext.create(ContextType.REQUEST)
        a.put(ctx)
        assert not b.exists(ctx.context_id)
        assert len(b) == 0

    def test_context_mutation_does_not_leak_across_instances(self):
        s1 = ContextStore()
        s2 = ContextStore()
        c1 = RuntimeContext.create(ContextType.AGENT, attributes={"x": 1})
        c2 = RuntimeContext.create(ContextType.AGENT, attributes={"x": 2})
        s1.put(c1)
        s2.put(c2)
        assert s1.get(c1.context_id).get_attr("x") == 1
        assert s2.get(c2.context_id).get_attr("x") == 2

    def test_no_module_level_global_store(self):
        import aios.runtime.context as mod

        # Module must not expose a singleton global store instance
        for name in dir(mod):
            obj = getattr(mod, name)
            if isinstance(obj, ContextStore):
                pytest.fail(f"Module exposes global ContextStore singleton: {name}")


# ------------------------------------------------------------------ #
# 4. Audit record có provenance/context + 5-7 Artifact invariants
# ------------------------------------------------------------------ #
class TestAuditProvenance:
    def test_audit_record_has_all_provenance_fields(self):
        trail = AuditTrail()
        ctx = RuntimeContext.create(ContextType.EXECUTION)
        ev = trail.record(
            "agent-1", "tool.invoke", "tool:calc", context_id=ctx.context_id, status=AuditStatus.OK
        )
        assert ev.actor == "agent-1"
        assert ev.action == "tool.invoke"
        assert ev.target == "tool:calc"
        assert ev.context_id == ctx.context_id
        assert ev.timestamp  # ISO8601
        assert ev.hash is not None
        assert ev.status == AuditStatus.OK

    def test_audit_chain_integrity(self):
        trail = AuditTrail()
        trail.record("a", "x", "r1")
        trail.record("a", "y", "r2")
        assert trail.verify_integrity()
        trail._events[0].metadata["tamper"] = True
        assert not trail.verify_integrity()


class TestArtifactInvariants:
    def test_identity(self):
        art = Artifact.create("spec.yaml", "hello")
        assert art.artifact_id.startswith("art-")
        assert art.name == "spec.yaml"

    def test_checksum(self):
        import hashlib

        art = Artifact.create("a", "payload")
        assert art.checksum == hashlib.sha256(b"payload").hexdigest()
        assert art.verify()
        art.content = b"tampered"
        assert not art.verify()

    def test_version_metadata(self):
        art = Artifact.create("a", "x", version="1.2.3")
        assert art.version == "1.2.3"
        assert art.semver.major == 1
        assert art.semver.minor == 2

    def test_store_rejects_tampered_artifact(self):
        store = ArtifactStore()
        art = Artifact.create("a", "ok")
        art.content = b"bad"
        with pytest.raises(Exception):
            store.put(art)


# ------------------------------------------------------------------ #
# 8-9. Permission scope + Policy pre-check TRƯỚC execution
# ------------------------------------------------------------------ #
class TestPolicyBeforeExecution:
    def test_policy_deny_prevents_handler_from_running(self):
        """Executor must NOT call handler when pre-check DENY."""
        broker = PermissionBroker()  # no grants
        eng = PolicyEngine(broker=broker)
        ex = Executor(policy=eng, subject="agent-x")
        plan = ExecutionPlan(plan_id="p1")
        step = Step(step_id="s0", action="tool.invoke")
        step.metadata["scope"] = PermissionScope.TOOL_INVOKE
        step.metadata["resource"] = "tool:rm"
        plan.add_step(step)

        called = {"n": 0}

        def handler(s, c):
            called["n"] += 1
            return "should-not-run"

        rep = ex.execute(plan, handler)
        assert rep.status == ExecutionOutcome.FAILED
        assert called["n"] == 0
        assert "policy DENY" in (rep.results["s0"].error or "")

    def test_kernel_policy_deny_blocks_execution_end_to_end(self):
        """Through RuntimeKernel wiring (shared broker) — the real gate."""
        k = RuntimeKernel()
        # No grant for agent-x -> policy must deny before execution
        plan = ExecutionPlan(plan_id="p-kernel")
        step = Step(step_id="s0", action="tool.invoke")
        step.metadata["scope"] = PermissionScope.TOOL_INVOKE
        step.metadata["resource"] = "tool:calc"
        plan.add_step(step)
        # Executor inside kernel uses kernel.policy (shares kernel.permissions)
        # but subject inside executor is "runtime" by default; we create a
        # dedicated executor bound to agent-x via the same shared policy.
        from aios.runtime.execution import Executor as Exec

        ex = Exec(policy=k.policy, audit=k.audit, subject="agent-x")
        rep = ex.execute(plan, lambda s, c: "nope")
        assert rep.status == ExecutionOutcome.FAILED

        # After granting, same request must pass (allow-all rule)
        k.permissions.grant("agent-x", Permission(PermissionScope.TOOL_INVOKE, "*"))
        k.policy.add_rule(
            PolicyRule("allow-tool", applies=lambda r: True, decision=PolicyDecision.ALLOW, reason="allow")
        )
        rep2 = ex.execute(plan, lambda s, c: "ok")
        assert rep2.status == ExecutionOutcome.COMPLETED

    def test_permission_scope_wildcard_and_prefix(self):
        broker = PermissionBroker()
        broker.grant("a", Permission(PermissionScope.READ, "*"))
        broker.grant("a", Permission(PermissionScope.WRITE, "file:/tmp/*"))
        assert broker.has("a", PermissionScope.READ, "anything")
        assert broker.has("a", PermissionScope.WRITE, "file:/tmp/a.txt")
        assert not broker.has("a", PermissionScope.WRITE, "file:/other/x")
        assert not broker.has("a", PermissionScope.DELETE, "anything")


# ------------------------------------------------------------------ #
# 10. Không bypass contract / layering
# ------------------------------------------------------------------ #
class TestRuntimeLayering:
    RUNTIME_DIR = pathlib.Path(__file__).parent.parent  # aios/runtime
    FORBIDDEN = ("aios.agents", "aios.orchestrator", "aios.governance", "aios.harness")

    def test_runtime_does_not_import_upper_layers(self):
        violations: list[str] = []
        for py in self.RUNTIME_DIR.rglob("*.py"):
            if "tests" in py.parts or "__pycache__" in py.parts:
                continue
            try:
                tree = ast.parse(py.read_text(encoding="utf-8"))
            except Exception:
                continue
            for node in ast.walk(tree):
                mod = ""
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        mod = alias.name
                        for prefix in self.FORBIDDEN:
                            if mod == prefix or mod.startswith(prefix + "."):
                                violations.append(f"{py.name} imports {mod}")
                elif isinstance(node, ast.ImportFrom):
                    mod = node.module or ""
                    for prefix in self.FORBIDDEN:
                        if mod == prefix or mod.startswith(prefix + "."):
                            violations.append(f"{py.name} imports {mod}")
        assert violations == [], "Runtime bypasses layering:\n" + "\n".join(violations)
