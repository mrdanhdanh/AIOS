"""Task lifecycle state machine (Rule 6)."""

from __future__ import annotations

from typing import Dict, Iterable, List, Set

# Ordered lifecycle states (Rule 6). PLANNED is the initial state.
LIFECYCLE_ORDER: List[str] = [
    "PLANNED",
    "SPECIFIED",
    "CRITIQUED_1",
    "CRITIQUED_2",
    "BROKEN_DOWN",
    "REVIEWED",
    "IMPLEMENTING",
    "TESTING",
    "EVALUATING",
    "REGRESSION",
    "READY_TO_CLOSE",
    "DONE",
]

# Mandatory artifacts required to enter each state. Missing any of these when
# transitioning (or when closing) yields REJECT.
STATE_ARTIFACTS: Dict[str, List[str]] = {
    "PLANNED": [],
    "SPECIFIED": ["spec.md"],
    "CRITIQUED_1": ["critique-1.md"],
    "CRITIQUED_2": ["critique-2.md"],
    "BROKEN_DOWN": ["tasks.md"],
    "REVIEWED": ["review.md"],
    "IMPLEMENTING": ["implementation/"],
    "TESTING": ["test.md"],
    "EVALUATING": ["evaluation.md"],
    "REGRESSION": ["regression.md"],
    "READY_TO_CLOSE": [],
    "DONE": [],
}

# Convenience: the union of every artifact a fully-closed task must have.
REQUIRED_FOR_DONE: Set[str] = set()
for _s, _a in STATE_ARTIFACTS.items():
    REQUIRED_FOR_DONE.update(_a)


class LifecycleError(Exception):
    """Raised on an invalid transition or a missing mandatory artifact."""


class TaskLifecycle:
    """Per-task lifecycle state machine."""

    def __init__(self) -> None:
        self._states: Dict[str, str] = {}

    # ------------------------------------------------------------------ #
    def init(self, task_id: str, state: str = "PLANNED") -> str:
        if state not in LIFECYCLE_ORDER:
            raise LifecycleError(f"Unknown lifecycle state '{state}'.")
        self._states[task_id] = state
        return state

    def current(self, task_id: str) -> str:
        if task_id not in self._states:
            raise LifecycleError(f"Task '{task_id}' has no lifecycle state.")
        return self._states[task_id]

    # ------------------------------------------------------------------ #
    def required_artifacts(self, state: str) -> List[str]:
        return list(STATE_ARTIFACTS.get(state, []))

    def can_transition(self, task_id: str, to_state: str) -> bool:
        try:
            self._validate_transition(task_id, to_state)
            return True
        except LifecycleError:
            return False

    def _validate_transition(self, task_id: str, to_state: str) -> None:
        if to_state not in LIFECYCLE_ORDER:
            raise LifecycleError(f"Unknown lifecycle state '{to_state}'.")
        current = self._states.get(task_id)
        if current is None:
            raise LifecycleError(f"Task '{task_id}' is not initialized.")
        if current == to_state:
            return
        if LIFECYCLE_ORDER.index(to_state) < LIFECYCLE_ORDER.index(current):
            raise LifecycleError(
                f"Cannot move backwards from '{current}' to '{to_state}'."
            )

    def transition(
        self, task_id: str, to_state: str, provided_artifacts: Iterable[str] = ()
    ) -> str:
        """Transition ``task_id`` to ``to_state``.

        The transition is rejected (LifecycleError) when:
          * the ordering is invalid, or
          * any of the state's mandatory artifacts are missing from
            ``provided_artifacts``.
        """
        self._validate_transition(task_id, to_state)
        required = STATE_ARTIFACTS.get(to_state, [])
        provided = set(provided_artifacts)
        missing = [a for a in required if a not in provided]
        if missing:
            raise LifecycleError(
                f"Cannot transition to '{to_state}': missing mandatory "
                f"artifacts {missing}."
            )
        self._states[task_id] = to_state
        return to_state

    # ------------------------------------------------------------------ #
    def missing_for_done(self, provided_artifacts: Iterable[str]) -> List[str]:
        """Return mandatory artifacts still missing for DONE."""
        provided = set(provided_artifacts)
        return [a for a in sorted(REQUIRED_FOR_DONE) if a not in provided]

    def can_close(self, task_id: str, provided_artifacts: Iterable[str] = ()) -> bool:
        """A task may close only when every mandatory artifact is present."""
        if self.current(task_id) != "READY_TO_CLOSE":
            return False
        return len(self.missing_for_done(provided_artifacts)) == 0

    def close(self, task_id: str, provided_artifacts: Iterable[str] = ()) -> str:
        """Attempt to reach DONE. Rejects when artifacts are missing."""
        if not self.can_close(task_id, provided_artifacts):
            missing = self.missing_for_done(provided_artifacts)
            raise LifecycleError(
                f"Cannot close '{task_id}': missing mandatory artifacts {missing}."
            )
        self._states[task_id] = "DONE"
        return "DONE"
