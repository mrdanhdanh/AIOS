"""Actionable error messages for AIOS Developer Experience (TASK-071).

Errors raised through this module always carry a *cause* (why it happened)
and a *fix hint* (how to resolve it) instead of a bare stack trace. This is
the DX contract for T071: "Error message phải actionable (không chỉ stack
trace)."
"""

from __future__ import annotations

from typing import Any, Optional


class ActionableError(Exception):
    """An error that explains its cause and how to fix it.

    The string form is structured so tooling and humans can parse the
    cause/fix without reading a traceback::

        <message> | cause: <cause> | fix: <fix_hint>
    """

    def __init__(
        self,
        message: str,
        *,
        cause: str,
        fix_hint: str,
        context: Optional[dict] = None,
    ) -> None:
        self.cause = cause
        self.fix_hint = fix_hint
        self.context = context or {}
        super().__init__(message)

    def __str__(self) -> str:  # noqa: D105
        base = super().__str__()
        return f"{base} | cause: {self.cause} | fix: {self.fix_hint}"

    def to_dict(self) -> dict[str, Any]:
        """Machine-readable representation for CLI/JSON output."""
        return {
            "error": str(super().__str__()),
            "cause": self.cause,
            "fix_hint": self.fix_hint,
            "context": self.context,
        }


def wrap_error(
    exc: BaseException,
    *,
    cause: str,
    fix_hint: str,
    context: Optional[dict] = None,
) -> ActionableError:
    """Wrap any exception into an :class:`ActionableError`.

    The original exception type and message are preserved in the wrapped
    message so no information is lost — only *cause* and *fix_hint* are added.
    """
    original = f"{type(exc).__name__}: {exc}" if str(exc) else type(exc).__name__
    return ActionableError(
        original,
        cause=cause,
        fix_hint=fix_hint,
        context=context,
    )


class CliStabilityError(ActionableError):
    """Raised when a CLI breaking change is not accompanied by a version bump
    and a deprecation window (T071 DX safety rule)."""


class CliVersionBumpRequired(CliStabilityError):
    """A breaking CLI change was detected without a corresponding version bump."""


def format_actionable(error: BaseException) -> str:
    """Render an error for CLI output.

    If the error is :class:`ActionableError` the cause and fix hint are shown;
    otherwise a generic actionable wrapper is produced so the user always gets
    a next step instead of a bare traceback.
    """
    if isinstance(error, ActionableError):
        return str(error)
    wrapped = wrap_error(
        error,
        cause="An unexpected error occurred while running the command.",
        fix_hint="Re-run with --verbose or check the command arguments and try again.",
    )
    return str(wrapped)


def explain(error: BaseException) -> dict[str, object]:
    """Return a structured explanation for an error (machine + human friendly)."""
    if isinstance(error, ActionableError):
        return error.to_dict()
    return wrap_error(
        error,
        cause="An unexpected error occurred.",
        fix_hint="Check the command arguments and try again.",
    ).to_dict()
