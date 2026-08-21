"""Tests for quota module."""
from __future__ import annotations
import pytest
from aios.quota.contracts import Quota, QuotaUsage
from aios.quota.quota_manager import QuotaManager

class TestQuota:
    def test_set_quota(self):
        mgr = QuotaManager()
        q = mgr.set_quota("t1", "tokens", 1000)
        assert q.limit == 1000
    def test_consume(self):
        mgr = QuotaManager()
        mgr.set_quota("t1", "tokens", 10)
        assert mgr.consume_quota("t1", "tokens", 5)
        q = mgr.check_quota("t1", "tokens")
        assert q.used == 5
    def test_exceeded(self):
        mgr = QuotaManager()
        mgr.set_quota("t1", "tokens", 2)
        mgr.consume_quota("t1", "tokens", 2)
        q = mgr.check_quota("t1", "tokens")
        assert q.exceeded
        assert not mgr.consume_quota("t1", "tokens", 1)
    def test_usage(self):
        mgr = QuotaManager()
        mgr.set_quota("t1", "api_calls", 100)
        mgr.consume_quota("t1", "api_calls", 30)
        usage = mgr.get_usage("t1", "api_calls")
        assert usage.used == 30
    def test_reset(self):
        mgr = QuotaManager()
        mgr.set_quota("t1", "x", 10)
        mgr.consume_quota("t1", "x", 5)
        mgr.reset_quota("t1", "x")
        q = mgr.check_quota("t1", "x")
        assert q.used == 0
