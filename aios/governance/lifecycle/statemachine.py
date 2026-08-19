"""Task State Machine — Rule 6 (full lifecycle before DONE)."""
import os

STATES = [
    "PLANNED", "SPECIFIED", "CRITIQUED_1", "CRITIQUED_2", "BROKEN_DOWN",
    "REVIEWED", "IMPLEMENTING", "TESTING", "EVALUATING", "REGRESSION",
    "READY_TO_CLOSE", "DONE",
]

TRANSITIONS = {
    "PLANNED": ["SPECIFIED"],
    "SPECIFIED": ["CRITIQUED_1"],
    "CRITIQUED_1": ["CRITIQUED_2"],
    "CRITIQUED_2": ["BROKEN_DOWN"],
    "BROKEN_DOWN": ["REVIEWED"],
    "REVIEWED": ["IMPLEMENTING"],
    "IMPLEMENTING": ["TESTING"],
    "TESTING": ["EVALUATING"],
    "EVALUATING": ["REGRESSION"],
    "REGRESSION": ["READY_TO_CLOSE"],
    "READY_TO_CLOSE": ["DONE"],
}

# Artifacts that MUST exist before DONE (mirrors Task Folder Standard + governance extensions)
REQUIRED_FOR_DONE = [
    "spec.md", "critique-1.md", "critique-2.md", "tasks.md", "review.md",
    "implementation", "test.md", "evaluation.md", "EVIDENCE.md",
    "REGRESSION.md", "STATUS.md",
]


class LifecycleError(Exception):
    pass


class TaskStateMachine:
    def __init__(self, state="PLANNED"):
        if state not in STATES:
            raise LifecycleError(f"unknown state {state!r}")
        self.state = state

    def can_transition(self, target):
        return target in TRANSITIONS.get(self.state, [])

    def transition(self, target):
        if not self.can_transition(target):
            raise LifecycleError(f"illegal transition {self.state} -> {target}")
        self.state = target
        return self.state

    @staticmethod
    def artifacts_present(task_folder):
        """Return (all_present: bool, missing: list)."""
        missing = []
        for art in REQUIRED_FOR_DONE:
            p = os.path.join(task_folder, art)
            if art == "implementation":
                if not (os.path.isdir(p) and os.listdir(p)):
                    missing.append(art)
            elif not (os.path.exists(p) and os.path.getsize(p) > 0):
                missing.append(art)
        return (len(missing) == 0, missing)
