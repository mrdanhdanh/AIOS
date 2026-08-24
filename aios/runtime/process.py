"""Real tool execution handler (TASK-222).

This module lives at the ``runtime`` layer and performs *real* operating-system
execution (shell / git / file writes) on behalf of an
:class:`~aios.runtime.execution.Executor`. It is the bridge that turns AIOS from
a "self-managing" system into one that can actually *do* work — without needing
an LLM or any external API (suitable for weak/offline machines).

Layering: ``runtime`` layer — may use ``subprocess`` / ``os`` (ARCH-001..004
only forbid these in the agent/worker/skill layers). Never imports agent or
orchestrator internals.

Design invariants:
  * Fail-closed: a step is only executed if the wired :class:`PermissionBroker`
    grants the subject the required :class:`~aios.runtime.permission.PermissionScope`.
  * Deterministic-first: this handler never calls an LLM.
  * Safe-by-default: real execution is opt-in via ``real_execution.enabled`` in
    ``configs/default.yaml`` (or ``AIOS_REAL_EXECUTION_ENABLED`` env var).
"""

from __future__ import annotations

import concurrent.futures as cf
import os
import signal
import subprocess
from typing import Any, Dict, Optional

from aios.core.planner import Step
from .context import RuntimeContext
from .permission import Permission, PermissionBroker, PermissionScope

__all__ = [
    "RealToolHandler",
    "SCOPE_MAP",
    "load_real_execution_config",
    "record_execution_evidence",
]

# Map a workflow/config scope string to a PermissionScope enum.
SCOPE_MAP: Dict[str, PermissionScope] = {
    "process.execute": PermissionScope.EXECUTE,
    "execute": PermissionScope.EXECUTE,
    "tool:invoke": PermissionScope.TOOL_INVOKE,
    "capability:invoke": PermissionScope.CAPABILITY_INVOKE,
    "filesystem.write": PermissionScope.WRITE,
    "write": PermissionScope.WRITE,
    "filesystem.read": PermissionScope.READ,
    "read": PermissionScope.READ,
}

# Commands that are never allowed to run, regardless of grants (defense-in-depth).
_DENY_COMMANDS = (
    "rm -rf /",
    "rm -rf /*",
    "format ",
    "mkfs",
    "shutdown",
    "reboot",
    ":(){",
)


def _is_denied_command(command: str) -> bool:
    lowered = command.strip().lower()
    return any(token in lowered for token in _DENY_COMMANDS)


class RealToolHandler:
    """A :data:`StepHandler` that runs real OS commands.

    The executor invokes ``__call__(step, context)`` for each step. The step's
    ``metadata`` must carry:

      * ``command``   — the shell command to run
      * ``tool_type`` — ``"shell"`` (default) or ``"git"``
      * ``cwd``       — working directory (sandboxed to ``allowed_cwd``)
      * ``timeout``   — per-step wall-clock budget (seconds)
      * ``scope``     — a :class:`PermissionScope` required for the step
      * ``resource``  — resource string checked against the broker

    Execution is denied (raises :class:`PermissionError`) if the broker does not
    grant the subject the step's scope on the resource, or if the command matches
    the deny-list.
    """

    def __init__(
        self,
        broker: PermissionBroker,
        subject: str = "runtime",
        allowed_cwd: Optional[str] = None,
    ) -> None:
        self._broker = broker
        self._subject = subject
        self._allowed_cwd = os.path.abspath(allowed_cwd) if allowed_cwd else None

    # StepHandler protocol: handler(step, context) -> output
    def __call__(self, step: Step, ctx: Optional[RuntimeContext] = None) -> Any:
        meta = step.metadata or {}
        command = meta.get("command") or step.action
        tool_type = meta.get("tool_type", "shell")
        timeout = float(meta.get("timeout", 30))
        cwd = meta.get("cwd") or self._allowed_cwd
        scope = meta.get("scope", PermissionScope.EXECUTE)
        resource = meta.get("resource", step.action)

        if not command or not str(command).strip():
            raise ValueError(f"step {step.step_id!r} has no command to execute")

        # Defense-in-depth: deny-list (never runs, even with grants).
        if _is_denied_command(str(command)):
            raise PermissionError(f"command denied by safety deny-list: {command!r}")

        # Defense-in-depth: permission re-check (executor also pre-checks).
        if not self._broker.has(self._subject, scope, resource):
            raise PermissionError(
                f"subject {self._subject!r} lacks {scope.value} on {resource!r}"
            )

        # Sandbox: confine cwd to allowed_cwd when set.
        if self._allowed_cwd is not None and cwd is not None:
            abs_cwd = os.path.abspath(cwd)
            if not abs_cwd.startswith(self._allowed_cwd):
                raise PermissionError(
                    f"cwd {abs_cwd!r} outside allowed_cwd {self._allowed_cwd!r}"
                )

        use_shell = tool_type in ("shell", "git")
        create_group = os.name == "nt"
        proc = subprocess.Popen(
            str(command),
            shell=use_shell,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            preexec_fn=os.setsid if os.name != "nt" else None,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if create_group else 0,
        )
        try:
            out, err = proc.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            self._kill(proc)
            raise cf.TimeoutError(f"command timed out after {timeout}s: {command!r}")
        if proc.returncode != 0:
            raise RuntimeError(
                f"command exited {proc.returncode}: {command!r}\n{err or ''}"
            )
        return out

    @staticmethod
    def _kill(proc: "subprocess.Popen[str]") -> None:
        """Kill the process group (cross-platform) and reap."""
        try:
            if os.name == "nt":
                proc.send_signal(signal.CTRL_BREAK_EVENT)
            else:
                os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass
        try:
            proc.wait(timeout=5)
        except Exception:
            pass


def load_real_execution_config() -> Dict[str, Any]:
    """Load the ``real_execution`` config section.

    Reads ``configs/default.yaml`` relative to the repo root. Falls back to the
    ``AIOS_REAL_EXECUTION_ENABLED`` environment variable. Returns a dict with at
    least ``{"enabled": bool}``; defaults to disabled (safe).
    """
    import yaml
    from pathlib import Path

    root = Path(__file__).resolve().parents[2]
    cfg_path = root / "configs" / "default.yaml"
    enabled_env = os.environ.get("AIOS_REAL_EXECUTION_ENABLED", "").lower()
    if enabled_env in {"1", "true", "yes"}:
        return {"enabled": True, "subject": "runtime", "allowed_cwd": str(root)}
    if not cfg_path.exists():
        return {"enabled": False}
    try:
        with open(cfg_path, "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
        re_cfg = data.get("real_execution", {}) or {}
        re_cfg.setdefault("enabled", False)
        re_cfg.setdefault("subject", "runtime")
        re_cfg.setdefault("scopes", ["process.execute", "tool:invoke", "filesystem.write"])
        if re_cfg.get("allowed_cwd") is None:
            re_cfg["allowed_cwd"] = str(root)
        return re_cfg
    except Exception:
        return {"enabled": False}


# NOTE: `record_execution_evidence` lives in `aios.governance.evidence.store`
# (governance layer) to avoid a runtime -> governance import (ARCH layering).
# The CLI `execute` command imports it from there.
