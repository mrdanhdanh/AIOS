"""Identity and access management (M7 — TASK-035)."""
from aios.identity.contracts import IdentityError, Permission, Principal, Policy, Role
from aios.identity.identity_service import IdentityService
from aios.identity.rbac import RBACEnforcer
__all__ = ["IdentityError", "Permission", "Principal", "Policy", "Role", "IdentityService", "RBACEnforcer"]
