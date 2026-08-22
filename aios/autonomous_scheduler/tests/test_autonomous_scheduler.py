"""Tests for TASK-062 Autonomous Scheduler."""
from __future__ import annotations

from aios.autonomous_scheduler.contracts import ScheduleEntry, TriggerType
from aios.autonomous_scheduler.scheduler import ActivationContext, Scheduler


def _sched(**kw):
    return Scheduler(**kw)


def test_cron_fires_when_due():
    s = _sched(now=lambda: 1000.0)
    e = ScheduleEntry(goal_id="g1", trigger=TriggerType.CRON, cron_expr="interval:10", next_fire=1005.0)
    s.register(e)
    assert s.evaluate_cron(e) is False
    s2 = Scheduler(now=lambda: 1010.0)
    s2._store[e.entry_id] = e
    assert s2.evaluate_cron(e) is True


def test_event_matches_filter():
    s = _sched()
    e = ScheduleEntry(goal_id="g1", trigger=TriggerType.EVENT, event_filter="goal.completed")
    assert s.evaluate_event(e, {"topic": "goal.completed.g1"}) is True
    assert s.evaluate_event(e, {"topic": "other"}) is False


def test_manual_requires_valid_token():
    s = _sched()
    e = ScheduleEntry(goal_id="g1", trigger=TriggerType.MANUAL, manual_token="tok-123")
    assert s.evaluate_manual(e, "tok-123") is True
    assert s.evaluate_manual(e, "wrong") is False
    assert s.evaluate_manual(e, "") is False


def test_undefined_trigger_no_activate():
    s = _sched()
    e = ScheduleEntry(goal_id="g1", trigger=TriggerType.MANUAL, manual_token="")
    ctx = ActivationContext(goal_id="g1", entry=e, autonomy_level="supervised")
    ok, reason = s.activate(ctx)
    assert ok is False


def test_activation_policy_blocks_low_autonomy():
    s = _sched()
    e = ScheduleEntry(goal_id="g1", trigger=TriggerType.MANUAL, manual_token="t",
                       autonomy_level_required="autonomous")
    ctx = ActivationContext(goal_id="g1", entry=e, autonomy_level="supervised", trigger_payload={"token": "t"})
    # token matches but autonomy level insufficient
    assert s.evaluate_manual(e, "t") is True
    ok, reason = s.activate(ctx)
    assert ok is False
    assert reason == "activation_policy_denied"


def test_governor_allow_activates():
    def gov(ctx):
        return "ALLOW"
    s = _sched(governor_decision=gov)
    e = ScheduleEntry(goal_id="g1", trigger=TriggerType.MANUAL, manual_token="t")
    ctx = ActivationContext(goal_id="g1", entry=e, autonomy_level="supervised", trigger_payload={"token": "t"})
    assert s.evaluate_manual(e, "t") is True
    ok, reason = s.activate(ctx)
    assert ok is True
    assert reason == "activated"


def test_governor_block_no_activate():
    def gov(ctx):
        return "BLOCK"
    s = _sched(governor_decision=gov)
    e = ScheduleEntry(goal_id="g1", trigger=TriggerType.MANUAL, manual_token="t")
    ctx = ActivationContext(goal_id="g1", entry=e, autonomy_level="supervised", trigger_payload={"token": "t"})
    ok, reason = s.activate(ctx)
    assert ok is False
    assert reason == "governor_blocked"


def test_budget_exceeded_blocks():
    s = _sched()
    e = ScheduleEntry(goal_id="g1", trigger=TriggerType.MANUAL, manual_token="t")
    ctx = ActivationContext(goal_id="g1", entry=e, autonomy_level="supervised",
                            trigger_payload={"token": "t"}, budget_exceeded=True)
    ok, reason = s.activate(ctx)
    assert ok is False


def test_audit_recorded_on_activation():
    def gov(ctx):
        return "ALLOW"
    s = _sched(governor_decision=gov)
    e = ScheduleEntry(goal_id="g1", trigger=TriggerType.MANUAL, manual_token="t")
    ctx = ActivationContext(goal_id="g1", entry=e, autonomy_level="supervised", trigger_payload={"token": "t"})
    s.activate(ctx)
    assert len(s.audit) == 1
    assert s.audit[0]["outcome"] == "activated"


def test_schedule_durable_next_fire():
    s = _sched(now=lambda: 500.0)
    e = ScheduleEntry(goal_id="g1", trigger=TriggerType.CRON, cron_expr="interval:60")
    s.register(e)
    assert e.next_fire == 560.0  # persisted, survives restart
