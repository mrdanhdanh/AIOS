"""Tests for security module."""
from __future__ import annotations
import pytest
from aios.security.contracts import Credential, CredentialType, NetworkPolicy, SandboxConfig
from aios.security.isolation import IsolationManager

class TestSecurity:
    def test_store_credential(self):
        mgr = IsolationManager()
        c = Credential(value="secret123")
        mgr.store_credential(c)
        assert mgr.validate_credential(c.cred_id)
    def test_invalid_credential(self):
        mgr = IsolationManager()
        c = Credential(value="")
        mgr.store_credential(c)
        assert not mgr.validate_credential(c.cred_id)
    def test_network_policy(self):
        mgr = IsolationManager()
        p = NetworkPolicy(name="allow_read", rules=["read", "list"])
        mgr.add_network_policy(p)
        assert mgr.check_network_policy("read")
        assert not mgr.check_network_policy("delete")
    def test_no_policy_allows(self):
        mgr = IsolationManager()
        assert mgr.check_network_policy("anything")
    def test_sandbox(self):
        mgr = IsolationManager()
        cfg = SandboxConfig(isolation_level="container", network_access=False)
        s = mgr.create_sandbox(cfg)
        assert mgr.get_sandbox(s.sandbox_id).isolation_level == "container"
