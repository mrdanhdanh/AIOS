"""Deterministic tests for the AIOS 2.0 Coding Edition (M26).

Covers all 22 capabilities (TASK-197..TASK-218). Each test asserts the
fail-closed, deterministic, provenance-bearing invariants required by the
governance gates. UNKNOWN is never promoted to PASS.
"""

import pytest

from aios.coding_edition import (
    ApprovalGate,
    ApprovalRequest,
    ApprovalVerdict,
    ArtifactLineage,
    BenchmarkGate,
    BenchmarkResult,
    BenchmarkVerdict,
    Certification,
    CodingCertification,
    CodingDoctor,
    CodingEdition,
    CodingEditionContract,
    CodingEditionState,
    CodingEditionStateMachine,
    CodingHealthScore,
    CodingSession,
    CompletionState,
    ComponentResult,
    DiagnosticLevel,
    Failure,
    FailureKind,
    FullRegression,
    Guardrail,
    GuardrailSet,
    GuardrailVerdict,
    HealthDimension,
    HealthReport,
    ImpactAnalyzer,
    LineageNode,
    MultiAgentCoordinator,
    AgentRole,
    ParallelCodingScheduler,
    CodingTask,
    PolicyContext,
    PolicyEngine,
    PolicyRule,
    PolicyVerdict,
    RecoveryOrchestrator,
    RecoveryPlan,
    ReleaseCandidate,
    ReleaseGate,
    ReleaseVerdict,
    RepoKnowledgeGraph,
    RepoNode,
    RiskEngine,
    RiskInput,
    RiskLevel,
    RiskModel,
    SafeStopController,
    SessionFork,
    StopState,
    CodingEditionError,
)


# --- TASK-197 Unified Coding Contract -----------------------------------------
def test_contract_requires_id():
    with pytest.raises(CodingEditionError):
        CodingEditionContract(contract_id="")


def test_contract_hash_deterministic():
    c1 = CodingEditionContract(contract_id="c1", capabilities=("gen", "verify"))
    c2 = CodingEditionContract(contract_id="c1", capabilities=("gen", "verify"))
    assert c1.contract_hash == c2.contract_hash


def test_contract_verify_completion_prefix():
    c = CodingEditionContract(contract_id="c1")
    assert c.verify_completion((CompletionState.AUTHORIZED, CompletionState.EXECUTED))
    assert not c.verify_completion((CompletionState.EXECUTED, CompletionState.AUTHORIZED))


# --- TASK-198 Coding State Machine --------------------------------------------
def test_state_machine_transition_happy():
    sm = CodingEditionStateMachine()
    sm.transition(CodingEditionState.AUTHORIZED, "authorization")
    sm.transition(CodingEditionState.EXECUTED, "generated_code")
    assert sm.state == CodingEditionState.EXECUTED
    assert len(sm.history) == 2


def test_state_machine_illegal_transition():
    sm = CodingEditionStateMachine()
    with pytest.raises(CodingEditionError):
        sm.transition(CodingEditionState.EXECUTED, "generated_code")


def test_state_machine_missing_artifact():
    sm = CodingEditionStateMachine()
    sm.transition(CodingEditionState.AUTHORIZED, "authorization")
    with pytest.raises(CodingEditionError):
        sm.transition(CodingEditionState.EXECUTED, "wrong")


def test_state_machine_provenance_deterministic():
    sm = CodingEditionStateMachine(run_id="r")
    sm.transition(CodingEditionState.AUTHORIZED, "authorization")
    sm2 = CodingEditionStateMachine(run_id="r")
    sm2.transition(CodingEditionState.AUTHORIZED, "authorization")
    assert sm.provenance_chain() == sm2.provenance_chain()


# --- TASK-199 Coding Policy Engine --------------------------------------------
def test_policy_pass_and_insufficient():
    eng = PolicyEngine([PolicyRule("p1", "needs gen", required_capability="gen")])
    assert eng.evaluate(PolicyContext("act", capabilities=("gen",))) == (PolicyVerdict.PASS, [])
    v, violated = eng.evaluate(PolicyContext("act", capabilities=()))
    assert v == PolicyVerdict.INSUFFICIENT and "p1" in violated


def test_policy_unknown_when_empty():
    eng = PolicyEngine()
    v, _ = eng.evaluate(PolicyContext("act"))
    assert v == PolicyVerdict.UNKNOWN


# --- TASK-200 Risk Engine -----------------------------------------------------
def test_risk_assess_bands():
    eng = RiskEngine([RiskModel("blast", 1.0)])
    score, level = eng.assess(RiskInput("ch1", {"blast": 0.9}))
    assert level == RiskLevel.CRITICAL
    score2, level2 = eng.assess(RiskInput("ch2", {"blast": 0.1}))
    assert level2 == RiskLevel.LOW


def test_risk_unknown_without_model():
    eng = RiskEngine()
    _, level = eng.assess(RiskInput("ch", {}))
    assert level == RiskLevel.UNKNOWN


# --- TASK-231 CodingEdition <-> RealToolHandler ------------------------------
def test_execute_code_writes_via_handler(tmp_path, monkeypatch):
    from aios.runtime.permission import Permission, PermissionBroker, PermissionScope
    from aios.runtime.process import RealToolHandler

    monkeypatch.setenv("AIOS_REAL_EXECUTION_ENABLED", "1")
    broker = PermissionBroker()
    broker.grant("runtime", Permission(PermissionScope.WRITE, "*"))
    broker.grant("runtime", Permission(PermissionScope.EXECUTE, "*"))
    handler = RealToolHandler(broker=broker, subject="runtime", allowed_cwd=str(tmp_path))

    ce = CodingEdition(run_id="t231")
    code = "def add(a, b):\n    return a + b\n"
    report = ce.execute_code(handler, code, str(tmp_path), run_tests=False)
    assert "wrote" in report
    written = (tmp_path / "generated_code.py").read_text(encoding="utf-8")
    assert written == code


def test_execute_code_requires_handler():
    ce = CodingEdition(run_id="t231b")
    with pytest.raises(CodingEditionError):
        ce.execute_code(None, "x = 1", "/tmp")


def test_execute_code_denied_without_permission(tmp_path, monkeypatch):
    from aios.runtime.permission import PermissionBroker
    from aios.runtime.process import RealToolHandler

    monkeypatch.setenv("AIOS_REAL_EXECUTION_ENABLED", "1")
    # Broker with NO grants -> handler must deny (fail-closed).
    handler = RealToolHandler(broker=PermissionBroker(), subject="runtime", allowed_cwd=str(tmp_path))
    ce = CodingEdition(run_id="t231c")
    with pytest.raises(PermissionError):
        ce.execute_code(handler, "x = 1", str(tmp_path))


# --- TASK-201 Approval Gate --------------------------------------------------
def test_approval_critical_rejected():
    gate = ApprovalGate(risk_engine=RiskEngine([RiskModel("b", 1.0)]))
    req = ApprovalRequest("r1", "c1", RiskInput("c1", {"b": 1.0}))
    v, _ = gate.evaluate(req)
    assert v == ApprovalVerdict.REJECTED


def test_approval_low_approved():
    gate = ApprovalGate(risk_engine=RiskEngine([RiskModel("b", 1.0)]))
    req = ApprovalRequest("r1", "c1", RiskInput("c1", {"b": 0.1}), required_approvers=1, obtained_approvers=1)
    v, _ = gate.evaluate(req)
    assert v == ApprovalVerdict.APPROVED


# --- TASK-202 Autonomous Guardrails -------------------------------------------
def test_guardrails_block_forbidden():
    gs = GuardrailSet([Guardrail("g1", "no rm", forbidden_prefix="rm ")])
    v, blocked = gs.check("rm -rf")
    assert v == GuardrailVerdict.BLOCKED and blocked


def test_guardrails_allow():
    gs = GuardrailSet([Guardrail("g1", "ok", max_autonomy=1.0)])
    v, _ = gs.check("edit", autonomy=0.5)
    assert v == GuardrailVerdict.ALLOWED


# --- TASK-203 Safe Stop / Resume ---------------------------------------------
def test_safe_stop_pause_resume():
    c = SafeStopController()
    cp = c.pause("snapshot-state")
    assert c.state == StopState.PAUSED
    assert c.latest_checkpoint() is cp
    c.resume()
    assert c.state == StopState.RESUMED


def test_safe_stop_resume_from_running_fails():
    c = SafeStopController()
    with pytest.raises(CodingEditionError):
        c.resume()


# --- TASK-204 Recovery Orchestrator -------------------------------------------
def test_recovery_plan_runtime_rollback():
    o = RecoveryOrchestrator()
    p = o.plan(Failure("f1", FailureKind.RUNTIME))
    assert p.strategy == "rollback"
    assert any(s.action == "snapshot-restore" for s in p.steps)


def test_recovery_requires_step():
    with pytest.raises(CodingEditionError):
        RecoveryPlan("p", "f", [], "x")


# --- TASK-205 Artifact Lineage ------------------------------------------------
def test_lineage_chain():
    l = ArtifactLineage()
    a = l.record("gen", "code")
    b = l.record("verify", "report", parents=[a.artifact_id])
    chain = l.get_chain(b.artifact_id)
    assert len(chain) == 2
    assert {n.artifact_id for n in chain} == {a.artifact_id, b.artifact_id}


def test_lineage_missing_parent():
    l = ArtifactLineage()
    with pytest.raises(CodingEditionError):
        l.record("x", "y", parents=["missing"])


# --- TASK-206 Coding Session -------------------------------------------------
def test_session_lifecycle():
    s = CodingSession(goal="build")
    s.start()
    s.commit_step("f.py", "hash")
    s.review()
    s.close()
    assert s.state.value == "CLOSED"


def test_session_close_empty_fails():
    s = CodingSession(goal="g")
    s.start()
    with pytest.raises(CodingEditionError):
        s.close()


# --- TASK-207 Session Fork ---------------------------------------------------
def test_session_fork():
    s = CodingSession(goal="g")
    s.start()
    s.commit_step("f.py", "h")
    fk = SessionFork().fork(s, "exp")
    assert fk.parent_id == s.session_id


# --- TASK-208 Multi-Agent Coding ---------------------------------------------
def test_multi_agent_conflict():
    co = MultiAgentCoordinator()
    co.assign("a1", AgentRole.CODER, "taskX")
    co.assign("a2", AgentRole.CODER, "taskX")
    assert "taskX" in co.detect_conflict()


# --- TASK-209 Parallel Coding ------------------------------------------------
def test_parallel_schedule_batches():
    sch = ParallelCodingScheduler()
    batches = sch.schedule([CodingTask("a"), CodingTask("b", ("a",)), CodingTask("c", ("a",))])
    assert batches[0] == ["a"]
    assert set(batches[1]) == {"b", "c"}


def test_parallel_cycle_detected():
    sch = ParallelCodingScheduler()
    with pytest.raises(CodingEditionError):
        sch.schedule([CodingTask("a", ("b",)), CodingTask("b", ("a",))])


# --- TASK-210 Change Impact Analysis -----------------------------------------
def test_impact_analysis():
    a = ImpactAnalyzer()
    a.add_edge("b", "a")  # b depends on a
    a.add_edge("c", "b")
    impacted = a.analyze(["a"])
    assert impacted == {"b", "c"}


# --- TASK-211 Repository Knowledge Graph -------------------------------------
def test_knowledge_graph_query():
    g = RepoKnowledgeGraph()
    g.ingest([RepoNode("m1", "module", "M"), RepoNode("s1", "symbol", "S")], {"m1": ["s1"]})
    assert len(g.query("module")) == 1
    assert g.neighbors("m1") == ["s1"]


# --- TASK-212 Coding Doctor --------------------------------------------------
def test_doctor_unhealthy():
    d = CodingDoctor()
    diags = d.diagnose(steps=0, failures=1)
    assert not d.is_healthy(diags)
    assert any(x.level == DiagnosticLevel.ERROR for x in diags)


# --- TASK-213 Coding Health Score --------------------------------------------
def test_health_score():
    h = CodingHealthScore([HealthDimension("q", 0.5), HealthDimension("r", 0.5)])
    rep = h.compute({"q": 1.0, "r": 0.0})
    assert isinstance(rep, HealthReport)
    assert 0.0 <= rep.score <= 1.0


def test_health_missing_dimension():
    h = CodingHealthScore([HealthDimension("q", 1.0)])
    with pytest.raises(CodingEditionError):
        h.compute({"other": 1.0})


# --- TASK-214 Release Gate ---------------------------------------------------
def test_release_go():
    g = ReleaseGate(min_coverage=0.8)
    assert g.evaluate(ReleaseCandidate("rc", tests_passed=True, coverage=0.9, certified=True)) == ReleaseVerdict.GO
    assert g.evaluate(ReleaseCandidate("rc", tests_passed=False)) == ReleaseVerdict.NOGO


# --- TASK-215 Coding Certification -------------------------------------------
def test_certification_trust_threshold():
    c = CodingCertification()
    cert = c.certify("art1", "ev1", 0.9)
    assert isinstance(cert, Certification)
    with pytest.raises(CodingEditionError):
        c.certify("art2", "ev2", 0.3)


# --- TASK-216 Benchmark Gate -------------------------------------------------
def test_benchmark_pass_fail():
    g = BenchmarkGate(tolerance=0.05)
    assert g.evaluate([BenchmarkResult("speed", 100, 100)]) == BenchmarkVerdict.PASS
    assert g.evaluate([BenchmarkResult("speed", 50, 100)]) == BenchmarkVerdict.FAIL
    assert g.evaluate([]) == BenchmarkVerdict.UNKNOWN


# --- TASK-217 AIOS 2.0 Coding Integration ------------------------------------
def test_integration_run():
    ce = CodingEdition()
    rep = ce.run(authorization="auth", generated_code="code", verification_report="ok")
    assert rep.final_state == CodingEditionState.CERTIFIED.value
    assert rep.status == "PASS"


def test_integration_missing_authorization():
    ce = CodingEdition()
    with pytest.raises(CodingEditionError):
        ce.run(authorization="", generated_code="code", verification_report="ok")


# --- TASK-218 Full M0-M26 Regression -----------------------------------------
def test_full_regression_pass():
    r = FullRegression()
    rep = r.run([ComponentResult("T001", "PASS")])
    assert rep.status.value == "PASS"


def test_full_regression_unknown_not_promoted():
    r = FullRegression()
    rep = r.run([ComponentResult("T001", "UNKNOWN")])
    assert rep.status.value == "UNKNOWN"
