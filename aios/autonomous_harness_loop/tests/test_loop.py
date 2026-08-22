"""Tests for the Autonomous Harness Loop (TASK-099)."""

from aios.autonomous_harness_loop.loop import HarnessLoopEngine
from aios.autonomy_governor.contracts import AutonomyAction, AutonomyMode, AutonomyPolicy
from aios.autonomy_governor.governor import AutonomyGovernor
from aios.autonomous_scheduler.contracts import ScheduleEntry, TriggerType
from aios.autonomous_scheduler.scheduler import Scheduler
from aios.remediation_apply.apply import ApplyOrchestrator
from aios.remediation_detect.detect import Incident
from aios.runtime.permission import Permission, PermissionBroker, PermissionScope


def _permissive_governor() -> AutonomyGovernor:
    actions = {a.value: "allow" for a in AutonomyAction}
    return AutonomyGovernor(policy=AutonomyPolicy(mode=AutonomyMode.AUTONOMOUS, actions=actions))


def _permissive_broker() -> PermissionBroker:
    b = PermissionBroker()
    b.grant("remediation", Permission(PermissionScope.EXECUTE, "*"))
    return b


def test_schedule_due_runs_harness_chain():
    sched = Scheduler(now=lambda: 100.0)
    entry = sched.register(
        ScheduleEntry(
            goal_id="g1",
            trigger=TriggerType.CRON,
            cron_expr="interval:0",
            autonomy_level_required="supervised",
        )
    )
    eng = HarnessLoopEngine(scheduler=sched)
    assert eng.trigger_due(entry) is True


def test_deviation_not_promoted_and_detect_triggered():
    eng = HarnessLoopEngine()  # default SUPERVISED governor blocks remediation
    incident = Incident(incident_id="inc-x", kind="failure", severity="high", evidence_ref="ev-x")
    run = eng.run(
        goal_id="g1",
        system_state={"healthy": False},
        harness_fn=lambda s: "fail",
        incident=incident,
    )
    assert run.verdict != "pass"
    assert run.deviations == ["inc-x"]
    assert run.remediation_triggered is False


def test_autonomy_not_allowed_no_remediation():
    eng = HarnessLoopEngine()  # default SUPERVISED governor
    incident = Incident(incident_id="inc-y", kind="failure", severity="high", evidence_ref="ev-y")
    run = eng.run(
        goal_id="g2",
        system_state={"healthy": False},
        harness_fn=lambda s: "fail",
        incident=incident,
    )
    assert run.autonomy_allowed is False
    assert run.remediation_triggered is False


def test_autonomy_allowed_triggers_remediation():
    gov = _permissive_governor()
    apply = ApplyOrchestrator(governor=gov, permission_broker=_permissive_broker())
    eng = HarnessLoopEngine(governor=gov, apply_orchestrator=apply)
    incident = Incident(incident_id="inc-z", kind="failure", severity="high", evidence_ref="ev-z")
    run = eng.run(
        goal_id="g3",
        system_state={"healthy": False},
        harness_fn=lambda s: "fail",
        incident=incident,
    )
    assert run.autonomy_allowed is True
    assert run.remediation_triggered is True


def test_deterministic_loop_result():
    eng = HarnessLoopEngine()
    incident = Incident(incident_id="inc-d", kind="failure", severity="high", evidence_ref="ev-d")
    r1 = eng.run(
        goal_id="g4",
        system_state={"healthy": False},
        harness_fn=lambda s: "fail",
        incident=incident,
    )
    r2 = eng.run(
        goal_id="g4",
        system_state={"healthy": False},
        harness_fn=lambda s: "fail",
        incident=incident,
    )
    assert eng.result_hash(r1) == eng.result_hash(r2)


def test_loop_evidence_provenance():
    eng = HarnessLoopEngine()
    run = eng.run(goal_id="g5", system_state={"healthy": True})
    assert eng.provenance_complete(run) is True
    assert run.evidence_ref
