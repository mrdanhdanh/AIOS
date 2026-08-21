"""IsolationManager."""
from __future__ import annotations
from aios.security.contracts import Credential, NetworkPolicy, SandboxConfig

class IsolationManager:
    def __init__(self) -> None:
        self._credentials: dict[str, Credential] = {}
        self._policies: list[NetworkPolicy] = []
        self._sandboxes: dict[str, SandboxConfig] = {}
    def store_credential(self, cred: Credential) -> None: self._credentials[cred.cred_id] = cred
    def get_credential(self, cid: str) -> Credential | None: return self._credentials.get(cid)
    def validate_credential(self, cid: str) -> bool:
        c = self._credentials.get(cid)
        return c is not None and c.is_valid()
    def add_network_policy(self, policy: NetworkPolicy) -> None: self._policies.append(policy)
    def check_network_policy(self, action: str) -> bool:
        for p in self._policies:
            if action in p.rules: return True
        return len(self._policies) == 0  # No policy = allow
    def create_sandbox(self, config: SandboxConfig) -> SandboxConfig:
        self._sandboxes[config.sandbox_id] = config; return config
    def get_sandbox(self, sid: str) -> SandboxConfig | None: return self._sandboxes.get(sid)
